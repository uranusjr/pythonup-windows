import contextlib
import winreg

import click

from pythonup import metadata, versions
from pythonup.operations.common import get_active_names
from pythonup.operations.link import activate


def get_version_or_none(name):
    force_32 = not metadata.can_install_64bit()
    with contextlib.suppress(versions.VersionNotFoundError):
        return versions.get_version(name, force_32=force_32)
    return None


ACTIVE_PYTHONS_KEY = 'Software\\uranusjr\\PythonUp\\ActivePythonVersions'


def _compat_get_active_python_versions():
    """Read old config stored in registry.

    We honour this for users upgrading from old versions, and convert the
    value to the new format.
    """
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, ACTIVE_PYTHONS_KEY) as key:
        value, _ = winreg.QueryValueEx(key, '')
    return value.split(';') if value else []


@click.command()
def main():
    names = get_active_names()
    if not names:
        with contextlib.suppress(FileNotFoundError):
            names = _compat_get_active_python_versions()
    versions = [
        v for v in (get_version_or_none(name) for name in names)
        if v is not None
    ]
    with contextlib.suppress(FileNotFoundError, OSError):
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, ACTIVE_PYTHONS_KEY)
    activate(versions, allow_empty=True)


if __name__ == '__main__':
    main()
