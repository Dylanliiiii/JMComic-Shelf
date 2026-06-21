import os
import re
from collections import OrderedDict
from typing import Iterable

from jmcomic.jm_plugin import CatalogPlugin

from .cover_cache import CoverCache
from .database import ShelfDatabase
from .models import AlbumRecord
from .path_utils import path_exists, path_for_open, walk_paths


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
        authors=_first_author_list(info['authors']),
        tags=info['tags'],
        chapters=info['chapters'],
    )


def group_by_author(records: Iterable[AlbumRecord]):
    grouped = OrderedDict()
    for record in records:
        author = _first_author(record.authors) or '未知作者'
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
        db.replace_albums(records)
    finally:
        db.close()
    return len(records)


def _scan_download_dir(download_dir: str, cover_cache_dir: str = '') -> list[AlbumRecord]:
    by_id: OrderedDict[str, AlbumRecord] = OrderedDict()
    catalog_by_id = _catalog_records_by_id(download_dir)
    for root, dirs, files in walk_paths(download_dir):
        dirs[:] = [name for name in dirs if name not in {'.git', '__pycache__', 'Cover', 'covers'}]
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
            if author and not record.authors:
                record.authors = [author]
            if not record.cover_path:
                record.cover_path = _cover_for_album(download_dir, jm_id, root, cover_cache_dir)

        for filename in files:
            pdf_match = PDF_RE.match(filename)
            if not pdf_match:
                continue
            jm_id = pdf_match.group('id')
            pdf_path = os.path.join(root, filename)
            if not path_exists(pdf_path):
                continue
            pdf_author = _author_from_pdf_root(download_dir, root)
            record = by_id.setdefault(
                jm_id,
                AlbumRecord(
                    jm_id=jm_id,
                    title=pdf_match.group('title').strip(),
                    authors=[pdf_author] if pdf_author else [],
                ),
            )
            record.pdf_path = pdf_path
            if not record.album_dir:
                record.album_dir = _album_dir_from_pdf(download_dir, root)
            if not record.title:
                record.title = pdf_match.group('title').strip()
            if pdf_author and not record.authors:
                record.authors = [pdf_author]
            if not record.cover_path:
                record.cover_path = _cover_for_album(download_dir, jm_id, record.album_dir or root, cover_cache_dir)

    for jm_id, record in by_id.items():
        _merge_catalog_record(record, catalog_by_id.get(jm_id))

    return sorted(by_id.values(), key=_record_sort_key)


def _catalog_records_by_id(download_dir: str) -> dict[str, dict]:
    catalog_path = os.path.join(download_dir, 'catalog.md')
    catalog = CatalogPlugin.read_catalog(catalog_path)
    by_id = {}
    for author, items in catalog.items():
        for item in items:
            jm_id = str(item.get('id', '')).removeprefix('JM').removeprefix('jm')
            if not jm_id:
                continue
            record = by_id.setdefault(jm_id, {'authors': [], 'tags': [], 'link': '', 'chapters': []})
            if author and not record['authors']:
                record['authors'].append(author)
            for tag in item.get('tags', []):
                if tag and tag not in record['tags']:
                    record['tags'].append(tag)
            if item.get('link') and not record['link']:
                record['link'] = item['link']
            if item.get('chapters') and not record['chapters']:
                record['chapters'] = item['chapters']
    return by_id


def _merge_catalog_record(record: AlbumRecord, catalog_record: dict | None) -> None:
    if not catalog_record:
        return
    if not record.authors:
        record.authors = _first_author_list(catalog_record.get('authors', []))
    record.tags = list(catalog_record.get('tags', []))
    if catalog_record.get('link') and not record.link:
        record.link = catalog_record['link']
    if catalog_record.get('chapters') and not record.chapters:
        record.chapters = catalog_record['chapters']


def _author_from_album_root(download_dir: str, root: str) -> str:
    rel = os.path.relpath(root, download_dir)
    if rel == '.':
        return ''
    parts = rel.split(os.sep)
    return parts[0] if len(parts) >= 2 else ''


def _author_from_pdf_root(download_dir: str, root: str) -> str:
    rel = os.path.relpath(root, download_dir)
    if rel == '.':
        return ''
    parts = rel.split(os.sep)
    return parts[0] if parts else ''


def _album_dir_from_pdf(download_dir: str, root: str) -> str:
    rel = os.path.relpath(root, download_dir)
    if rel == '.':
        return ''
    return root


def _chapters_from_album_dir(album_dir: str) -> list[dict[str, str]]:
    chapters = []
    for name in sorted(os.listdir(path_for_open(album_dir))):
        path = os.path.join(album_dir, name)
        if os.path.isdir(path_for_open(path)):
            chapters.append({'id': '', 'index': _chapter_index(name), 'title': name})
    return chapters


def _chapter_index(name: str) -> str:
    match = re.search(r'(\d+)', name)
    return match.group(1) if match else ''


def _cover_for_album(download_dir: str, jm_id: str, album_dir: str, cover_cache_dir: str = '') -> str:
    source = _root_cover_image(download_dir, jm_id) or _first_image(album_dir)
    if not source:
        return ''
    if not cover_cache_dir:
        return source
    try:
        return CoverCache(cover_cache_dir).create_thumbnail(jm_id, source)
    except Exception:
        return source


def _first_image(album_dir: str) -> str:
    if not album_dir or not os.path.isdir(path_for_open(album_dir)):
        return ''
    for root, _, files in os.walk(path_for_open(album_dir)):
        for filename in sorted(files):
            if os.path.splitext(filename)[1].lower() in IMAGE_EXTS:
                return os.path.join(root, filename)
    return ''


def _root_cover_image(download_dir: str, jm_id: str) -> str:
    cover_dir = os.path.join(download_dir, 'Cover')
    if not os.path.isdir(path_for_open(cover_dir)):
        return ''
    prefix = f'JM{jm_id}'
    for filename in sorted(os.listdir(path_for_open(cover_dir))):
        stem, ext = os.path.splitext(filename)
        if stem.startswith(prefix) and ext.lower() in IMAGE_EXTS:
            return os.path.join(cover_dir, filename)
    return ''


def _first_author(authors: Iterable[str]) -> str:
    for author in authors or []:
        author = str(author).strip()
        if author:
            return author
    return ''


def _first_author_list(authors: Iterable[str]) -> list[str]:
    author = _first_author(authors)
    return [author] if author else []


def _record_sort_key(record: AlbumRecord):
    return (_first_author(record.authors), -_numeric_jm_id(record.jm_id), record.jm_id)


def _numeric_jm_id(jm_id: str) -> int:
    try:
        return int(str(jm_id))
    except ValueError:
        return 0
