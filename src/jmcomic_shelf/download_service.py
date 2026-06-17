import re
import os
from dataclasses import dataclass
from typing import List


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
    def __init__(self, option_path: str):
        self.option_path = option_path

    def run_task(self, task: DownloadTask) -> DownloadTask:
        from jmcomic import create_option, download_album

        task.mark_running()
        try:
            if not self.option_path:
                raise ValueError('请先在设置里选择配置文件 jmcomic-option.yml')
            if not os.path.exists(self.option_path):
                raise FileNotFoundError(f'配置文件不存在: {self.option_path}')
            option = create_option(self.option_path)
            download_album(task.jm_id, option)
            task.mark_success()
        except Exception as e:
            task.mark_failed(e)
        return task
