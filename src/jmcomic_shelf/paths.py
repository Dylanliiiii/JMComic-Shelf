import os
import sys
from pathlib import Path


APP_NAME = 'JMComic Shelf'
APP_ICON_NAME = 'icon.png'


def get_default_app_data_dir() -> str:
    base = os.environ.get('APPDATA') or os.path.expanduser('~')
    return os.path.join(base, APP_NAME)


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def get_settings_path(app_data_dir: str = '') -> str:
    return os.path.join(app_data_dir or get_default_app_data_dir(), 'settings.json')


def get_database_path(app_data_dir: str = '') -> str:
    return os.path.join(app_data_dir or get_default_app_data_dir(), 'shelf.db')


def get_cover_cache_dir(app_data_dir: str = '') -> str:
    return os.path.join(app_data_dir or get_default_app_data_dir(), 'covers')


def get_project_root() -> Path:
    bundle_root = getattr(sys, '_MEIPASS', None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parents[2]


def get_app_icon_path() -> str:
    candidates = [
        get_project_root() / 'assets' / APP_ICON_NAME,
        Path.cwd() / 'assets' / APP_ICON_NAME,
        Path(__file__).resolve().parent / 'assets' / APP_ICON_NAME,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(candidates[0])
