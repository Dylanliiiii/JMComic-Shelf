import re
import os
from dataclasses import dataclass
from typing import List

from .database import ShelfDatabase
from .index_service import record_from_album
from .paths import get_database_path


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
                raise FileNotFoundError(f'配置文件不存在: {self.option_path}')
            option_factory = self.option_factory or create_option
            download_func = self.download_func or download_album
            option = option_factory(self.option_path)
            result = download_func(task.jm_id, option)
            album = result[0] if isinstance(result, tuple) else result
            self.index_album(album)
            task.mark_success()
        except Exception as e:
            task.mark_failed(e)
        return task

    def index_album(self, album) -> None:
        db = ShelfDatabase(get_database_path(self.app_data_dir))
        db.open()
        try:
            db.upsert_album(record_from_album(
                album,
                pdf_path=self.find_pdf_path(str(album.album_id), album.name),
            ))
        finally:
            db.close()

    def find_pdf_path(self, jm_id: str, title: str = '') -> str:
        if not self.download_dir or not os.path.isdir(self.download_dir):
            return ''

        exact_names = [f'JM{jm_id}-{title}.pdf'] if title else []
        exact_names.append(f'JM{jm_id}.pdf')
        for root, _, files in os.walk(self.download_dir):
            for name in files:
                if name in exact_names or (name.startswith(f'JM{jm_id}-') and name.lower().endswith('.pdf')):
                    return os.path.join(root, name)
        return ''
