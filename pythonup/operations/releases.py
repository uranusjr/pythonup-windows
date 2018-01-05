import ctypes
import pathlib
import warnings

import click

from .. import __version__
from .. import metadata, releases, termui, utils


def install_self_upgrade(path):
    click.echo('Installing upgrade from {}'.format(path))
    click.echo('PythonUp will terminate now to let the installer run.')
    click.echo('Come back after the installation finishes. See ya later!')

    # The PythonUp installer requests elevation, so subprocess won't work, and
    # we need some Win32 API magic here. (Notice we use 'open', not 'runas';
    # the installer requests elevation on its own; we don't need to do that.)
    # Launched process is in a detached state so the command process ends here,
    # releasing files for the installer to overwrite.
    instance = ctypes.windll.shell32.ShellExecuteW(
        None, 'open', str(path), '', None, 1,
    )

    if instance < 32:   # According to MSDN this is an error.
        message = '\n'.join([
            'Failed to launcn installer (error code {}).'.format(instance),
            'Find the downloaded installer and execute yourself at:',
            '  {}'.format(path),
        ])
        click.echo(message, err=True)
        click.get_current_context().exit(1)
    else:
        click.get_current_context().exit(0)


def self_upgrade(*, installer, pre):
    if installer:
        if pre:
            click.echo('Ignoring --pre flag for upgrading self with --file')
        install_self_upgrade(pathlib.Path(installer))
        return

    with warnings.catch_warnings():
        warnings.showwarning = termui.warn
        try:
            release = releases.get_new_release(__version__, includes_pre=pre)
        except releases.ReleaseUpToDate as e:
            click.echo('Current verion {} is up to date.'.format(__version__))
            if e.version.is_prerelease and not pre:
                click.echo(
                    "You are on a pre-release. Maybe you want to check for a "
                    "pre-release update with --pre?",
                )
            return

    arch = 'win32' if metadata.is_python_32bit() else 'amd64'
    asset = release.get_asset(arch)
    if asset is None:
        click.echo('No suitable asset to download in {}'.format(release))
        return

    url = asset.browser_download_url
    path = utils.download_file(url, check=asset.check_download)
    install_self_upgrade(path)
