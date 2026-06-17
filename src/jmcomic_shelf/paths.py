import os


APP_NAME = 'JMComic Shelf'


def get_default_app_data_dir() -> str:
    base = os.environ.get('APPDATA') or os.path.expanduser('~')
    return os.path.join(base, APP_NAME)


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
