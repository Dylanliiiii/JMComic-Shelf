import os


APP_NAME = 'JMComic Shelf'


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
