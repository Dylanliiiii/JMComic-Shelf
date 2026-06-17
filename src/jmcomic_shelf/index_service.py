from collections import OrderedDict
from typing import Iterable

from jmcomic.jm_plugin import CatalogPlugin

from .models import AlbumRecord


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
