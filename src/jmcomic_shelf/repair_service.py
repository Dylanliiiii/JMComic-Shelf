import os
import re
import shutil
from dataclasses import dataclass, field

from .index_service import rebuild_index_from_download_dir
from .path_utils import path_exists, path_for_open, walk_paths


IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
ALBUM_DIR_RE = re.compile(r'^JM(?P<id>\d+)-(?P<title>.+)$', re.IGNORECASE)
SKIP_DIRS = {'.git', '__pycache__', 'Cover', 'covers'}


@dataclass
class LibraryRepairEntry:
    jm_id: str
    title: str
    album_dir: str
    status: str
    message: str
    pdf_path: str = ''


@dataclass
class LibraryRepairResult:
    found_dirs: int = 0
    repaired_pdfs: int = 0
    removed_dirs: int = 0
    failed: int = 0
    synced_count: int = 0
    entries: list[LibraryRepairEntry] = field(default_factory=list)


def repair_library(download_dir: str, db_path: str, cover_cache_dir: str = '') -> LibraryRepairResult:
    if not download_dir:
        raise ValueError('请先在设置里选择下载目录。')
    if not os.path.isdir(path_for_open(download_dir)):
        raise FileNotFoundError(f'下载目录不存在：{download_dir}')

    result = LibraryRepairResult()
    for album_dir in _iter_album_image_dirs(download_dir):
        result.found_dirs += 1
        entry = _repair_album_dir(download_dir, album_dir)
        result.entries.append(entry)
        if entry.status == 'repaired':
            result.repaired_pdfs += 1
            result.removed_dirs += 1
        elif entry.status == 'cleaned':
            result.removed_dirs += 1
        elif entry.status == 'failed':
            result.failed += 1

    result.synced_count = rebuild_index_from_download_dir(download_dir, db_path, cover_cache_dir)
    return result


def _iter_album_image_dirs(download_dir: str):
    for root, dirs, _ in walk_paths(download_dir):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        for name in list(dirs):
            candidate = os.path.join(root, name)
            if not ALBUM_DIR_RE.match(name):
                continue
            if _image_paths(candidate):
                yield candidate


def _repair_album_dir(download_dir: str, album_dir: str) -> LibraryRepairEntry:
    match = ALBUM_DIR_RE.match(os.path.basename(album_dir))
    jm_id = match.group('id')
    title = match.group('title').strip()
    final_pdf = _final_pdf_path(album_dir, jm_id, title)
    entry = LibraryRepairEntry(jm_id, title, album_dir, 'skipped', '已存在 PDF，跳过补全。', final_pdf)
    images = _image_paths(album_dir)
    if path_exists(final_pdf):
        if images:
            try:
                _copy_cover(download_dir, jm_id, title, images[0])
                shutil.rmtree(path_for_open(album_dir))
                entry.status = 'cleaned'
                entry.message = '已存在 PDF，已清理残留图片目录。'
            except Exception as exc:
                entry.status = 'failed'
                entry.message = f'清理残留图片目录失败，已保留原目录：{exc}'
                entry.pdf_path = ''
        return entry

    if not images:
        entry.message = '没有找到可用于生成 PDF 的图片。'
        entry.pdf_path = ''
        return entry

    tmp_path = final_pdf + '.tmp'
    try:
        _convert_images_to_pdf(images, tmp_path)
        if not os.path.exists(path_for_open(tmp_path)) or os.path.getsize(path_for_open(tmp_path)) <= 0:
            raise RuntimeError('PDF 输出为空。')
        os.replace(path_for_open(tmp_path), path_for_open(final_pdf))
        _copy_cover(download_dir, jm_id, title, images[0])
        shutil.rmtree(path_for_open(album_dir))
        entry.status = 'repaired'
        entry.message = '已补全 PDF，并清理原图片目录。'
        entry.pdf_path = final_pdf
        return entry
    except Exception as exc:
        if os.path.exists(path_for_open(tmp_path)):
            os.remove(path_for_open(tmp_path))
        entry.status = 'failed'
        entry.message = f'生成 PDF 失败，已保留原图片目录：{exc}'
        entry.pdf_path = ''
        return entry


def _final_pdf_path(album_dir: str, jm_id: str, title: str) -> str:
    author_dir = os.path.dirname(album_dir)
    return os.path.join(author_dir, f'JM{jm_id}-{title}.pdf')


def _convert_images_to_pdf(images: list[str], output_path: str) -> None:
    try:
        import img2pdf
    except ImportError as exc:
        raise RuntimeError('生成 PDF 需要依赖 img2pdf，请重新安装或更新 JMComic Shelf') from exc
    with open(path_for_open(output_path), 'wb') as f:
        f.write(img2pdf.convert([path_for_open(path) for path in images]))


def _copy_cover(download_dir: str, jm_id: str, title: str, source_path: str) -> str:
    ext = os.path.splitext(source_path)[1].lower() or '.jpg'
    cover_dir = os.path.join(download_dir, 'Cover')
    os.makedirs(path_for_open(cover_dir), exist_ok=True)
    cover_path = os.path.join(cover_dir, f'JM{jm_id}-{title}{ext}')
    shutil.copy2(path_for_open(source_path), path_for_open(cover_path))
    return cover_path


def _image_paths(album_dir: str) -> list[str]:
    if not album_dir or not os.path.isdir(path_for_open(album_dir)):
        return []
    result = []
    for root, dirs, files in os.walk(path_for_open(album_dir)):
        dirs.sort(key=_natural_sort_key)
        for filename in sorted(files, key=_natural_sort_key):
            if os.path.splitext(filename)[1].lower() in IMAGE_EXTS:
                result.append(os.path.join(root, filename))
    return result


def _natural_sort_key(value: str):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', str(value))]
