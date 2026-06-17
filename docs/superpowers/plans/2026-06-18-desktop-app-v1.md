# JMComic Shelf Desktop App v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first JMComic Shelf desktop application around the existing downloader workflow, with a PySide6 + QFluentWidgets UI, SQLite shelf index, complete non-cropped cover thumbnails, and preserved Markdown catalog output.

**Architecture:** Keep upstream `jmcomic` download logic intact and add a separate `jmcomic_shelf` package for desktop settings, indexing, cover cache, services, and UI. A small `shelf_index` plugin updates the SQLite index after album downloads, while `CatalogPlugin` continues to update `catalog.md`.

**Tech Stack:** Python 3.12+, `sqlite3`, `Pillow`, `PySide6`, `PySide6-Fluent-Widgets` / `qfluentwidgets`, existing `jmcomic` API and plugin system, `unittest`.

---

## File Structure

- Create `src/jmcomic_shelf/__init__.py`: desktop package marker.
- Create `src/jmcomic_shelf/paths.py`: Windows user data paths and safe directory helpers.
- Create `src/jmcomic_shelf/settings.py`: `settings.json` load/save with current download directory and option path.
- Create `src/jmcomic_shelf/models.py`: dataclasses for albums and download tasks.
- Create `src/jmcomic_shelf/database.py`: SQLite schema, migrations, upsert, query, and relation helpers.
- Create `src/jmcomic_shelf/cover_cache.py`: complete-cover thumbnail generation without cropping.
- Create `src/jmcomic_shelf/index_service.py`: translate JM album data into SQLite records and group records by author.
- Create `src/jmcomic_shelf/download_service.py`: parse JM IDs, run existing download API, record task states, retry failures.
- Create `src/jmcomic_shelf/detail_service.py`: fetch album detail and detect local PDF/index state.
- Create `src/jmcomic_shelf/file_actions.py`: open PDF and reveal file in Explorer.
- Create `src/jmcomic_shelf/app.py`: desktop app entry point.
- Create `src/jmcomic_shelf/ui/main_window.py`: QFluentWidgets-compatible main window and left navigation.
- Create `src/jmcomic_shelf/ui/library_page.py`: search, filters, author sections, cover cards.
- Create `src/jmcomic_shelf/ui/download_page.py`: JM input, task list, retry button.
- Create `src/jmcomic_shelf/ui/detail_page.py`: one-ID detail view without query history.
- Create `src/jmcomic_shelf/ui/settings_page.py`: download directory, option path, app data path, clear cache, rebuild index.
- Modify `src/jmcomic/jm_plugin.py`: add `ShelfIndexPlugin`.
- Modify `pyproject.toml` and `setup.py`: add GUI dependencies and `jmcomic-shelf` script.
- Modify `README.md` and `assets/readme/README-en.md`: document desktop app workflow and reference links.
- Test files:
  - `tests/test_jmcomic/test_shelf_settings.py`
  - `tests/test_jmcomic/test_shelf_database.py`
  - `tests/test_jmcomic/test_shelf_cover_cache.py`
  - `tests/test_jmcomic/test_shelf_index_service.py`
  - `tests/test_jmcomic/test_shelf_download_service.py`
  - Extend `tests/test_jmcomic/test_jm_plugin.py` for `ShelfIndexPlugin`.

## Task 1: Settings And Path Foundation

**Files:**
- Create: `src/jmcomic_shelf/__init__.py`
- Create: `src/jmcomic_shelf/paths.py`
- Create: `src/jmcomic_shelf/settings.py`
- Test: `tests/test_jmcomic/test_shelf_settings.py`

- [ ] **Step 1: Write failing settings/path tests**

```python
from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfSettings(unittest.TestCase):

    def test_default_app_data_dir_uses_appdata_when_present(self):
        from jmcomic_shelf.paths import get_default_app_data_dir

        old = os.environ.get('APPDATA')
        with TemporaryDirectory() as tmp:
            os.environ['APPDATA'] = tmp
            try:
                self.assertEqual(
                    get_default_app_data_dir(),
                    os.path.join(tmp, 'JMComic Shelf'),
                )
            finally:
                if old is None:
                    os.environ.pop('APPDATA', None)
                else:
                    os.environ['APPDATA'] = old

    def test_settings_round_trip(self):
        from jmcomic_shelf.settings import ShelfSettings

        with TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'settings.json')
            settings = ShelfSettings(
                download_dir='D:/path/to/JMComic',
                option_path='D:/path/to/JMComic Shelf/jmcomic-option.yml',
                app_data_dir=tmp,
            )

            settings.save(path)
            loaded = ShelfSettings.load(path)

            self.assertEqual(loaded.download_dir, 'D:/path/to/JMComic')
            self.assertEqual(loaded.option_path, 'D:/path/to/JMComic Shelf/jmcomic-option.yml')
            self.assertEqual(loaded.app_data_dir, tmp)
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_settings -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'jmcomic_shelf'`.

