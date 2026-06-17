from collections import OrderedDict
import os
import re
from typing import Iterable

from jmcomic.jm_plugin import CatalogPlugin

from .cover_cache import CoverCache
from .database import ShelfDatabase
from .models import AlbumRecord


ALBUM_DIR_RE = re.compile(r'^JM(?P<id>\d+)-(?P<title>.+)$', re.IGNORECASE)
PDF_RE = re.compile(r'^JM(?P<id>\d+)-(?P<title>.+)\.pdf$', re.IGNORECASE)
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}


def record_from_album(album, pdf_path: str = '', cover_path: str = '') -> AlbumRecord:
    info = CatalogPlugin.build_album_info(album)
    return AlbumRecord(
        jm_id=info['id'],
        title=info['title'],
        link=info['link'],
        pdf_path=pdf_path,
        cover_path=cover_path,
        authors=info['authors'],
        tags=info['tags'],
        chapters=info['chapters'],
    )


def group_by_author(records: Iterable[AlbumRecord]):
    grouped = OrderedDict()
    for record in records:
        for author in record.authors or ['未知作者']:
            grouped.setdefault(author, []).append(record)
    return grouped


def rebuild_index_from_download_dir(download_dir: str, db_path: str, cover_cache_dir: str = '') -> int:
    """递归扫描下载目录，把现有漫画目录/PDF 同步到桌面端 SQLite 索引。"""
    if not download_dir or not os.path.isdir(download_dir):
        return 0

    records = _scan_download_dir(download_dir, cover_cache_dir)
    db = ShelfDatabase(db_path)
    db.open()
    try:
        for record in records:
            db.upsert_album(record)
    finally:
        db.close()
    return len(records)


def _scan_download_dir(download_dir: str, cover_cache_dir: str = '') -> list[AlbumRecord]:
    by_id: OrderedDict[str, AlbumRecord] = OrderedDict()
    for root, dirs, files in os.walk(download_dir):
        dirs[:] = [name for name in dirs if name not in {'.git', '__pycache__'}]
        author = _author_from_album_root(download_dir, root)
        album_match = ALBUM_DIR_RE.match(os.path.basename(root).strip())
        if album_match:
            jm_id = album_match.group('id')
            record = by_id.setdefault(
                jm_id,
                AlbumRecord(
                    jm_id=jm_id,
                    title=album_match.group('title').strip(),
                    album_dir=root,
                    authors=[author] if author else [],
                    chapters=_chapters_from_album_dir(root),
                ),
            )
            if not record.album_dir:
                record.album_dir = root
            if author and author not in record.authors:
                record.authors.append(author)
            if not record.cover_path:
                record.cover_path = _cover_for_album(jm_id, root, cover_cache_dir)

        for filename in files:
            pdf_match = PDF_RE.match(filename)
            if not pdf_match:
                continue
            jm_id = pdf_match.group('id')
            record = by_id.setdefault(
                jm_id,
                AlbumRecord(
                    jm_id=jm_id,
                    title=pdf_match.group('title').strip(),
                    authors=[author] if author else [],
                ),
            )
            record.pdf_path = os.path.join(root, filename)
            if not record.title:
                record.title = pdf_match.group('title').strip()

    return list(by_id.values())


def _author_from_album_root(download_dir: str, root: str) -> str:
    rel = os.path.relpath(root, download_dir)
    if rel == '.':
        return ''
    parts = rel.split(os.sep)
    return parts[0] if len(parts) >= 2 else ''


def _chapters_from_album_dir(album_dir: str) -> list[dict[str, str]]:
    chapters = []
    for name in sorted(os.listdir(album_dir)):
        path = os.path.join(album_dir, name)
        if os.path.isdir(path):
            chapters.append({'id': '', 'index': _chapter_index(name), 'title': name})
    return chapters


def _chapter_index(name: str) -> str:
    match = re.search(r'(\d+)', name)
    return match.group(1) if match else ''


def _cover_for_album(jm_id: str, album_dir: str, cover_cache_dir: str = '') -> str:
    source = _first_image(album_dir)
    if not source:
        return ''
    if not cover_cache_dir:
        return source
    try:
        return CoverCache(cover_cache_dir).create_thumbnail(jm_id, source)
    except Exception:
        return source


def _first_image(album_dir: str) -> str:
    for root, _, files in os.walk(album_dir):
        for filename in sorted(files):
            if os.path.splitext(filename)[1].lower() in IMAGE_EXTS:
                return os.path.join(root, filename)
    return ''
