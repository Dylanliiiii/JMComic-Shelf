from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import LineEdit, PrimaryPushButton, PushButton, StrongBodyLabel

from jmcomic_shelf.database import ShelfDatabase
from jmcomic_shelf.detail_service import fetch_album_detail
from jmcomic_shelf.file_actions import open_pdf, reveal_in_explorer
from jmcomic_shelf.index_service import record_from_album
from jmcomic_shelf.paths import get_database_path, get_settings_path
from jmcomic_shelf.settings import ShelfSettings


class DetailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.local_record = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        header.addWidget(StrongBodyLabel('查看详情'))
        self.input = LineEdit()
        self.input.setPlaceholderText('输入 JM 号')
        self.query_button = PrimaryPushButton('查看详情')
        self.query_button.clicked.connect(self.load_detail)
        header.addWidget(self.input, 1)
        header.addWidget(self.query_button)

        self.info = QLabel('尚未查询')
        self.info.setAlignment(Qt.AlignTop)
        self.info.setWordWrap(True)

        actions = QHBoxLayout()
        self.open_button = PushButton('打开 PDF')
        self.reveal_button = PushButton('在文件资源管理器中显示位置')
        self.open_button.clicked.connect(self.open_local_pdf)
        self.reveal_button.clicked.connect(self.reveal_local_pdf)
        actions.addWidget(self.open_button)
        actions.addWidget(self.reveal_button)
        actions.addStretch(1)

        layout.addLayout(header)
        layout.addWidget(self.info, 1)
        layout.addLayout(actions)
        self.update_actions()

    def load_detail(self):
        jm_id = self.input.text().strip().removeprefix('JM').removeprefix('jm')
        settings = ShelfSettings.load(get_settings_path())
        album = fetch_album_detail(settings.option_path, jm_id)
        record = record_from_album(album)
        self.local_record = self.find_local_record(jm_id)
        self.info.setText(
            f'标题：{record.title}\n'
            f'JM号：JM{record.jm_id}\n'
            f'作者：{", ".join(record.authors)}\n'
            f'标签：{", ".join(record.tags)}\n'
            f'章节：{len(record.chapters)}\n'
            f'链接：{record.link}'
        )
        self.update_actions()

    def find_local_record(self, jm_id: str):
        db = ShelfDatabase(get_database_path())
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

    def open_local_pdf(self):
        if self.local_record:
            open_pdf(self.local_record.pdf_path)

    def reveal_local_pdf(self):
        if self.local_record:
            reveal_in_explorer(self.local_record.pdf_path)
