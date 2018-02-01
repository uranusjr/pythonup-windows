import json
import pathlib


def get_value(key):
    with pathlib.Path(__file__).with_name('installation.json').open() as f:
        data = json.load(f)
    return data[key]


def get_directory(key):
    path = pathlib.Path(__file__).parent.joinpath(get_value(key))
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve(strict=True)


def get_scripts_dir_path():
    return get_directory('scripts_dir')


def get_cmd_dir_path():
    return get_directory('cmd_dir')


def get_linkexe_script_path():
    return get_directory('utils_dir').joinpath('linkexe.vbs')


def get_shim_path():
    return get_directory('shims_dir').joinpath('shim.exe')


def get_conf_path():
    path = get_directory('base_dir').joinpath('config')
    path.touch(mode=0o644, exist_ok=True)
    return path


def safe_load(f):
    try:
        return json.load(f)
    except json.JSONDecodeError:
        return {}


def get_active_names():
    with get_conf_path().open() as f:
        data = safe_load(f)
    return data.get('using', [])


def set_active_names(names):
    with get_conf_path().open('w+') as f:
        data = safe_load(f)
        data['using'] = names
        json.dump(data, f)
