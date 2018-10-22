"""Update entry in pythonup/versions. Only works with new styles installers.
"""

import argparse
import contextlib
import operator
import json
import os
import pathlib
import re
import sys
import urllib.parse

import requests


def _get_version(s):
    match = re.match(r'^(\d+)\.(\d+)$', s)
    if not match:
        raise argparse.ArgumentTypeError('should be an X.Y version number')
    x_y = tuple(map(int, match.groups()))
    if x_y < (3, 5):
        raise argparse.ArgumentTypeError('only 3.5+ is supported')
    return x_y


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'version', type=_get_version, help="Name of version, in X.Y",
    )
    return parser


def parse_arguments(argv=None):
    parser = get_parser()
    return parser.parse_args(argv)


def _get_page(url, params):
    headers = {'Accept': 'application/json'}
    response = requests.get(url, params=params, headers=headers)
    try:
        response.raise_for_status()
    except Exception:
        print('ERROR:', response.text)
        raise
    return response.json()


class CollectionIterator:
    """Iterator for Collection.
    """
    def __init__(self, url, params):
        self._params = params
        self._set_page(url)

    def __repr__(self):
        return 'CollectionIterator(url={!r})'.format(self._url)

    def __iter__(self):
        return self

    def __next__(self):
        with contextlib.suppress(StopIteration):
            return next(self._iter)
        path = self._meta['next']
        if not path:
            raise StopIteration
        self._set_page(urllib.parse.urljoin(self._url, path))
        return next(self._iter)

    def _set_page(self, url):
        self._url = url
        page = _get_page(url, self._params)
        self._meta = page['meta']
        self._iter = iter(page['objects'])


class Collection:
    """A collection returned by Tastypie's list view.
    """
    def __init__(self, url, params=None):
        self._url = url
        self._params = params

    def __repr__(self):
        return 'Collection(url={!r})'.format(self._url)

    def __iter__(self):
        return CollectionIterator(self._url, self._params)


def _get_endpoint(*parts):
    return 'https://www.python.org/api/v1/{}/'.format('/'.join(parts))


def iter_releases(version):
    url = _get_endpoint('downloads', 'release')
    params = {
        'is_published': True,
        'pre_release': False,
    }
    name_prefix = 'Python {}.{}.'.format(version[0], version[1])
    for dataset in Collection(url, params):
        if not dataset['name'].startswith(name_prefix):
            continue
        yield dataset


def parse_release_id(dataset):
    return int(dataset['resource_uri'].rsplit('/', 2)[-2])


def iter_installer_files(release):
    url = _get_endpoint('downloads', 'release_file')
    params = {'release': release['id']}
    for dataset in Collection(url, params):
        if dataset['name'].lower().endswith(' executable installer'):
            yield dataset


def get_latest_release(version):
    datasets = list(iter_releases(version))
    for dataset in datasets:
        dataset['id'] = parse_release_id(dataset)
    datasets = sorted(datasets, key=operator.itemgetter('id'), reverse=True)

    for dataset in datasets:
        print('Checking {} ...'.format(dataset['name']), end=' ')
        installer_files = list(iter_installer_files(dataset))
        if not installer_files:
            print('No installers')
            continue
        print('OK')
        return (dataset, installer_files)

    print('No available versions')
    return None


def parse_version_info(name):
    match = re.match(r'^Python (\d+)\.(\d+)\.(\d+)$', name)
    if not match:
        raise ValueError('cannot parse version from {}'.format(name))
    return list(map(int, match.groups()))


VERSIONS_DIR = pathlib.Path(os.path.abspath(__file__)).parent.parent.joinpath(
    'pythonup', 'versions',
)


def detect_newline(f):
    newline = f.newlines
    if isinstance(newline, str):
        return newline
    return '\n'


def write_version_file(suffix, version_info, dataset):
    filename = '{0[0]}.{0[1]}{1}.json'.format(version_info, suffix)
    path = VERSIONS_DIR.joinpath(filename)
    data = {
        'type': 'cpython',
        'version_info': version_info,
        'url': dataset['url'],
        'md5_sum': dataset['md5_sum'],
    }
    if path.exists():
        with path.open() as f:
            try:
                curr = json.load(f)
            except ValueError:
                curr = {}
            if curr == data:
                print('Spec {} is up-to-date'.format(filename))
                return
            newline = detect_newline(f)
    else:
        newline = '\n'
    with path.open('w', newline=newline) as f:
        json.dump(data, f, indent='\t')
        f.write('\n')   # Trailing newline.
    print('Spec {} written'.format(filename))


def write_version_files(release, files):
    version_info = parse_version_info(release['name'])
    for dataset in files:
        if ' x86-64 ' in dataset['name']:
            write_version_file('', version_info, dataset)
        elif ' x86 ' in dataset['name']:
            write_version_file('-32', version_info, dataset)
        else:
            print('Unrecognized file {}'.format(dataset['name']))


def main():
    options = parse_arguments()
    try:
        release, files = get_latest_release(options.version)
    except TypeError:
        sys.exit(1)
    write_version_files(release, files)


if __name__ == '__main__':
    main()
