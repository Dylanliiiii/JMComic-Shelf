import os
import re
from pathlib import Path
from typing import Iterable
from zipfile import ZIP_DEFLATED, ZipFile

from PySide6.QtCore import QUrl

from .models import AlbumRecord


INVALID_ARCHIVE_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def existing_pdf_paths(records: Iterable[AlbumRecord]) -> tuple[list[str], list[str]]:
    paths: list[str] = []
    missing: list[str] = []
    for record in records:
        path = str(record.pdf_path or '')
        if path and os.path.isfile(path):
            paths.append(path)
        else:
            missing.append(str(record.jm_id))
    return paths, missing


def file_urls(records: Iterable[AlbumRecord]) -> tuple[list[QUrl], list[str]]:
    paths, missing = existing_pdf_paths(records)
    return [QUrl.fromLocalFile(path) for path in paths], missing


def safe_archive_name(record: AlbumRecord, used_names: set[str] | None = None) -> str:
    used_names = used_names if used_names is not None else set()
    title = INVALID_ARCHIVE_CHARS.sub('_', str(record.title or '未命名')).strip(' .') or '未命名'
    base = f'JM{record.jm_id}-{title}.pdf'
    candidate = base
    index = 2
    while candidate.casefold() in {name.casefold() for name in used_names}:
        candidate = f'JM{record.jm_id}-{title} ({index}).pdf'
        index += 1
    used_names.add(candidate)
    return candidate


def create_pdf_archive(records: Iterable[AlbumRecord], output_path: str) -> tuple[int, list[str]]:
    records = list(records)
    _, missing = existing_pdf_paths(records)
    count = 0
    used_names: set[str] = set()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, 'w', compression=ZIP_DEFLATED) as archive:
        for record in records:
            path = str(record.pdf_path or '')
            if not path or not os.path.isfile(path):
                continue
            archive.write(path, arcname=safe_archive_name(record, used_names))
            count += 1
    return count, missing
