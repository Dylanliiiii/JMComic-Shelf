import os
import subprocess


def open_pdf(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    os.startfile(path)


def reveal_in_explorer(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    subprocess.run(['explorer', '/select,', os.path.normpath(path)], check=False)
