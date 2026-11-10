import os
import re
import unicodedata
from dataclasses import dataclass


def parse_preview_ids(text: str) -> tuple[list[str], list[str]]:
    """接受空白或常见标点分隔的编号，保留顺序并记录格式有误的输入。"""
    from .download_service import parse_album_ids

    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'(?i)(?<=[0-9])(?=jm\s*[0-9])', ' ', text)
    text = re.sub(r'(?i)\bjm\s+(?=[0-9])', 'JM', text)
    text = re.sub(r'[;、|]+', ' ', text)
    ids = []
    invalid = []
    for token in parse_album_ids(text):
        if re.fullmatch(r'[0-9]+', token) and token.strip('0'):
            ids.append(token.lstrip('0'))
        else:
            invalid.append(token)
    return list(dict.fromkeys(ids)), list(dict.fromkeys(invalid))


@dataclass
class DetailResult:
    album: object
    cover_path: str = ''


def fetch_album_detail(option_path: str, jm_id: str):
    return fetch_album_detail_result(option_path, jm_id).album


def fetch_album_detail_result(
    option_path: str,
    jm_id: str,
    cover_cache_dir: str = '',
    local_cover_path: str = '',
    option_factory=None,
) -> DetailResult:
    from jmcomic import create_option

    if not option_path:
        raise ValueError('请先在设置里选择配置文件 jmcomic-option.yml')
    if not os.path.exists(option_path):
        raise FileNotFoundError(f'配置文件不存在：{option_path}')

    option = (option_factory or create_option)(option_path)
    client = option.build_jm_client()
    album = client.get_album_detail(jm_id)
    cover_path = _usable_cover_path(local_cover_path) or _ensure_online_cover(client, jm_id, cover_cache_dir)
    return DetailResult(album=album, cover_path=cover_path)


def _usable_cover_path(path: str) -> str:
    if path and os.path.exists(path):
        return path
    return ''


def _ensure_online_cover(client, jm_id: str, cover_cache_dir: str) -> str:
    if not cover_cache_dir:
        return ''

    os.makedirs(cover_cache_dir, exist_ok=True)
    cover_path = os.path.join(cover_cache_dir, f'JM{jm_id}.jpg')
    if os.path.exists(cover_path):
        return cover_path

    temp_path = os.path.join(cover_cache_dir, f'JM{jm_id}.download.jpg')
    try:
        client.download_album_cover(jm_id, temp_path)
        os.replace(temp_path, cover_path)
        return cover_path
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return ''
