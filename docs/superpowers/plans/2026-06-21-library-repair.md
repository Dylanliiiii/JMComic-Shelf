# 书库修复功能页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增桌面端“书库修复”页面，一键补全残留图片目录缺失的 PDF，成功后清理图片目录，并复用现有索引重建同步 SQLite 与 `catalog.md`。

**Architecture:** 新增 `repair_service.py` 承担文件扫描、PDF 生成、封面复制、目录清理和索引重建编排；UI 新增 `RepairPage`，通过 `QThread` 调用服务并展示摘要日志；`MainWindow` 只负责按现有 `addSubInterface()` 模式新增导航项。

**Tech Stack:** Python、PySide6、QFluentWidgets、SQLite、`img2pdf`、`unittest`。

---

## File Structure

- Create: `src/jmcomic_shelf/repair_service.py`
  - 负责扫描残留 `JM号-标题` 图片目录、生成 PDF、复制封面、成功后删除图片目录、调用 `rebuild_index_from_download_dir()`。
- Create: `src/jmcomic_shelf/ui/repair_page.py`
  - 负责“书库修复”页面、主按钮、摘要卡片、日志展示和后台 worker。
- Create: `tests/test_jmcomic/test_shelf_repair_service.py`
  - 覆盖服务层红绿测试。
- Modify: `tests/test_jmcomic/test_shelf_library_page.py`
  - 补充主窗口导航与按钮样式约束测试，沿用现有 UI 测试文件。
- Modify: `src/jmcomic_shelf/ui/main_window.py`
  - 引入并注册 `RepairPage`，导航项位于“禁漫预览”和底部“设置”之间，图标使用 QFluentWidgets 内置图标。
- Modify: `README.md`
  - 说明桌面端提供书库修复入口。
- Modify: `AGENTS.md`
  - 更新桌面端工作流和质量要求。
- Modify: `.agents/skills/jmcomic-shelf-project/SKILL.md`
  - 更新项目专属 Skill 中的桌面端模块与修复规则。
- Modify: `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
  - 补充“书库修复”页面设计。
- Modify: `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
  - 补充 v1 后续任务中的修复页。
- Modify: `development-log.md`
  - 顶部新增日常开发记录。
- Modify: `TASKS.md`
  - 按步骤勾选，收尾时清空为“暂无进行中任务”。

## Task 1: 修复服务红绿测试

**Files:**
- Create: `tests/test_jmcomic/test_shelf_repair_service.py`
- Create later: `src/jmcomic_shelf/repair_service.py`

- [ ] **Step 1: Write failing service tests**

Create `tests/test_jmcomic/test_shelf_repair_service.py`:

