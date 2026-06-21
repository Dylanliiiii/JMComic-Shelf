import os
import re
import shutil
from dataclasses import dataclass, field
from typing import Iterable

from .models import AlbumRecord


@dataclass
class DeleteResult:
    deleted_count: int = 0
    deleted_paths: list[str] = field(default_factory=list)
    skipped_paths: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def delete_album_files(records: Iterable[AlbumRecord], download_dir: str) -> DeleteResult:
    result = DeleteResult()
    if not download_dir:
        return result

    root = os.path.abspath(download_dir)
    for record in records:
        for path in _candidate_paths(record):
            normalized = os.path.abspath(path)
            if os.path.isdir(normalized) and not _is_album_dir_for_record(record, normalized):
                result.skipped_paths.append(path)
                continue
            if not _is_inside(root, normalized):
                result.skipped_paths.append(path)
                continue
            if not os.path.exists(normalized):
                continue
            try:
                if os.path.isdir(normalized):
                    shutil.rmtree(normalized)
                else:
                    os.remove(normalized)
                result.deleted_paths.append(normalized)
                result.deleted_count += 1
            except Exception as e:
                result.errors.append(f'{path}: {e}')
    return result


def _candidate_paths(record: AlbumRecord) -> list[str]:
    paths = []
    if record.album_dir:
        paths.append(record.album_dir)
    if record.pdf_path and record.pdf_path not in paths:
        paths.append(record.pdf_path)
    return paths


def _is_album_dir_for_record(record: AlbumRecord, path: str) -> bool:
    basename = os.path.basename(os.path.normpath(path))
    return re.match(rf'^JM{re.escape(str(record.jm_id))}-.+', basename, re.IGNORECASE) is not None


def _is_inside(root: str, path: str) -> bool:
    try:
        return path != root and os.path.commonpath([root, path]) == root
    except ValueError:
        return False
