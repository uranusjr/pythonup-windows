import contextlib

import click

from pythonup.operations.link import link_commands
from pythonup.operations.versions import get_versions


@click.command()
def main():
    for version in get_versions(installed_only=True):
        with contextlib.suppress(FileNotFoundError):
            link_commands(version)


if __name__ == '__main__':
    main()
