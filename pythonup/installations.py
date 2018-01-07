import ast
import contextlib
import itertools
import os
import pathlib
import re
import subprocess

import attr


@attr.s
class Installation:

    path = attr.ib(convert=pathlib.Path)

    @property
    def python(self):
        return self.path.joinpath('python.exe')

    @property
    def scripts_dir(self):
        return self.path.joinpath('Scripts')

    @property
    def pip(self):
        return self.scripts_dir.joinpath('pip.exe')

    def get_version_info(self):
        output = subprocess.check_output(
            [str(self.python), '--version'], encoding='ascii',
        ).strip()
        match = re.match(r'^Python (\d+)\.(\d+)\.(\d+)$', output)
        return tuple(int(x) for x in match.groups())

    def is_32bit(self):
        """Ask the interpreter about its bitness.

        The return value should match :ref:`.metadata.is_python_32bit()`.
        """
        return bool(ast.eval_literal(subprocess.check_output([
            self.python, '-c', '"import sys; print(sys.maxsize <= 2 ** 32)"',
        ]).strip()))

    def find_script(self, name):
        names = itertools.chain([name], [
            '{}{}'.format(name, ext)
            for ext in os.environ['PATHEXT'].split(';')
        ])
        for name in names:
            with contextlib.suppress(FileNotFoundError):
                return self.scripts_dir.joinpath(name).resolve(strict=True)
        raise FileNotFoundError(name)
