from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import PrimaryPushButton, PushButton, StrongBodyLabel, TextEdit

from jmcomic_shelf.download_service import DownloadService, DownloadTask, parse_album_ids
from jmcomic_shelf.paths import get_settings_path
from jmcomic_shelf.settings import ShelfSettings


class DownloadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        header = QHBoxLayout()
        header.addWidget(StrongBodyLabel('下载'))
        header.addStretch(1)
        self.start_button = PrimaryPushButton('开始下载')
        self.start_button.clicked.connect(self.start_download)
        header.addWidget(self.start_button)

        self.input = TextEdit()
        self.input.setPlaceholderText('输入一个或多个 JM 号，可用空格、逗号或换行分隔')
        self.input.setFixedHeight(120)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['JM号', '状态', '错误', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout.addLayout(header)
        layout.addWidget(self.input)
        layout.addWidget(self.table, 1)

    def start_download(self):
        self.tasks = [DownloadTask(jm_id=jm_id) for jm_id in parse_album_ids(self.input.toPlainText())]
        self.render_tasks()
        for task in self.tasks:
            self.run_task(task)

    def retry_task(self, task: DownloadTask):
        task.mark_waiting()
        self.render_tasks()
        self.run_task(task)

    def run_task(self, task: DownloadTask):
        settings = ShelfSettings.load(get_settings_path())
        service = DownloadService(settings.option_path)
        service.run_task(task)
        self.render_tasks()

    def render_tasks(self):
        self.table.setRowCount(len(self.tasks))
        for row, task in enumerate(self.tasks):
            self.table.setItem(row, 0, QTableWidgetItem(f'JM{task.jm_id}'))
            self.table.setItem(row, 1, QTableWidgetItem(task.status))
            self.table.setItem(row, 2, QTableWidgetItem(task.error))
            if task.status == 'failed':
                retry = PushButton('重试')
                retry.clicked.connect(lambda checked=False, current=task: self.retry_task(current))
                self.table.setCellWidget(row, 3, retry)
            else:
                self.table.setCellWidget(row, 3, QWidget())