- [ ] **Step 3: Implement modules**

Create `src/jmcomic_shelf/__init__.py`:

```python
"""Desktop application layer for JMComic Shelf."""

__all__ = ['__version__']
__version__ = '0.1.0'
```

Create `src/jmcomic_shelf/paths.py`:

```python
import os


APP_NAME = 'JMComic Shelf'


def get_default_app_data_dir() -> str:
    base = os.environ.get('APPDATA') or os.path.expanduser('~')
    return os.path.join(base, APP_NAME)


def ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path
```

Create `src/jmcomic_shelf/settings.py`:

```python
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
```

- [ ] **Step 4: Verify and commit**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_settings -v
git add src/jmcomic_shelf/__init__.py src/jmcomic_shelf/paths.py src/jmcomic_shelf/settings.py tests/test_jmcomic/test_shelf_settings.py
git commit -m "feat: add desktop settings foundation"
```

Expected: tests PASS, commit succeeds.

## Task 2: SQLite Schema And Repository

**Files:**
- Create: `src/jmcomic_shelf/models.py`
- Create: `src/jmcomic_shelf/database.py`
- Test: `tests/test_jmcomic/test_shelf_database.py`

- [ ] **Step 1: Write failing database tests**

```python
from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfDatabase(unittest.TestCase):

    def test_upsert_album_and_query_all(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            db.upsert_album(AlbumRecord(
                jm_id='211899',
                title='作品A',
                link='https://18comic.vip/album/211899/',
                pdf_path=os.path.join(tmp, 'JM211899-作品A.pdf'),
                cover_path=os.path.join(tmp, 'covers', 'JM211899.jpg'),
                authors=['作者A', '作者B'],
                tags=['标签1', '标签2'],
                chapters=[{'id': '211899', 'index': '1', 'title': '作品A'}],
            ))

            result = db.query_albums('')
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].jm_id, '211899')
            self.assertEqual(result[0].authors, ['作者A', '作者B'])
            self.assertEqual(result[0].tags, ['标签1', '标签2'])

    def test_query_by_jm_id_author_and_tag(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            db.upsert_album(AlbumRecord('211899', '作品A', '', '', '', ['作者A'], ['后宫'], []))
            db.upsert_album(AlbumRecord('123456', '作品B', '', '', '', ['作者B'], ['全彩'], []))

            self.assertEqual([x.jm_id for x in db.query_albums('JM211899')], ['211899'])
            self.assertEqual([x.jm_id for x in db.query_albums('作者B')], ['123456'])
            self.assertEqual([x.jm_id for x in db.query_albums('后宫')], ['211899'])
```

- [ ] **Step 2: Implement `AlbumRecord` and `ShelfDatabase`**

Create `src/jmcomic_shelf/models.py`:

```python
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
```

Create `src/jmcomic_shelf/database.py` with:

- SQLite tables: `albums`, `authors`, `tags`, `album_authors`, `album_tags`, `chapters`.
- `ShelfDatabase.open()`, `close()`, `upsert_album(record)`, `query_albums(query='')`.
- `query_albums('')` returns all albums.
- `query_albums('JM211899')`, `query_albums('作者')`, and `query_albums('标签')` search ID/title/author/tag.
- Do not create a fake `全部` tag; empty query means all.

- [ ] **Step 3: Verify and commit**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_database -v
git add src/jmcomic_shelf/models.py src/jmcomic_shelf/database.py tests/test_jmcomic/test_shelf_database.py
git commit -m "feat: add shelf sqlite index"
```

Expected: tests PASS.

## Task 3: Complete Non-Cropped Cover Cache

**Files:**
- Create: `src/jmcomic_shelf/cover_cache.py`
- Test: `tests/test_jmcomic/test_shelf_cover_cache.py`

- [ ] **Step 1: Write failing cover tests**

```python
from test_jmcomic import *
from tempfile import TemporaryDirectory
from PIL import Image


class TestShelfCoverCache(unittest.TestCase):

    def test_thumbnail_preserves_portrait_aspect_ratio_without_crop(self):
        from jmcomic_shelf.cover_cache import CoverCache

        with TemporaryDirectory() as tmp:
            source = os.path.join(tmp, 'source.jpg')
            Image.new('RGB', (1000, 1600), 'red').save(source)

            cache = CoverCache(os.path.join(tmp, 'covers'), max_width=240)
            output = cache.create_thumbnail('211899', source)

            with Image.open(output) as img:
                self.assertEqual(img.size, (240, 384))

    def test_thumbnail_preserves_landscape_aspect_ratio_without_crop(self):
        from jmcomic_shelf.cover_cache import CoverCache

        with TemporaryDirectory() as tmp:
            source = os.path.join(tmp, 'source.jpg')
            Image.new('RGB', (1600, 1000), 'blue').save(source)

            cache = CoverCache(os.path.join(tmp, 'covers'), max_width=240)
            output = cache.create_thumbnail('123456', source)

            with Image.open(output) as img:
                self.assertEqual(img.size, (240, 150))
```

- [ ] **Step 2: Implement cover cache**

Create `src/jmcomic_shelf/cover_cache.py`:

```python
import os
from PIL import Image


class CoverCache:
    def __init__(self, cache_dir: str, max_width: int = 240, quality: int = 82):
        self.cache_dir = cache_dir
        self.max_width = max_width
        self.quality = quality

    def create_thumbnail(self, jm_id: str, source_path: str) -> str:
        os.makedirs(self.cache_dir, exist_ok=True)
        output = os.path.join(self.cache_dir, f'JM{jm_id}.jpg')
        with Image.open(source_path) as img:
            img = img.convert('RGB')
            width, height = img.size
            if width > self.max_width:
                ratio = self.max_width / width
                img = img.resize((self.max_width, max(1, round(height * ratio))), Image.Resampling.LANCZOS)
            img.save(output, format='JPEG', quality=self.quality, optimize=True)
        return output

    def clear(self) -> int:
        if not os.path.isdir(self.cache_dir):
            return 0
        count = 0
        for name in os.listdir(self.cache_dir):
            if name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                os.remove(os.path.join(self.cache_dir, name))
                count += 1
        return count
```

- [ ] **Step 3: Verify and commit**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_cover_cache -v
git add src/jmcomic_shelf/cover_cache.py tests/test_jmcomic/test_shelf_cover_cache.py
git commit -m "feat: add complete cover thumbnail cache"
```

Expected: tests PASS.

## Task 4: Index Service

**Files:**
- Create: `src/jmcomic_shelf/index_service.py`
- Test: `tests/test_jmcomic/test_shelf_index_service.py`

- [ ] **Step 1: Write failing tests**

```python
from test_jmcomic import *


class FakeShelfAlbum:
    def __init__(self):
        self.album_id = '211899'
        self.name = '作品A'
        self.authors = ['作者A', '作者B']
        self.tags = ['标签1', '标签2']
        self.episode_list = [('211899', '1', '作品A')]


class TestShelfIndexService(unittest.TestCase):

    def test_record_from_album_uses_album_metadata(self):
        from jmcomic_shelf.index_service import record_from_album

        record = record_from_album(FakeShelfAlbum(), pdf_path='D:/downloads/JM211899-作品A.pdf', cover_path='cover.jpg')

        self.assertEqual(record.jm_id, '211899')
        self.assertEqual(record.title, '作品A')
        self.assertEqual(record.authors, ['作者A', '作者B'])
        self.assertEqual(record.tags, ['标签1', '标签2'])
        self.assertEqual(record.chapters, [{'id': '211899', 'index': '1', 'title': '作品A'}])

    def test_group_by_author_for_library_display(self):
        from jmcomic_shelf.index_service import group_by_author
        from jmcomic_shelf.models import AlbumRecord

        records = [
            AlbumRecord('1', 'A', authors=['作者A', '作者B']),
            AlbumRecord('2', 'B', authors=['作者A']),
        ]

        grouped = group_by_author(records)

        self.assertEqual([x.jm_id for x in grouped['作者A']], ['1', '2'])
        self.assertEqual([x.jm_id for x in grouped['作者B']], ['1'])
```

- [ ] **Step 2: Implement index service**

Create `src/jmcomic_shelf/index_service.py`:

```python
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
```

- [ ] **Step 3: Verify and commit**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_index_service -v
git add src/jmcomic_shelf/index_service.py tests/test_jmcomic/test_shelf_index_service.py
git commit -m "feat: add shelf index mapping"
```

Expected: tests PASS.

## Task 5: Shelf Index Plugin

**Files:**
- Modify: `src/jmcomic/jm_plugin.py`
- Test: extend `tests/test_jmcomic/test_jm_plugin.py`

- [ ] **Step 1: Add failing plugin test**

Add after `Test_CatalogPlugin`:

```python
class Test_ShelfIndexPlugin(unittest.TestCase):

    def test_shelf_index_plugin_updates_sqlite(self):
        from jmcomic.jm_plugin import ShelfIndexPlugin
        from jmcomic_shelf.database import ShelfDatabase

        album = FakeCatalogAlbum('211899', '作品A', ['作者A'], ['标签1'])

        with TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, 'shelf.db')
            plugin = ShelfIndexPlugin(None)
            plugin.invoke(album=album, db_path=db_path, pdf_path=os.path.join(tmp, 'JM211899-作品A.pdf'))

            db = ShelfDatabase(db_path)
            db.open()
            result = db.query_albums('211899')

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].title, '作品A')
            self.assertEqual(result[0].authors, ['作者A'])
```

- [ ] **Step 2: Implement plugin**

Add below `CatalogPlugin`:

```python
class ShelfIndexPlugin(JmOptionPlugin):
    plugin_key = 'shelf_index'

    def invoke(self, album: JmAlbumDetail = None, db_path=None, pdf_path='', cover_path='', **kwargs) -> None:
        if album is None:
            return

        self.require_param(db_path, 'shelf_index 插件需要 db_path 参数')

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.index_service import record_from_album

        db = ShelfDatabase(JmcomicText.parse_to_abspath(db_path))
        db.open()
        try:
            db.upsert_album(record_from_album(album, pdf_path=pdf_path, cover_path=cover_path))
        finally:
            db.close()

        self.log(f'更新桌面书库索引: {db_path}', 'finish')
```

- [ ] **Step 3: Verify and commit**

```powershell
python -m unittest discover -s tests -p test_jm_plugin.py -k "catalog or shelf_index" -v
python -m py_compile src\jmcomic\jm_plugin.py
git add src/jmcomic/jm_plugin.py tests/test_jmcomic/test_jm_plugin.py
git commit -m "feat: add shelf index plugin"
```

Expected: tests PASS and compile succeeds.

## Task 6: Download Service

**Files:**
- Create: `src/jmcomic_shelf/download_service.py`
- Test: `tests/test_jmcomic/test_shelf_download_service.py`

- [ ] **Step 1: Write failing tests**

```python
from test_jmcomic import *


class TestShelfDownloadService(unittest.TestCase):

    def test_parse_album_ids_supports_space_newline_and_comma(self):
        from jmcomic_shelf.download_service import parse_album_ids

        self.assertEqual(
            parse_album_ids('211899 123456,p789\nJM654321'),
            ['211899', '123456', 'p789', '654321'],
        )

    def test_task_retry_resets_failed_state(self):
        from jmcomic_shelf.download_service import DownloadTask

        task = DownloadTask(jm_id='211899', status='failed', error='network')
        task.mark_waiting()

        self.assertEqual(task.status, 'waiting')
        self.assertEqual(task.error, '')
```

- [ ] **Step 2: Implement service**

Create `src/jmcomic_shelf/download_service.py`:

```python
import re
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
            option = create_option(self.option_path)
            download_album(task.jm_id, option)
            task.mark_success()
        except Exception as e:
            task.mark_failed(e)
        return task
```

- [ ] **Step 3: Verify and commit**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_download_service -v
git add src/jmcomic_shelf/download_service.py tests/test_jmcomic/test_shelf_download_service.py
git commit -m "feat: add desktop download service"
```

Expected: tests PASS.

## Task 7: File Actions And Detail Service

**Files:**
- Create: `src/jmcomic_shelf/file_actions.py`
- Create: `src/jmcomic_shelf/detail_service.py`

- [ ] **Step 1: Implement file actions**

Create `src/jmcomic_shelf/file_actions.py`:

```python
import os
import subprocess


def open_pdf(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    os.startfile(path)


def reveal_in_explorer(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    subprocess.run(['explorer', '/select,', os.path.normpath(path)], check=False)
```

- [ ] **Step 2: Implement detail service**

Create `src/jmcomic_shelf/detail_service.py`:

```python
def fetch_album_detail(option_path: str, jm_id: str):
    from jmcomic import create_option

    option = create_option(option_path)
    client = option.build_jm_client()
    return client.get_album_detail(jm_id)
```

- [ ] **Step 3: Verify and commit**

```powershell
python -m py_compile src\jmcomic_shelf\file_actions.py src\jmcomic_shelf\detail_service.py
git add src/jmcomic_shelf/file_actions.py src/jmcomic_shelf/detail_service.py
git commit -m "feat: add desktop file and detail services"
```

Expected: compile succeeds.

## Task 8: Desktop App Shell

**Files:**
- Modify: `pyproject.toml`
- Modify: `setup.py`
- Create: `src/jmcomic_shelf/app.py`
- Create: `src/jmcomic_shelf/ui/__init__.py`
- Create: `src/jmcomic_shelf/ui/main_window.py`
- Create: `src/jmcomic_shelf/ui/library_page.py`
- Create: `src/jmcomic_shelf/ui/download_page.py`
- Create: `src/jmcomic_shelf/ui/detail_page.py`
- Create: `src/jmcomic_shelf/ui/settings_page.py`

- [ ] **Step 1: Add package dependencies and script**

Add to `pyproject.toml` dependencies:

```toml
    "PySide6",
    "PySide6-Fluent-Widgets",
```

Add to `[project.scripts]`:

```toml
jmcomic-shelf = "jmcomic_shelf.app:main"
```

Add to `setup.py` `install_requires`:

```python
        'PySide6',
        'PySide6-Fluent-Widgets',
```

Add to `setup.py` console scripts:

```python
            'jmcomic-shelf = jmcomic_shelf.app:main',
```

- [ ] **Step 2: Create app entry and minimal pages**

`src/jmcomic_shelf/app.py`:

```python
def main():
    import sys
    from PySide6.QtWidgets import QApplication

    from .ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
```

Create each page as a QWidget with a label:

```python
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LibraryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('书库'))
```

Use matching class names and labels for `DownloadPage`, `DetailPage`, and `SettingsPage`.

- [ ] **Step 3: Create main window with icon + text navigation**

`src/jmcomic_shelf/ui/main_window.py`:

```python
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QWidget

from .detail_page import DetailPage
from .download_page import DownloadPage
from .library_page import LibraryPage
from .settings_page import SettingsPage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JMComic Shelf')
        self.resize(1100, 720)

        self.nav = QListWidget()
        self.nav.setFixedWidth(160)
        self.stack = QStackedWidget()

        self.pages = [
            ('▦  书库', LibraryPage()),
            ('↓  下载', DownloadPage()),
            ('ℹ  查看详情', DetailPage()),
            ('⚙  设置', SettingsPage()),
        ]

        for title, page in self.pages:
            self.nav.addItem(QListWidgetItem(title))
            self.stack.addWidget(page)

        layout = QHBoxLayout(self)
        layout.addWidget(self.nav)
        layout.addWidget(self.stack, 1)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
```

- [ ] **Step 4: Verify and commit**

```powershell
python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py
git add pyproject.toml setup.py src/jmcomic_shelf/app.py src/jmcomic_shelf/ui
git commit -m "feat: add desktop app shell"
```

Expected: compile succeeds if GUI dependencies are installed.

## Task 9: UI Pages

**Files:**
- Modify: `src/jmcomic_shelf/ui/library_page.py`
- Modify: `src/jmcomic_shelf/ui/download_page.py`
- Modify: `src/jmcomic_shelf/ui/detail_page.py`
- Modify: `src/jmcomic_shelf/ui/settings_page.py`

- [ ] **Step 1: Build library page**

Implement:

- Search input placeholder `搜索 JM号 / 作者 / 标签`.
- `全部` default filter.
- Author sections as `{作者名} · {数量} 本`.
- Cover cards with complete image, elided `JM{jm_id} {title}` caption.
- Right-click menu with `打开 PDF` and `在文件资源管理器中显示位置`.

- [ ] **Step 2: Build download page**

Implement:

- Multi-line JM input.
- `开始下载` button.
- Task list columns `JM号`, `状态`, `错误`, `操作`.
- Failed rows show `重试`.
- Use `parse_album_ids()` and `DownloadTask`.

- [ ] **Step 3: Build detail page**

Implement:

- Single JM ID input.
- `查看详情` button.
- Detail labels for title/authors/tags/chapters/link.
- No query history.
- If local PDF exists, show open/reveal actions; otherwise show go-to-download action.

- [ ] **Step 4: Build settings page**

Implement:

- Download directory selector.
- `jmcomic-option.yml` path selector.
- Read-only app data directory display.
- `清理封面缓存` button.
- `重建索引` button wired to the rebuild service entry.
- Do not implement app data directory migration.

- [ ] **Step 5: Verify and commit**

```powershell
python -m py_compile src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py
git add src/jmcomic_shelf/ui
git commit -m "feat: add desktop app pages"
```

Expected: compile succeeds.

## Task 10: README And Final Verification

**Files:**
- Modify: `README.md`
- Modify: `assets/readme/README-en.md`
- Modify: `development-log.md`

- [ ] **Step 1: Document desktop workflow**

Add to Chinese README:

- `jmcomic-shelf` command.
- `%APPDATA%/JMComic Shelf/` for desktop app data.
- Download content remains in user-selected directory.
- `catalog.md` remains in download root.
- Reference links:
  - https://github.com/ok-oldking/ok-script
  - https://github.com/ok-oldking/pyappify

Add concise English note in `assets/readme/README-en.md`.

- [ ] **Step 2: Run focused verification**

```powershell
python -m unittest tests.test_jmcomic.test_shelf_settings -v
python -m unittest tests.test_jmcomic.test_shelf_database -v
python -m unittest tests.test_jmcomic.test_shelf_cover_cache -v
python -m unittest tests.test_jmcomic.test_shelf_index_service -v
python -m unittest tests.test_jmcomic.test_shelf_download_service -v
python -m unittest discover -s tests -p test_jm_plugin.py -k "catalog or shelf_index" -v
python -m py_compile src\jmcomic_shelf\app.py src\jmcomic\jm_plugin.py
```

Expected: all tests pass and compile commands exit 0.

- [ ] **Step 3: Run manual desktop smoke test**

```powershell
python -m jmcomic_shelf.app
```

Expected:

- Window opens.
- Left navigation shows icon + text entries.
- Default page is `书库`.
- Settings page displays app data directory and cache button.
- No real download is triggered during smoke test.

- [ ] **Step 4: Update development log**

Record:

- Modified files.
- Implemented desktop app v1 scope.
- Verification commands and results.
- Note that no `jmcomic-option.yml`, account credentials, downloads, PDFs, cover cache, or local `catalog.md` were committed.

- [ ] **Step 5: Final safety checks**

```powershell
git status --short
git check-ignore -v jmcomic-option.yml .superpowers/brainstorm/desktop-app/layout-preview.html
rg -n "password|passwd|cookie|token|proxy|D:\\\\|C:\\\\" README.md AGENTS.md development-log.md docs src tests
```

Expected:

- `jmcomic-option.yml` is ignored.
- `.superpowers/` is ignored.
- Sensitive-word matches are only policy text, example paths, or existing upstream docs; no real credentials or private download files appear.

- [ ] **Step 6: Commit and push**

```powershell
git add README.md assets/readme/README-en.md development-log.md
git commit -m "docs: document desktop app workflow"
git push origin master
```

Expected: push succeeds to `origin master`.

## Self-Review

- Spec coverage: covers UI shell, library search/grouping, one download directory, SQLite index, Markdown catalog retention, complete non-cropped cover thumbnails, download retry, no detail history, settings without data migration, and reference URLs.
- Completion scan: no `TBD`, `TODO`, or unresolved user-confirmation items remain.
- Type consistency: plan consistently uses `AlbumRecord`, `ShelfDatabase`, `CoverCache`, `DownloadTask`, and `ShelfSettings`.
