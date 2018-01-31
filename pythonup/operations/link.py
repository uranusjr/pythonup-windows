import collections
import enum
import filecmp
import itertools
import shutil
import sys

import click

from .. import configs, metadata

from .common import (
    check_installation, get_active_names, get_version, version_command,
)


class Overwrite(enum.Enum):

    yes = 'yes'
    no = 'no'
    smart = 'smart'

    def should(self, source, target):
        return (
            self == self.yes or (
                self == self.smart and
                not filecmp.cmp(str(source), str(target))
            )
        )


def publish_file(source, target, *, overwrite, quiet):
    if target.exists():
        if not overwrite.should(source, target):
            return False
    if not quiet:
        click.echo('  {}'.format(target.name))
    try:
        shutil.copy2(str(source), str(target))
    except OSError as e:
        click.echo('WARNING: Failed to copy {}.\n{}: {}'.format(
            source.name, type(e).__name__, e,
        ), err=True)
        return False
    return True


def publish_shim(source, target, *, relink, overwrite, quiet):
    """Write a shim.

    A shim is an pre-compiled executable, with extra data appended to the end
    of it. The extra data contain what command(s) the shim should attempt to
    execute when launched. Arguments are seperated by NULL characters, and
    commands (if there are multiple) are seperated by line feeds. Two extra
    line feeds signify the end of the command sequence.

    The extra data are encoded with UTF-8, and written *backwards* into the
    executable. This makes it easier to read data out.
    """
    success = publish_file(
        configs.get_shim_path(), target,
        overwrite=overwrite, quiet=quiet,
    )
    if not success:
        return False

    cmds = [[str(source.resolve(strict=True))]]
    if relink:
        cmds.append([
            sys.executable, '-m', 'pythonup',
            'link', '--all', '--overwrite=smart',
        ])
    data = bytes(reversed(
        ('\n'.join('\0'.join(args) for args in cmds) + '\n\n').encode('utf-8')
    ))
    with target.open('ab') as f:
        f.write(data)

    return True


def safe_unlink(p):
    if not p.exists():
        return
    try:
        p.unlink()
    except OSError as e:
        click.echo('Failed to remove {} ({})'.format(p, e), err=True)


def collect_version_scripts(versions):
    names = set()
    scripts = []
    shims = []
    for version in versions:
        version_scripts_dir = version.get_installation().scripts_dir
        if not version_scripts_dir.is_dir():
            continue
        for path in version_scripts_dir.iterdir():
            blacklisted_stems = {
                # Encourage people to always use qualified commands.
                'easy_install', 'pip',
                # Fully qualified pip is already populated on installation.
                'pip{}'.format(version.arch_free_name),
            }
            shimmed_stems = {
                # Major version names, e.g. "pip3".
                'pip{}'.format(version.version_info[0]),
                # Fully-qualified easy_install.
                'easy_install-{}'.format(version.arch_free_name),
            }
            if path.name in names or path.stem in blacklisted_stems:
                continue
            names.add(path.name)
            if path.stem in shimmed_stems:
                shims.append(path)
            else:
                scripts.append(path)
    return scripts, shims


def activate(versions, *, overwrite=Overwrite.yes,
             allow_empty=False, quiet=False):
    if not allow_empty and not versions:
        click.echo('No active versions.', err=True)
        click.get_current_context().exit(1)

    source_scripts, shimmed_scripts = collect_version_scripts(versions)
    scripts_dir = configs.get_scripts_dir_path()

    using_scripts = set()

    # TODO: Distinguish between `use` and automatic hook after shimmed pip
    # execution. The latter should only write scripts that actually chaged, or
    # at least should only log those writes (and overwrite others silently).
    if source_scripts or shimmed_scripts or versions:
        if not quiet:
            click.echo('Publishing scripts....')
        for source in source_scripts:
            target = scripts_dir.joinpath(source.name)
            if not source.is_file():
                continue
            using_scripts.add(target)
            publish_file(source, target, overwrite=overwrite, quiet=quiet)
        for source in shimmed_scripts:
            target = scripts_dir.joinpath(source.name)
            if target in using_scripts:
                continue
            using_scripts.add(target)
            publish_shim(
                source, target, relink=True, overwrite=overwrite, quiet=quiet,
            )
        for version in versions:
            target = version.python_major_command
            if target in using_scripts:
                continue
            using_scripts.add(target)
            publish_shim(
                version.get_installation().python, target,
                relink=False, overwrite=overwrite, quiet=quiet,
            )

    metadata.set_active_python_versions(version.name for version in versions)

    stale_scripts = set(scripts_dir.iterdir()) - using_scripts
    if stale_scripts:
        if not quiet:
            click.echo('Cleaning stale scripts...')
        for script in stale_scripts:
            if not quiet:
                click.echo('  {}'.format(script.name))
            safe_unlink(script)


