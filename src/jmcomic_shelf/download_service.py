import os
import re
import shutil
from dataclasses import dataclass
from typing import Iterable, List

from .database import ShelfDatabase
from .index_service import record_from_album
from .path_utils import path_exists, path_for_open, walk_paths
from .paths import get_database_path


IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
WINDOWS_INVALID_CHARS = r'<>:"/\|?*'


def parse_album_ids(text: str) -> List[str]:
    result = []
    for chunk in re.split(r'[\s,，]+', text.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.upper().startswith('JM') and chunk[2:].isdigit():
            chunk = chunk[2:]
        result.append(chunk)
    return result


@dataclass
class DownloadTask:
    jm_id: str
    status: str = 'waiting'
    error: str = ''

    def mark_waiting(self) -> None:
        self.status = 'waiting'
        self.error = ''

    def mark_running(self) -> None:
        self.status = 'running'
        self.error = ''

    def mark_success(self) -> None:
        self.status = 'success'
        self.error = ''

    def mark_failed(self, error: str) -> None:
        self.status = 'failed'
        self.error = str(error)


class DownloadService:
    def __init__(
        self,
        option_path: str,
        app_data_dir: str = '',
        download_dir: str = '',
        option_factory=None,
        download_func=None,
    ):
        self.option_path = option_path
        self.app_data_dir = app_data_dir
        self.download_dir = download_dir
        self.option_factory = option_factory
        self.download_func = download_func

    def run_task(self, task: DownloadTask) -> DownloadTask:
        from jmcomic import create_option, download_album

        task.mark_running()
        try:
            if not self.option_path:
                raise ValueError('请先在设置里选择配置文件 jmcomic-option.yml')
            if not os.path.exists(self.option_path):
                raise FileNotFoundError(f'配置文件不存在：{self.option_path}')
            option_factory = self.option_factory or create_option
            download_func = self.download_func or download_album
            option = option_factory(self.option_path)
            result = download_func(task.jm_id, option)
            album = result[0] if isinstance(result, tuple) else result
            pdf_path = self.find_pdf_path(str(album.album_id), album.name)
            if not pdf_path:
                pdf_path = self.build_pdf_from_downloaded_images(album, option)
            if not pdf_path:
                raise FileNotFoundError(f'下载完成，但未找到可合成 PDF 的图片：JM{album.album_id}')
            pdf_path, cover_path = self.organize_downloaded_album(album, pdf_path, option)
            self.index_album(album, pdf_path, cover_path)
            task.mark_success()
        except Exception as e:
            task.mark_failed(e)
        return task

    def index_album(self, album, pdf_path: str | None = None, cover_path: str = '') -> None:
        db = ShelfDatabase(get_database_path(self.app_data_dir))
        db.open()
        try:
            db.upsert_album(record_from_album(
                album,
                pdf_path=pdf_path if pdf_path is not None else self.find_pdf_path(str(album.album_id), album.name),
                cover_path=cover_path,
            ))
        finally:
            db.close()

    def build_pdf_from_downloaded_images(self, album, option=None) -> str:
        if not self.download_dir or not os.path.isdir(path_for_open(self.download_dir)):
            return ''

        album_dir = self._find_album_dir(album, '', option)
        images = _image_paths(album_dir)
        if not images:
            return ''

        try:
            import img2pdf
        except ImportError as exc:
            raise RuntimeError('生成 PDF 需要依赖 img2pdf，请重新安装或更新 JMComic Shelf') from exc

        jm_id = str(album.album_id)
        title = _safe_path_segment(getattr(album, 'name', '') or jm_id)
        pdf_path = os.path.join(album_dir, f'JM{jm_id}-{title}.pdf')
        tmp_path = pdf_path + '.tmp'
        try:
            with open(path_for_open(tmp_path), 'wb') as f:
                f.write(img2pdf.convert([path_for_open(path) for path in images]))
            if not os.path.exists(path_for_open(tmp_path)) or os.path.getsize(path_for_open(tmp_path)) <= 0:
                raise RuntimeError(f'PDF 输出为空：JM{jm_id}')
            os.replace(path_for_open(tmp_path), path_for_open(pdf_path))
        except Exception:
            if os.path.exists(path_for_open(tmp_path)):
                os.remove(path_for_open(tmp_path))
            raise
        return pdf_path

    def organize_downloaded_album(self, album, pdf_path: str, option=None) -> tuple[str, str]:
        if not self.download_dir or not os.path.isdir(path_for_open(self.download_dir)):
            return pdf_path, ''

        jm_id = str(album.album_id)
        title = _safe_path_segment(getattr(album, 'name', '') or jm_id)
        author = _safe_path_segment(_first_author(getattr(album, 'authors', [])) or getattr(album, 'author', '') or '未知作者')
        final_dir = os.path.join(self.download_dir, author)
        os.makedirs(path_for_open(final_dir), exist_ok=True)
        final_pdf = os.path.join(final_dir, f'JM{jm_id}-{title}.pdf')

        album_dir = self._find_album_dir(album, pdf_path, option)
        first_image = _first_image(album_dir)
        cover_path = self._copy_cover(jm_id, title, first_image)

        if os.path.abspath(pdf_path) != os.path.abspath(final_pdf):
            os.makedirs(path_for_open(os.path.dirname(final_pdf)), exist_ok=True)
            if os.path.exists(path_for_open(final_pdf)):
                os.remove(path_for_open(final_pdf))
            shutil.move(path_for_open(pdf_path), path_for_open(final_pdf))

        self._remove_album_image_dir(album_dir, final_dir)
        return final_pdf, cover_path

    def _find_album_dir(self, album, pdf_path: str, option=None) -> str:
        pdf_dir = os.path.dirname(pdf_path)
        if re.match(r'^JM\d+-.+', os.path.basename(pdf_dir), re.IGNORECASE):
            return pdf_dir

        target_name = f'JM{album.album_id}-'
        option_album_dir = ''
        if option is not None:
            try:
                album_dir = option.dir_rule.decide_album_root_dir(album)
                if album_dir and os.path.isdir(path_for_open(album_dir)):
                    if os.path.basename(album_dir).startswith(target_name):
                        return album_dir
                    option_album_dir = album_dir
            except Exception:
                pass

        for root, dirs, _ in walk_paths(self.download_dir):
            for name in dirs:
                candidate = os.path.join(root, name)
                if name.startswith(target_name) and os.path.isdir(path_for_open(candidate)):
                    return candidate

        return option_album_dir

    def _copy_cover(self, jm_id: str, title: str, source_path: str) -> str:
        if not source_path:
            return ''
        ext = os.path.splitext(source_path)[1].lower() or '.jpg'
        cover_dir = os.path.join(self.download_dir, 'Cover')
        os.makedirs(path_for_open(cover_dir), exist_ok=True)
        cover_path = os.path.join(cover_dir, f'JM{jm_id}-{title}{ext}')
        shutil.copy2(path_for_open(source_path), path_for_open(cover_path))
        return cover_path

    def _remove_album_image_dir(self, album_dir: str, final_dir: str) -> None:
        if not album_dir or not os.path.isdir(path_for_open(album_dir)):
            return
        if not _is_inside(album_dir, self.download_dir):
            return
        if os.path.abspath(album_dir) == os.path.abspath(final_dir):
            return
        shutil.rmtree(path_for_open(album_dir))

    def find_pdf_path(self, jm_id: str, title: str = '') -> str:
        if not self.download_dir or not os.path.isdir(path_for_open(self.download_dir)):
            return ''

        prefixes = (f'JM{jm_id}-', f'[JM{jm_id}]')
        exact_names = {f'JM{jm_id}.pdf', f'{jm_id}.pdf'}
        if title:
            exact_names.update({
                f'JM{jm_id}-{title}.pdf',
                f'[JM{jm_id}]{title}.pdf',
                f'{jm_id}-{title}.pdf',
                f'{jm_id}{title}.pdf',
            })
        for root, _, files in walk_paths(self.download_dir):
            for name in files:
                if not name.lower().endswith('.pdf'):
                    continue
                if name in exact_names or name.startswith(prefixes):
                    pdf_path = os.path.join(root, name)
                    if path_exists(pdf_path):
                        return pdf_path
        return ''


def _safe_path_segment(value: str) -> str:
    value = str(value).strip()
    cleaned = ''.join('_' if ch in WINDOWS_INVALID_CHARS or ord(ch) < 32 else ch for ch in value)
    cleaned = cleaned.strip(' .')
    return cleaned or '未命名'


def _first_author(authors: Iterable[str]) -> str:
    for author in authors or []:
        author = str(author).strip()
        if author:
            return author
    return ''


def _first_image(album_dir: str) -> str:
    images = _image_paths(album_dir)
    return images[0] if images else ''


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


def _is_inside(path: str, root: str) -> bool:
    try:
        path = os.path.abspath(path)
        root = os.path.abspath(root)
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False
