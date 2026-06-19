import os
import subprocess

from .path_utils import path_exists, path_for_open


def open_pdf(path: str) -> None:
    if not path_exists(path):
        raise FileNotFoundError(path)
    os.startfile(path_for_open(path))


def reveal_in_explorer(path: str) -> None:
    if not path_exists(path):
        raise FileNotFoundError(path)
    subprocess.run(['explorer', '/select,', os.path.normpath(path)], check=False)
