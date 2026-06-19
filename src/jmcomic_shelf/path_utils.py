import os


def path_for_open(path: str) -> str:
    if not path or os.name != 'nt':
        return path
    normalized = os.path.abspath(os.path.normpath(path))
    if normalized.startswith('\\\\?\\'):
        return normalized
    if normalized.startswith('\\\\'):
        return '\\\\?\\UNC\\' + normalized[2:]
    return '\\\\?\\' + normalized


def path_exists(path: str) -> bool:
    return bool(path) and os.path.exists(path_for_open(path))


def display_path(path: str) -> str:
    if not path:
        return path
    if path.startswith('\\\\?\\UNC\\'):
        return '\\\\' + path[8:]
    if path.startswith('\\\\?\\'):
        return path[4:]
    return path


def walk_paths(path: str):
    for root, dirs, files in os.walk(path_for_open(path)):
        yield display_path(root), dirs, files
