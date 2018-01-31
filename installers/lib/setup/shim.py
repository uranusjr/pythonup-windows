import pathlib

import click


@click.command()
@click.argument('base', type=click.Path(exists=True, file_okay=False))
def main(base):
    instdir = pathlib.Path(base)
    shim = instdir.joinpath('cmd', 'pythonup.exe')
    print('Writing {}'.format(shim))
    data = instdir.joinpath('lib', 'shims', 'shim.exe').read_bytes()
    cmd = '\0'.join([
        str(instdir.joinpath('lib', 'python', 'python.exe')), '-m', 'pythonup',
    ])
    data += bytes(reversed((cmd + '\n\n').encode('utf-8')))
    with shim.open('wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
