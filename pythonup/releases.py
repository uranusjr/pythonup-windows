import os
import re
import urllib.parse
import warnings

import attr
import packaging.version
import requests


GITHUB_API_TOKEN_KEY = 'PYTHONUP_GITHUB_API_TOKEN'


def get_request_headers():
    token = os.environ.get(GITHUB_API_TOKEN_KEY)
    if not token:
        warnings.warn('{} environment variable not set.'.format(
            GITHUB_API_TOKEN_KEY,
        ))
        return None
    return {'Authorazation': 'token {}'.format(token)}


def get(endpoint):
    url = urllib.parse.urljoin('https://api.github.com', endpoint)
    headers = get_request_headers()
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp


class Parsable:
    @classmethod
    def parse(cls, data):
        extras = {}
        attr_names = set(a.name for a in attr.fields(cls))
        for k, v in tuple(data.items()):
            if k not in attr_names:
                extras[k] = data.pop(k)
        instance = cls(**data)
        for k, v in extras.items():
            setattr(instance, k, v)
        return instance


@attr.s
class ReleaseAsset(Parsable):

    browser_download_url = attr.ib(converter=str)
    size = attr.ib(converter=int)

    def check_download(self, data):
        assert len(data) == self.size, \
            'expect {} bytes, got {}'.format(self.size, len(data))


def parse_asset_list(data_list):
    return [ReleaseAsset.parse(data) for data in data_list]


ASSET_NAME_RE = re.compile(r'''
    ^pythonup\-setup
    \-
    (?P<arch>\w+)   # amd64 or win32
    \-.+            # version
    \.exe$
''', re.VERBOSE)


@attr.s
class Release(Parsable):

    name = attr.ib(converter=str)
    draft = attr.ib(converter=bool)
    prerelease = attr.ib(converter=bool)
    tag_name = attr.ib(converter=str)
    assets = attr.ib(converter=parse_asset_list)

    def __str__(self):
        return self.name

    def get_asset(self, arch):
        for asset in self.assets:
            match = ASSET_NAME_RE.match(asset.name)
            if match and match.group('arch') == arch:
                return asset
        return None


class ReleaseUpToDate(ValueError):
    def __init__(self, current):
        super().__init__('{} is up to date'.format(current))
        self.version = current


def get_releases():
    response = get('/repos/uranusjr/pythonup-windows/releases')
    return [Release.parse(data) for data in response.json()]


def get_new_release(current, *, includes_pre):
    current = packaging.version.parse(current)
    for release in get_releases():
        if release.draft or (release.prerelease and not includes_pre):
            continue
        version = packaging.version.parse(release.tag_name)
        if version > current:
            return release
    raise ReleaseUpToDate(current)
