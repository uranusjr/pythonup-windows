import os
import pathlib
import warnings

import click

from .. import __version__
from .. import metadata, releases, termui, utils


def install_self_upgrade(path):
    click.echo('Installing upgrade from {}'.format(path))
    click.echo('PythonUp will terminate now to let the installer run.')
    click.echo('Come back after the installation finishes. See ya later!')

    # Launch detached installer and exit, releasing files for writes.
    os.startfile(path)
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
