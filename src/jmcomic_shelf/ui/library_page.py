import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFontMetrics, QPixmap
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QMenu, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, CaptionLabel, LineEdit, Pivot, SmoothScrollArea, SubtitleLabel, TitleLabel

from jmcomic_shelf.database import ShelfDatabase
from jmcomic_shelf.file_actions import open_pdf, reveal_in_explorer
from jmcomic_shelf.index_service import group_by_author, rebuild_index_from_download_dir
from jmcomic_shelf.paths import get_cover_cache_dir, get_database_path, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import TRANSPARENT_SCROLL_STYLE, apply_page_style


class CoverCard(CardWidget):
    cover_width = 150

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedWidth(178)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.cover = QLabel(self)
        self.cover.setFixedSize(self.cover_width, 210)
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setStyleSheet('border-radius: 6px;')
        self._load_cover()

        caption = f'JM{record.jm_id} {record.title}'
        metrics = QFontMetrics(self.font())
        self.caption = CaptionLabel(metrics.elidedText(caption, Qt.TextElideMode.ElideRight, self.cover_width), self)
        self.caption.setFixedWidth(self.cover_width)
        self.caption.setToolTip(caption)

        layout.addWidget(self.cover)
        layout.addWidget(self.caption)

    def _load_cover(self):
        if self.record.cover_path and os.path.exists(self.record.cover_path):
            pixmap = QPixmap(self.record.cover_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.cover.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.cover.setPixmap(scaled)
                return
        self.cover.setText('无封面')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.record.pdf_path:
            open_pdf(self.record.pdf_path)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = QAction('打开 PDF', self)
        reveal_action = QAction('在文件资源管理器中显示位置', self)
        open_action.triggered.connect(lambda: open_pdf(self.record.pdf_path))
        reveal_action.triggered.connect(lambda: reveal_in_explorer(self.record.pdf_path))
        exists = bool(self.record.pdf_path and os.path.exists(self.record.pdf_path))
        open_action.setEnabled(exists)
        reveal_action.setEnabled(exists)
        menu.addAction(open_action)
        menu.addAction(reveal_action)
        menu.exec(event.globalPos())


class LibraryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = []
        self.load_error = ''
        self.setObjectName('libraryPage')
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = TitleLabel('书库', self)
        self.search_input = LineEdit(self)
        self.search_input.setPlaceholderText('搜索 JM号 / 作者 / 标签')
        self.search_input.textChanged.connect(self.reload)

        note = CaptionLabel(
            '浏览当前下载目录里的本地漫画；可输入 JM 号、作者或标签筛选，点击封面打开 PDF，右键可定位文件。',
            self,
        )
        note.setWordWrap(True)

        self.filter_pivot = Pivot(self)
        self.filter_pivot.addItem('all', '全部', lambda: self.search_input.clear())
        self.filter_pivot.setCurrentItem('all')

        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(self.scroll.Shape.NoFrame)
        self.scroll.setStyleSheet(TRANSPARENT_SCROLL_STYLE)
        self.content = QWidget(self.scroll)
        self.content.setStyleSheet('background: transparent;')
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 14, 0)
        self.content_layout.setSpacing(16)
        self.scroll.setWidget(self.content)

        layout.addWidget(title)
        layout.addWidget(self.search_input)
        layout.addWidget(note)
        layout.addWidget(self.filter_pivot)
        layout.addWidget(self.scroll, 1)
        self.reload()

    def reload(self):
        query = self.search_input.text().strip()
        settings = ShelfSettings.load(get_settings_path())
        sync_error = ''
        try:
            self._sync_index_from_settings(settings)
        except Exception as e:
            sync_error = str(e)
        db = ShelfDatabase(get_database_path(settings.app_data_dir))
        try:
            db.open()
            self.records = db.query_albums(query)
            self.load_error = sync_error
        except Exception as e:
            self.records = []
            self.load_error = str(e)
        finally:
            db.close()
        self.render_records()

    def _sync_index_from_settings(self, settings):
        if not settings.download_dir:
            return
        rebuild_index_from_download_dir(
            settings.download_dir,
            get_database_path(settings.app_data_dir),
            get_cover_cache_dir(settings.app_data_dir),
        )

    def render_records(self):
        self._clear_content()
        if not self.records:
            self.content_layout.addWidget(self._empty_card())
            self.content_layout.addStretch(1)
            return

        for author, records in group_by_author(self.records).items():
            self.content_layout.addWidget(SubtitleLabel(f'{author} · {len(records)} 本', self.content))
            grid_host = QWidget(self.content)
            grid_host.setStyleSheet('background: transparent;')
            grid = QGridLayout(grid_host)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(12)
            for index, record in enumerate(records):
                grid.addWidget(CoverCard(record, grid_host), index // 5, index % 5)
            self.content_layout.addWidget(grid_host)

        self.content_layout.addStretch(1)

    def _empty_card(self):
        card = QFrame(self.content)
        card.setStyleSheet('QFrame { background: #3a2f32; border: 1px solid #493d41; border-radius: 8px; }')
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        if self.load_error:
            title = SubtitleLabel('无法读取书库索引', card)
            desc = BodyLabel(self.load_error, card)
        else:
            title = SubtitleLabel('暂无内容', card)
            desc = BodyLabel('请先在设置中确认下载目录，或点击“重建索引”扫描现有漫画。', card)
        desc.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(desc)
        return card

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