def link_commands(version):
    installation = version.get_installation()
    for path in version.python_commands:
        click.echo('Publishing {}'.format(path.name))
        publish_shim(
            installation.python, path,
            relink=False, overwrite=Overwrite.yes, quiet=True,
        )
    for path in version.pip_commands:
        click.echo('Publishing {}'.format(path.name))
        publish_shim(
            installation.pip, path,
            relink=True, overwrite=Overwrite.yes, quiet=True,
        )


def unlink_commands(version):
    for p in itertools.chain(version.python_commands, version.pip_commands):
        click.echo('Unlinking {}'.format(p.name))
        safe_unlink(p)


def update_active_versions(*, remove=frozenset()):
    current_active_names = set(get_active_names())
    active_names = [n for n in current_active_names]
    for version in remove:
        try:
            active_names.remove(version.name)
        except ValueError:
            continue
        click.echo('Deactivating {}'.format(version))
    if len(current_active_names) != len(active_names):
        activate([get_version(n) for n in active_names], allow_empty=True)


@version_command(plural=True)
def use(ctx, versions, add):
    if add is None and not versions:
        # Bare "use": Display active versions.
        names = get_active_names()
        if names:
            click.echo(' '.join(names))
        else:
            click.echo('Not using any versions.', err=True)
        return

    for version in versions:
        check_installation(version)

    active_versions = [
        get_version(name)
        for name in get_active_names()
    ]
    if add:
        active_names = set(v.name for v in active_versions)
        new_versions = []
        for v in versions:
            if v.name in active_names:
                click.echo('Already using {}.'.format(v), err=True)
            else:
                new_versions.append(v)
        versions = active_versions + new_versions

    # Remove duplicate inputs (keep first apperance).
    versions = list(collections.OrderedDict(
        (version.name, version) for version in versions
    ).values())

    if active_versions == versions:
        click.echo('No version changes.', err=True)
        return

    if versions:
        click.echo('Using: {}'.format(', '.join(v.name for v in versions)))
    else:
        click.echo('Not using any versions.')
    activate(versions, allow_empty=(not add))


def link(ctx, command, link_all, overwrite):
    if not link_all and not command:    # This mistake is more common.
        click.echo(ctx.get_usage(), color=ctx.color)
        click.echo('\nError: Missing argument "command".', color=ctx.color)
        ctx.exit(1)
    if link_all and command:
        click.echo('--all cannot be used with a command.', err=True)
        ctx.exit(1)

    active_names = get_active_names()
    if not active_names:
        click.echo('Not using any versions.', err=True)
        if not link_all:
            click.echo(
                'HINT: Use "pythonup use" to use a version first.', err=True,
            )
            ctx.exit(1)

    if link_all:
        activate(
            [get_version(n) for n in active_names],
            overwrite=overwrite, allow_empty=True,
        )
        return

    command_name = command  # Better variable names.
    command = None
    for version_name in active_names:
        version = get_version(version_name)
        try:
            command = version.get_installation().find_script(command_name)
        except FileNotFoundError:
            continue
        break
    if command is None:
        click.echo('Command "{}" not found. Looked in {}: {}'.format(
            command_name,
            'version' if len(active_names) == 1 else 'versions',
            ', '.join(active_names),
        ), err=True)
        ctx.exit(1)

    target_name = command.name
    target = configs.get_scripts_dir_path().joinpath(target_name)

    # This can be done in publish_file, but we provide a better error message.
    if overwrite != Overwrite.yes and target.exists():
        if filecmp.cmp(str(command), str(target)):
            return  # If the two files are identical, we're good anyway.
        click.echo('{} exists. Use --overwrite=yes to overwrite.', err=True)
        ctx.exit(1)

    ok = publish_file(command, target, overwrite=Overwrite.yes, quiet=True)
    if ok:
        click.echo('Linked {} from {}'.format(target_name, version))
