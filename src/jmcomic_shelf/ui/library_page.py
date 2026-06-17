import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QFontMetrics, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import BodyLabel, LineEdit, Pivot, StrongBodyLabel

from jmcomic_shelf.database import ShelfDatabase
from jmcomic_shelf.file_actions import open_pdf, reveal_in_explorer
from jmcomic_shelf.index_service import group_by_author
from jmcomic_shelf.paths import get_database_path

from .styles import apply_page_style


class CoverCard(QFrame):
    cover_width = 150

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setObjectName('coverCard')
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(178)
        self.setStyleSheet(
            '#coverCard { border: 1px solid #d9d9d9; border-radius: 8px; padding: 8px; }'
            '#coverCard:hover { border-color: #7aa7e8; background: #f7fbff; }'
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.cover = QLabel()
        self.cover.setFixedSize(self.cover_width, 210)
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setStyleSheet('background: #f3f3f3; border-radius: 6px; color: #777;')
        self._load_cover()

        caption = f'JM{record.jm_id} {record.title}'
        metrics = QFontMetrics(self.font())
        self.caption = BodyLabel(metrics.elidedText(caption, Qt.ElideRight, self.cover_width))
        self.caption.setFixedWidth(self.cover_width)
        self.caption.setToolTip(caption)

        layout.addWidget(self.cover)
        layout.addWidget(self.caption)

    def _load_cover(self):
        if self.record.cover_path and os.path.exists(self.record.cover_path):
            pixmap = QPixmap(self.record.cover_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.cover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.cover.setPixmap(scaled)
                return
        self.cover.setText('无封面')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.record.pdf_path:
            open_pdf(self.record.pdf_path)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = QAction('打开 PDF', self)
        reveal_action = QAction('在文件资源管理器中显示位置', self)
        open_action.triggered.connect(lambda: open_pdf(self.record.pdf_path))
        reveal_action.triggered.connect(lambda: reveal_in_explorer(self.record.pdf_path))
        open_action.setEnabled(bool(self.record.pdf_path and os.path.exists(self.record.pdf_path)))
        reveal_action.setEnabled(bool(self.record.pdf_path and os.path.exists(self.record.pdf_path)))
        menu.addAction(open_action)
        menu.addAction(reveal_action)
        menu.exec(event.globalPos())


class LibraryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = []
        self.load_error = ''
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = StrongBodyLabel('书库')
        title.setFont(QFont(self.font().family(), 16, QFont.Bold))
        self.search_input = LineEdit()
        self.search_input.setPlaceholderText('搜索 JM号 / 作者 / 标签')
        self.search_input.textChanged.connect(self.reload)
        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(self.search_input, 1)

        note = BodyLabel('浏览当前下载目录里的本地漫画；可输入 JM 号、作者或标签筛选，点封面打开 PDF，右键可定位文件。')
        note.setWordWrap(True)

        self.filter_pivot = Pivot()
        self.filter_pivot.addItem('all', '全部', lambda: self.search_input.clear())
        self.filter_pivot.setCurrentItem('all')

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        self.scroll.setWidget(self.content)

        layout.addLayout(header)
        layout.addWidget(note)
        layout.addWidget(self.filter_pivot)
        layout.addWidget(self.scroll, 1)
        self.reload()

    def reload(self):
        query = self.search_input.text().strip()
        db = ShelfDatabase(get_database_path())
        try:
            db.open()
            self.records = db.query_albums(query)
            self.load_error = ''
        except Exception as e:
            self.records = []
            self.load_error = str(e)
        finally:
            db.close()
        self.render_records()

    def render_records(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self.records:
            empty = QLabel(f'无法读取书库索引：{self.load_error}' if self.load_error else '暂无内容')
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch(1)
            return

        for author, records in group_by_author(self.records).items():
            self.content_layout.addWidget(StrongBodyLabel(f'{author} · {len(records)} 本'))
            grid_host = QWidget()
            grid = QGridLayout(grid_host)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(12)
            for index, record in enumerate(records):
                grid.addWidget(CoverCard(record), index // 5, index % 5)
            self.content_layout.addWidget(grid_host)

        self.content_layout.addStretch(1)
