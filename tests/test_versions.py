import json
import pathlib
import re

import pytest

import pythonup.versions


version_paths = list(pythonup.versions.VERSIONS_DIR_PATH.iterdir())
version_names = [p.stem for p in version_paths]


@pytest.mark.parametrize('path', version_paths, ids=version_names)
def test_version_definitions(path):
    assert path.suffix == '.json', '{} has wrong extension'.format(path)
    assert pythonup.versions.VERSION_NAME_RE.match(path.stem), \
        '{} has invalid name'.format(path)

    with path.open() as f:
        data = json.load(f)

    schema = data.pop('type')
    possible_types = pythonup.versions.InstallerType.__members__
    assert schema in possible_types

    assert isinstance(data.pop('version_info'), list)

    if schema == 'cpython_msi':
        for key in ('x86', 'amd64'):
            d = data.pop(key)
            assert d.pop('url')
            assert re.match(r'^[a-f\d]{32}$', d.pop('md5_sum'))
    elif schema == 'cpython':
        assert data.pop('url')
        assert re.match(r'^[a-f\d]{32}$', data.pop('md5_sum'))

    assert not data, 'superfulous keys: {}'.format(', '.join(data.keys()))


def test_get_version_cpython_msi():
    version = pythonup.versions.get_version('3.4', force_32=False)
    assert version == pythonup.versions.CPythonMSIVersion(
        name='3.4',
        url='https://www.python.org/ftp/python/3.4.4/python-3.4.4.amd64.msi',
        md5_sum='963f67116935447fad73e09cc561c713',
        version_info=(3, 4, 4),
    )


def test_get_version_cpython_msi_switch():
    version = pythonup.versions.get_version('3.4', force_32=True)
    assert version == pythonup.versions.CPythonMSIVersion(
        name='3.4',
        url='https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi',
        md5_sum='e96268f7042d2a3d14f7e23b2535738b',
        version_info=(3, 4, 4),
    )


def test_get_version_cpython():
    version = pythonup.versions.get_version('3.5', force_32=False)
    assert version == pythonup.versions.CPythonVersion(
        name='3.5',
        url='https://www.python.org/ftp/python/3.5.4/python-3.5.4-amd64.exe',
        md5_sum='4276742a4a75a8d07260f13fe956eec4',
        version_info=(3, 5, 4),
    )


def test_get_version_cpython_switch():
    version = pythonup.versions.get_version('3.5', force_32=True)
    assert version == pythonup.versions.CPythonVersion(
        name='3.5-32',
        url='https://www.python.org/ftp/python/3.5.4/python-3.5.4.exe',
        md5_sum='9693575358f41f452d03fd33714f223f',
        version_info=(3, 5, 4),
        forced_32=True,
    )


def test_get_version_not_found():
    with pytest.raises(pythonup.versions.VersionNotFoundError) as ctx:
        pythonup.versions.get_version('2.8', force_32=False)
    assert str(ctx.value) == '2.8'


@pytest.mark.parametrize('name, force_32, result', [
    ('3.6', False, 'Python 3.6'),
    ('3.6', True, 'Python 3.6-32'),
    ('3.4', False, 'Python 3.4'),
    ('3.4', True, 'Python 3.4'),
])
def test_str(name, force_32, result):
    version = pythonup.versions.get_version(name, force_32=force_32)
    assert str(version) == result


@pytest.mark.parametrize('name, force_32, cmd', [
    ('3.6', False, 'python3.exe'),
    ('3.6', True, 'python3.exe'),
    ('2.7', False, 'python2.exe'),
    ('2.7', True, 'python2.exe'),
])
def test_python_major_command(mocker, name, force_32, cmd):
    mocker.patch.object(pythonup.versions, 'configs', **{
        'get_scripts_dir_path.return_value': pathlib.Path(),
    })
    version = pythonup.versions.get_version(name, force_32=force_32)
    assert version.python_major_command == pathlib.Path(cmd)


@pytest.mark.parametrize('name, force_32, result', [
    ('3.6', False, '3.6'),
    ('3.6', True, '3.6'),
    ('3.4', False, '3.4'),
    ('3.4', True, '3.4'),
])
def test_arch_free_name(name, force_32, result):
    version = pythonup.versions.get_version(name, force_32=force_32)
    assert version.arch_free_name == result


@pytest.mark.parametrize('name, force_32, result', [
    ('3.6', False, {'3.6'}),
    ('3.6', True, {'3.6', '3.6-32'}),
    ('3.6-32', False, {'3.6-32'}),
    ('3.4', False, {'3.4'}),
    ('3.4', True, {'3.4'}),
])
def test_script_version_names(name, force_32, result):
    version = pythonup.versions.get_version(name, force_32=force_32)
    assert version.script_version_names == result


def test_is_installed(tmpdir, mocker):
    mock_metadata = mocker.patch.object(pythonup.versions, 'metadata', **{
        'get_install_path.return_value': pathlib.Path(str(tmpdir)),
    })
    version = pythonup.versions.get_version('3.6', force_32=False)
    assert version.is_installed()
    mock_metadata.get_install_path.assert_called_once_with('3.6')
