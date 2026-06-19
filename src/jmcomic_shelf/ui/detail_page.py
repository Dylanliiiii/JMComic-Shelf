import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, LineEdit, PrimaryPushButton, PushButton, TitleLabel

from jmcomic_shelf.database import ShelfDatabase
from jmcomic_shelf.detail_service import fetch_album_detail_result
from jmcomic_shelf.file_actions import open_pdf, reveal_in_explorer
from jmcomic_shelf.index_service import rebuild_index_from_download_dir, record_from_album
from jmcomic_shelf.paths import get_cover_cache_dir, get_database_path, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import apply_page_style


class DetailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('detailPage')
        self.local_record = None
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        layout.addWidget(TitleLabel('禁漫预览', self))

        header = QHBoxLayout()
        self.input = LineEdit(self)
        self.input.setPlaceholderText('输入 JM 号')
        self.input.returnPressed.connect(self.load_detail)
        self.query_button = PrimaryPushButton('查看详情', self)
        self.query_button.clicked.connect(self.load_detail)
        header.addWidget(self.input, 1)
        header.addWidget(self.query_button)

        self.cover = QLabel(self)
        self.cover.setFixedSize(220, 300)
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setStyleSheet('background: transparent; border-radius: 6px;')
        self.cover.hide()

        self.info = QLabel('尚未查询', self)
        self.info.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.info.setWordWrap(True)
        self.info.setStyleSheet('background: transparent;')

        note = BodyLabel('查询单个 JM 号的线上详情；如果书库索引里已有本地 PDF，可直接打开或定位文件。', self)
        note.setWordWrap(True)

        actions = QHBoxLayout()
        self.open_button = PushButton('打开 PDF', self)
        self.reveal_button = PushButton('在文件资源管理器中显示位置', self)
        self.open_button.clicked.connect(self.open_local_pdf)
        self.reveal_button.clicked.connect(self.reveal_local_pdf)
        actions.addWidget(self.open_button)
        actions.addWidget(self.reveal_button)
        actions.addStretch(1)

        layout.addLayout(header)
        layout.addWidget(note)
        layout.addWidget(self.cover, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.info, 1)
        layout.addLayout(actions)
        self.update_actions()

    def load_detail(self):
        jm_id = self.input.text().strip().removeprefix('JM').removeprefix('jm')
        if not jm_id:
            self.info.setText('请输入 JM 号。')
            return

        self.query_button.setEnabled(False)
        self.input.setEnabled(False)
        self.set_cover('')
        self.info.setText(f'正在搜索中：JM{jm_id} ...')
        QApplication.processEvents()
        try:
            settings = ShelfSettings.load(get_settings_path())
            self._sync_index(settings)
            self.local_record = self.find_local_record(jm_id, settings.app_data_dir)
            local_cover_path = self.local_record.cover_path if self.local_record else ''
            result = fetch_album_detail_result(
                settings.option_path,
                jm_id,
                get_cover_cache_dir(settings.app_data_dir),
                local_cover_path,
            )
            album = result.album
            record = record_from_album(album)
            self.set_cover(result.cover_path)
            self.info.setText(
                f'标题：{record.title}\n'
                f'JM号：JM{record.jm_id}\n'
                f'作者：{", ".join(record.authors)}\n'
                f'标签：{", ".join(record.tags)}\n'
                f'章节：{len(record.chapters)}\n'
                f'链接：{record.link}'
            )
        except Exception as e:
            self.local_record = None
            self.info.setText(str(e))
        finally:
            self.query_button.setEnabled(True)
            self.input.setEnabled(True)
            self.update_actions()

    def _sync_index(self, settings):
        if settings.download_dir:
            rebuild_index_from_download_dir(
                settings.download_dir,
                get_database_path(settings.app_data_dir),
                get_cover_cache_dir(settings.app_data_dir),
            )

    def find_local_record(self, jm_id: str, app_data_dir: str = ''):
        db = ShelfDatabase(get_database_path(app_data_dir))
        db.open()
        try:
            records = db.query_albums(jm_id)
        finally:
            db.close()
        return records[0] if records else None

    def update_actions(self):
        available = bool(self.local_record and self.local_record.pdf_path)
        self.open_button.setEnabled(available)
        self.reveal_button.setEnabled(available)

    def set_cover(self, cover_path: str):
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    QSize(220, 300),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.cover.setPixmap(scaled)
                self.cover.show()
                return

        self.cover.clear()
        self.cover.hide()

    def open_local_pdf(self):
        if self.local_record:
            open_pdf(self.local_record.pdf_path)

    def reveal_local_pdf(self):
        if self.local_record:
            reveal_in_explorer(self.local_record.pdf_path)