```python
from test_jmcomic import *
from tempfile import TemporaryDirectory
from unittest.mock import patch


class TestShelfRepairService(unittest.TestCase):

    def test_repair_library_builds_missing_pdf_removes_image_dir_and_rebuilds_index(self):
        from PIL import Image
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.repair_service import repair_library

        with TemporaryDirectory() as tmp:
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A')
            chapter_dir = os.path.join(album_dir, '第1章')
            os.makedirs(chapter_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(chapter_dir, '00001.jpg'))
            Image.new('RGB', (120, 180), 'blue').save(os.path.join(chapter_dir, '00002.jpg'))

            db_path = os.path.join(tmp, 'app', 'shelf.db')
            result = repair_library(tmp, db_path, os.path.join(tmp, 'app', 'covers'))

            final_pdf = os.path.join(tmp, '作者A', 'JM211899-作品A.pdf')
            final_cover = os.path.join(tmp, 'Cover', 'JM211899-作品A.jpg')
            self.assertEqual(result.found_dirs, 1)
            self.assertEqual(result.repaired_pdfs, 1)
            self.assertEqual(result.removed_dirs, 1)
            self.assertEqual(result.failed, 0)
            self.assertEqual(result.synced_count, 1)
            self.assertTrue(os.path.exists(final_pdf))
            self.assertGreater(os.path.getsize(final_pdf), 0)
            self.assertTrue(os.path.exists(final_cover))
            self.assertFalse(os.path.exists(album_dir))

            db = ShelfDatabase(db_path)
            db.open()
            try:
                records = db.query_albums('211899')
            finally:
                db.close()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].pdf_path, final_pdf)

    def test_repair_library_skips_album_dir_when_pdf_already_exists(self):
        from PIL import Image
        from jmcomic_shelf.repair_service import repair_library

        with TemporaryDirectory() as tmp:
            author_dir = os.path.join(tmp, '作者A')
            album_dir = os.path.join(author_dir, 'JM211899-作品A')
            chapter_dir = os.path.join(album_dir, '第1章')
            os.makedirs(chapter_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(chapter_dir, '00001.jpg'))
            final_pdf = os.path.join(author_dir, 'JM211899-作品A.pdf')
            with open(final_pdf, 'wb') as f:
                f.write(b'%PDF-1.4\n')

            result = repair_library(tmp, os.path.join(tmp, 'app', 'shelf.db'))

            self.assertEqual(result.found_dirs, 1)
            self.assertEqual(result.repaired_pdfs, 0)
            self.assertEqual(result.removed_dirs, 0)
            self.assertEqual(result.failed, 0)
            self.assertTrue(os.path.exists(album_dir))
            self.assertTrue(os.path.exists(final_pdf))

    def test_repair_library_keeps_image_dir_when_pdf_generation_fails(self):
        from PIL import Image
        from jmcomic_shelf.repair_service import repair_library

        with TemporaryDirectory() as tmp:
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A')
            chapter_dir = os.path.join(album_dir, '第1章')
            os.makedirs(chapter_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(chapter_dir, '00001.jpg'))

            with patch('jmcomic_shelf.repair_service._convert_images_to_pdf', side_effect=RuntimeError('broken pdf')):
                result = repair_library(tmp, os.path.join(tmp, 'app', 'shelf.db'))

            final_pdf = os.path.join(tmp, '作者A', 'JM211899-作品A.pdf')
            self.assertEqual(result.found_dirs, 1)
            self.assertEqual(result.repaired_pdfs, 0)
            self.assertEqual(result.removed_dirs, 0)
            self.assertEqual(result.failed, 1)
            self.assertTrue(os.path.exists(album_dir))
            self.assertFalse(os.path.exists(final_pdf))
            self.assertIn('broken pdf', result.entries[0].message)
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_repair_service -v
```

Expected: FAIL or ERROR because `jmcomic_shelf.repair_service` does not exist.

## Task 2: 修复服务实现

**Files:**
- Create: `src/jmcomic_shelf/repair_service.py`
- Test: `tests/test_jmcomic/test_shelf_repair_service.py`

- [ ] **Step 1: Implement focused repair service**

Create `src/jmcomic_shelf/repair_service.py`:

```python
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
    if path_exists(final_pdf):
        return entry

    images = _image_paths(album_dir)
    if not images:
        entry.status = 'skipped'
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
```

