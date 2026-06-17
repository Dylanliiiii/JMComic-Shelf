import json
import os
from dataclasses import asdict, dataclass

from .paths import get_default_app_data_dir


@dataclass
class ShelfSettings:
    download_dir: str = ''
    option_path: str = ''
    app_data_dir: str = ''

    def __post_init__(self):
        if not self.app_data_dir:
            self.app_data_dir = get_default_app_data_dir()

    @classmethod
    def load(cls, filepath: str) -> 'ShelfSettings':
        if not os.path.exists(filepath):
            return cls()
        with open(filepath, encoding='utf-8') as f:
            return cls(**json.load(f))

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)
            f.write('\n')
