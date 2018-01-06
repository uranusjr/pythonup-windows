.. _develop:

==================================
Contribute to PythonUp for Windows
==================================

Development happens on `GitHub <https://github.com/uranusjr/pythonup-windows>`__.


Development Guide
=================

Requirements
------------

* Windows
* Python 3.6
* Pipenv_

.. _Pipenv: https://pipenv.org

Optional Dependencies
---------------------

* Rust_ if you want to build the shims. The Rust development environment needs
  to be available in your shell. PythonUp targets the stable channel.
* NSIS_ 3.x if you want to build the installer. ``makensis`` needs to be
  available in your shell.

.. _Rust: https://www.rust-lang.org/install.html
.. _NSIS: http://nsis.sourceforge.net/Download

Project Setup
-------------

Download and enter the project::

    git clone https://github.com/uranusjr/pythonup-windows.git
    cd pythonup-windows

Set up environment::

    pipenv install --dev

Run Tests
---------

Run Python tests::

    pipenv run pytest tests

Run Rust tests::

    pipenv run invoke shims.test

Unfortunately there are only very limited tests right now.

Run In-Development PythonUp
---------------------------

::

    pipenv run python -m pythonup [COMMAND] ...

This should have the same behaviour as an installed command, but within the
confine of the Pipenv-managed virtual environment.

.. warning::

    PythonUp depends a lot on the Windows Registry, so certain commands still
    has some global implications. For example, the ``uninstall`` command will
    uninstall Python from your system, and ``use`` will affect your global
    using state!


Build Installer
---------------

::

    pipenv run invoke installers.build

You can only build installers of your host’s architecture. Cross compilation
is certainly possible, but I haven’t found the need to set it up.

After the command finishes you should get an EXE in the ``installers``
directory.

Build Documentation
-------------------

::

    pipenv run invoke docs.build

Documentation is managed with Sphinx_, and hosted on `Read the Docs`_ with a
custom domain.

.. _Sphinx: http://sphinx-doc.org
.. _`Read the Docs`: https://readthedocs.org

Source Code Guideline
---------------------

Try to follow the code style. For Python code, run the linter to check for
issues before submitting::

    pipenv run flake8 .

Format of text files are managed with EditorConfig_. I recommend using one of
the editor plugins to automatically format files. If you can’t/don’t want to
do so, please at least make sure you’re using the correct format before sending
in pull requests.

.. _EditorConfig: http://editorconfig.org