- [ ] **Step 2: Run service tests and verify GREEN**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_repair_service -v
```

Expected: all 3 tests pass.

## Task 3: UI 和导航红绿测试

**Files:**
- Modify: `tests/test_jmcomic/test_shelf_library_page.py`
- Create later: `src/jmcomic_shelf/ui/repair_page.py`
- Modify later: `src/jmcomic_shelf/ui/main_window.py`

- [ ] **Step 1: Add failing UI tests**

Append to `TestShelfLibraryPage` in `tests/test_jmcomic/test_shelf_library_page.py`:

```python
    def test_main_window_adds_library_repair_page_before_settings(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        window = MainWindow()

        self.assertTrue(hasattr(window, 'repair_page'))
        self.assertEqual(window.repair_page.objectName(), 'repairPage')
        self.assertLess(
            window.stackedWidget.indexOf(window.repair_page),
            window.stackedWidget.indexOf(window.settings_page),
        )
        window.close()
        self.assertIsNotNone(app)

    def test_repair_page_primary_button_uses_large_fluent_primary_button(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from qfluentwidgets import PrimaryPushButton
        from jmcomic_shelf.ui.repair_page import RepairPage

        app = QApplication.instance() or QApplication([])
        page = RepairPage()

        self.assertIsInstance(page.repair_button, PrimaryPushButton)
        self.assertEqual(page.repair_button.text(), '开始修复')
        self.assertGreaterEqual(page.repair_button.minimumWidth(), 160)
        self.assertGreaterEqual(page.repair_button.minimumHeight(), 44)
        self.assertIsNotNone(app)
```

- [ ] **Step 2: Run UI tests and verify RED**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_library_page.TestShelfLibraryPage.test_main_window_adds_library_repair_page_before_settings tests.test_jmcomic.test_shelf_library_page.TestShelfLibraryPage.test_repair_page_primary_button_uses_large_fluent_primary_button -v
```

Expected: FAIL or ERROR because `RepairPage` and `window.repair_page` do not exist.

## Task 4: RepairPage 实现和主窗口接入

**Files:**
- Create: `src/jmcomic_shelf/ui/repair_page.py`
- Modify: `src/jmcomic_shelf/ui/main_window.py`
- Test: `tests/test_jmcomic/test_shelf_library_page.py`

- [ ] **Step 1: Create RepairPage**

Create `src/jmcomic_shelf/ui/repair_page.py`:

```python
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, CaptionLabel, PrimaryPushButton, SmoothScrollArea, SubtitleLabel, TitleLabel

from jmcomic_shelf.paths import get_cover_cache_dir, get_database_path, get_settings_path
from jmcomic_shelf.repair_service import LibraryRepairResult, repair_library
from jmcomic_shelf.settings import ShelfSettings

from .styles import TRANSPARENT_SCROLL_STYLE, apply_page_style


class RepairWorker(QObject):
    finished = Signal(object, str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    @Slot()
    def run(self):
        try:
            result = repair_library(
                self.settings.download_dir,
                get_database_path(self.settings.app_data_dir),
                get_cover_cache_dir(self.settings.app_data_dir),
            )
            self.finished.emit(result, '')
        except Exception as exc:
            self.finished.emit(LibraryRepairResult(), str(exc))


class RepairPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('repairPage')
        self.thread = None
        self.worker = None
        self.last_result = LibraryRepairResult()
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        layout.addWidget(TitleLabel('书库修复', self))
        note = CaptionLabel(
            '扫描当前下载目录，补全缺失 PDF；PDF 生成成功后清理残留图片目录，并同步 SQLite 与 catalog.md。',
            self,
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        action_card = CardWidget(self)
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(18, 16, 18, 16)
        action_layout.setSpacing(10)
        action_layout.addWidget(SubtitleLabel('一键修复书库', action_card))
        desc = BodyLabel('适用于封面能显示但点击无响应、作者目录下残留 JM 作品图片文件夹、手动删除漫画后数量不一致等情况。', action_card)
        desc.setWordWrap(True)
        action_layout.addWidget(desc)
        button_row = QHBoxLayout()
        self.repair_button = PrimaryPushButton('开始修复', action_card)
        self.repair_button.setMinimumSize(160, 44)
        self.repair_button.clicked.connect(self.start_repair)
        button_row.addWidget(self.repair_button)
        button_row.addStretch(1)
        action_layout.addLayout(button_row)
        layout.addWidget(action_card)

        self.summary_host = QWidget(self)
        self.summary_layout = QGridLayout(self.summary_host)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        self.summary_layout.setHorizontalSpacing(10)
        self.summary_layout.setVerticalSpacing(10)
        self.summary_labels = {}
        for index, key_title in enumerate([
            ('found_dirs', '发现残留目录'),
            ('repaired_pdfs', '补全 PDF'),
            ('removed_dirs', '清理目录'),
            ('failed', '失败'),
            ('synced_count', '同步后数量'),
        ]):
            key, title = key_title
            card, value_label = self._summary_card(title)
            self.summary_labels[key] = value_label
            self.summary_layout.addWidget(card, index // 3, index % 3)
        layout.addWidget(self.summary_host)

        self.status = CaptionLabel('尚未运行修复。', self)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.log_scroll = SmoothScrollArea(self)
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setFrameShape(self.log_scroll.Shape.NoFrame)
        self.log_scroll.setStyleSheet(TRANSPARENT_SCROLL_STYLE)
        self.log_content = QWidget(self.log_scroll)
        self.log_content.setStyleSheet('background: transparent;')
        self.log_layout = QVBoxLayout(self.log_content)
        self.log_layout.setContentsMargins(0, 0, 14, 0)
        self.log_layout.setSpacing(8)
        self.log_scroll.setWidget(self.log_content)
        layout.addWidget(self.log_scroll, 1)
        self.render_result(self.last_result)

    def _summary_card(self, title: str):
        card = CardWidget(self.summary_host)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        value = SubtitleLabel('0', card)
        caption = CaptionLabel(title, card)
        layout.addWidget(value)
        layout.addWidget(caption)
        return card, value

    def start_repair(self):
        if self.thread and self.thread.isRunning():
            return
        settings = ShelfSettings.load(get_settings_path())
        self.repair_button.setEnabled(False)
        self.status.setText('正在修复书库，请稍候...')
        self.thread = QThread(self)
        self.worker = RepairWorker(settings)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_repair_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_worker)
        self.thread.start()

    @Slot(object, str)
    def on_repair_finished(self, result, error: str):
        self.repair_button.setEnabled(True)
        if error:
            self.status.setText(error)
            return
        self.last_result = result
        self.status.setText(
            f'修复完成：补全 {result.repaired_pdfs} 本，失败 {result.failed} 本，同步后 {result.synced_count} 本。'
        )
        self.render_result(result)

    @Slot()
    def clear_worker(self):
        self.thread = None
        self.worker = None

    def render_result(self, result):
        for key, label in self.summary_labels.items():
            label.setText(str(getattr(result, key)))
        self._clear_log()
        if not result.entries:
            self.log_layout.addWidget(CaptionLabel('尚未运行修复。', self.log_content))
            self.log_layout.addStretch(1)
            return
        for entry in result.entries[:80]:
            text = f'JM{entry.jm_id} {entry.title}：{entry.message}'
            label = BodyLabel(text, self.log_content)
            label.setWordWrap(True)
            self.log_layout.addWidget(label)
        self.log_layout.addStretch(1)

    def _clear_log(self):
        while self.log_layout.count():
            item = self.log_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
```

- [ ] **Step 2: Register page in MainWindow**

Modify `src/jmcomic_shelf/ui/main_window.py`:

```python
from .repair_page import RepairPage
```

In `__init__`, instantiate after detail page:

```python
self.repair_page = RepairPage(self)
```

Set object name:

```python
self.repair_page.setObjectName('repairPage')
```

Register between detail page and settings page:

```python
self.addSubInterface(self.repair_page, FluentIcon.SYNC, '书库修复')
```

Update theme loop:

```python
for page in (self.library_page, self.download_page, self.detail_page, self.repair_page, self.settings_page):
    apply_page_style(page)
```

- [ ] **Step 3: Run UI tests and verify GREEN**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_library_page.TestShelfLibraryPage.test_main_window_adds_library_repair_page_before_settings tests.test_jmcomic.test_shelf_library_page.TestShelfLibraryPage.test_repair_page_primary_button_uses_large_fluent_primary_button -v
```

Expected: both tests pass.

## Task 5: 文档同步

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `.agents/skills/jmcomic-shelf-project/SKILL.md`
- Modify: `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- Modify: `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- Modify: `TASKS.md`

- [ ] **Step 1: Update README**

Find the desktop app feature list and add one bullet describing:

```markdown
- 提供“书库修复”入口，可一键补全历史残留图片目录缺失的 PDF，成功后清理图片目录，并同步 SQLite 与 `catalog.md`。
```

- [ ] **Step 2: Update AGENTS.md**

Add the repair workflow to desktop UI or index rules:

```markdown
- 书库修复页用于处理历史残留的 `作者 / JM{Aid}-{Atitle} / 第{Pindex}章 / 图片` 目录：只有 PDF 生成成功后才删除原图片目录，并在修复结束后复用重建索引同步 SQLite 与 `catalog.md`。
```

- [ ] **Step 3: Update project skill**

In `.agents/skills/jmcomic-shelf-project/SKILL.md`, add `repair_service.py` and `ui/repair_page.py` to desktop modules and record the same success-before-delete rule.

- [ ] **Step 4: Update existing spec and plan**

In `docs/superpowers/specs/2026-06-17-desktop-app-design.md`, add a “书库修复” page section.

In `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`, add a task note under library/index stability or a new repair section.

- [ ] **Step 5: Mark TASKS progress**

Update completed items in `TASKS.md`; do not clear the task until verification passes.

## Task 6: Full verification and maintenance

**Files:**
- Modify: `development-log.md`
- Modify: `TASKS.md`

- [ ] **Step 1: Run focused and full tests**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_repair_service -v
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v
```

Expected: repair service tests pass, then all shelf tests pass.

- [ ] **Step 2: Run py_compile**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\repair_service.py src\jmcomic_shelf\database.py src\jmcomic_shelf\delete_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\repair_page.py
```

Expected: exit code 0.

- [ ] **Step 3: Write development log**

Add a top entry to `development-log.md` with:

- 修改范围：新增书库修复页和服务。
- 涉及文件：all touched files.
- 具体内容：PDF 补全、成功后清理、失败保留、索引同步、UI 样式约束。
- 验证情况：list exact commands and results.
- 明确：本次为日常功能更新，未更新项目版本号，也未发布 Release。

- [ ] **Step 4: Clear TASKS when done**

Set `TASKS.md` back to:

```markdown
# JMComic Shelf 当前任务

本文件用于在对话中断、上下文压缩或新开对话后继续未完成工作。开始任何需要修改代码、脚本或文档的任务时，先在这里记录目标和拆分步骤；每完成一步就更新状态。全部任务完成、验证通过并准备交付后，清空本次任务，只保留“暂无进行中任务”。

暂无进行中任务。
```

- [ ] **Step 5: Run final safety checks**

Run:

```powershell
git diff --check
git check-ignore -v jmcomic-option.yml
git status --short
```

Expected:

- `git diff --check` has no whitespace errors.
- `jmcomic-option.yml` is ignored by `.gitignore`.
- `git status --short` only shows intended files before staging.

- [ ] **Step 6: Commit and push**

Run:

```powershell
git add README.md AGENTS.md TASKS.md development-log.md docs/superpowers/specs/2026-06-17-desktop-app-design.md docs/superpowers/specs/2026-06-21-library-repair-design.md docs/superpowers/plans/2026-06-18-desktop-app-v1.md docs/superpowers/plans/2026-06-21-library-repair.md .agents/skills/jmcomic-shelf-project/SKILL.md src/jmcomic_shelf/repair_service.py src/jmcomic_shelf/ui/repair_page.py src/jmcomic_shelf/ui/main_window.py tests/test_jmcomic/test_shelf_repair_service.py tests/test_jmcomic/test_shelf_library_page.py
git commit -m "feat: add library repair page"
git push origin master
```

Expected: commit succeeds and push updates `origin/master`.

## Self-Review

- Spec coverage: plan covers navigation style, large primary button, service scan, PDF generation, success-before-delete cleanup, failure preservation, index/catalog sync, docs, tests and verification.
- Placeholder scan: no `TBD` or deferred implementation language is present.
- Type consistency: `LibraryRepairResult`, `LibraryRepairEntry`, `repair_library()`, `RepairPage`, `RepairWorker`, and `repair_button` names are consistent across tests and implementation tasks.
