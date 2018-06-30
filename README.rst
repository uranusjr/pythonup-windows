=================================================
PythonUp — The Python Runtime Manager (Windows)
=================================================

.. image:: https://ci.appveyor.com/api/projects/status/7fdfpbvu2roawg23/branch/master?svg=true
    :target: https://ci.appveyor.com/project/uranusjr/pythonup-windows
    :alt: Build status

.. image:: https://readthedocs.org/projects/pythonup-windows/badge/?version=latest
    :target: https://pythonup-windows.readthedocs.io/en/latest/
    :alt: Documentation Status

PythonUp helps your download, configure, install, and manage Python runtimes.
It also provides utilities that can be integrated into your Python-related
development workflows. This is the Windows version.

.. highlights::

    macOS or Linux user? Check out `PythonUp for POSIX`_.

.. _`PythonUp for POSIX`: https://github.com/uranusjr/pythonup-posix


Distribution
============

PythonUp for Windows is officially distributed on GitHub. Download installers
from `Releases <https://github.com/uranusjr/pythonup-windows/releases>`_ and
run it. After installation, a ``pythonup`` command will be available in
newly-opened command prompts.


Quick Start
===========

Install Python 3.6::

    $ pythonup install 3.6

Run Python::

    $ python3

Install Pipenv to Python 3.6::

    $ pip3.6 install pipenv

And use it immediately::

    $ pipenv --version
    pipenv, version 9.0.1

Install Python 3.5 (32-bit)::

    $ pythonup install 3.5-32

Switch to a specific version::

    $ pythonup use 3.5-32
    $ python3 --version
    Python 3.5.4

Switch back to 3.6::

    $ pythonup use 3.6
    $ python3 --version
    Python 3.6.4
    $ python3.5 --version
    Python 3.5.4

Uninstall Python::

    $ pythonup uninstall 3.5-32

Use ``--help`` to find more::

    $ pythonup --help
    $ pythonup install --help

Or read the `Documentation <https://pythonup-windows.readthedocs.io>`_.

Now you’re ready to use CPython on Windows like a first-class citizen, and
ignore people telling you to get a Mac.

🤔😉😆
