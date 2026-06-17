from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AlbumRecord:
    jm_id: str
    title: str
    link: str = ''
    pdf_path: str = ''
    cover_path: str = ''
    authors: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    chapters: List[Dict[str, str]] = field(default_factory=list)
    album_dir: str = ''
