import os
from dataclasses import dataclass


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
