.. _install:

==============
Install Python
==============

PythonUp installs a Python version with a single command. To install
``<version>`` on you machine: [#]_

::

    pythonup install <version>

.. [#] Use ``pythonup list --all`` to find out what versions are available. See
    :ref:`list` for more information about the ``list`` command.

This automatically downloads the installer, and runs it with minimal user input
possible. [#]_ If there’s need to install without Internet connection, you can
download the installer yourself, and run::

    pythonup install --file=path\to\installer.exe <version>

to install directly from that installer. Either way, PythonUp sets up the
Python installation on its own, and let you start using it right away.

.. [#] Generally only to confirm the UAC dialog, if needed.

PythonUp provides some extra executables for you. Say you have install Python
3.6 after you set up PythonUp. Now you can launch Python with::

    python3

Install a package, say, Pipenv_, with::

    pip3 install pipenv

.. _Pipenv: https://docs.pipenv.org

and have the ``pipenv`` command available immediately after.

Upgrade Python
==============

PythonUp allows you to upgrade a Python installation to a newer micro version,
e.g. 3.6.3 to 3.6.4. Run the following command to upgrade an installed version
(if available)::

    pythonup upgrade <version>

It takes some time for the developers to update the definition to a newer
version. If you find a newer version released on `python.org`_ that is not
available in PythonUp, :ref:`send a pull request <develop>` to update the
definition files!

.. _`python.org`: https://python.org

Uninstall Python
================

You probably guessed it::

    pythonup uninstall <version>

Similar to installing, this does nothing too fancy, but just runs the
standard uninstaller. It does perform some additional cleanup if you are using
the version. See :ref:`manage` about how you can manage/use versions.
