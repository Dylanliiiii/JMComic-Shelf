from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, PrimaryPushButton, PushButton, TextEdit, TitleLabel

from jmcomic_shelf.download_service import DownloadService, DownloadTask, parse_album_ids
from jmcomic_shelf.paths import get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import apply_page_style, prepare_table


class DownloadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('downloadPage')
        self.tasks = []
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        header.addWidget(TitleLabel('下载', self))
        header.addStretch(1)
        self.start_button = PrimaryPushButton('开始下载', self)
        self.start_button.clicked.connect(self.start_download)
        header.addWidget(self.start_button)

        note = BodyLabel('先到设置页选择下载目录和 jmcomic-option.yml；这里可一次输入多个 JM 号，失败后可点击重试。', self)
        note.setWordWrap(True)

        self.input = TextEdit(self)
        self.input.setPlaceholderText('输入一个或多个 JM 号，可用空格、逗号或换行分隔')
        self.input.setFixedHeight(120)

        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(['JM号', '状态', '错误', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        prepare_table(self.table)

        self.status = QLabel('', self)
        self.status.setWordWrap(True)

        layout.addLayout(header)
        layout.addWidget(note)
        layout.addWidget(self.input)
        layout.addWidget(self.status)
        layout.addWidget(self.table, 1)

    def start_download(self):
        self.tasks = [DownloadTask(jm_id=jm_id) for jm_id in parse_album_ids(self.input.toPlainText())]
        if not self.tasks:
            self.status.setText('请输入至少一个 JM 号。')
            return
        self.status.setText('')
        self.render_tasks()
        for task in self.tasks:
            self.run_task(task)

    def retry_task(self, task: DownloadTask):
        task.mark_waiting()
        self.render_tasks()
        self.run_task(task)

    def run_task(self, task: DownloadTask):
        settings = ShelfSettings.load(get_settings_path())
        service = DownloadService(
            settings.option_path,
            app_data_dir=settings.app_data_dir,
            download_dir=settings.download_dir,
        )
        service.run_task(task)
        if task.status == 'failed':
            self.status.setText(task.error)
        elif task.status == 'success':
            self.status.setText('下载完成，已更新书库索引。')
        self.render_tasks()

    def render_tasks(self):
        self.table.setRowCount(len(self.tasks))
        for row, task in enumerate(self.tasks):
            self.table.setItem(row, 0, QTableWidgetItem(f'JM{task.jm_id}'))
            self.table.setItem(row, 1, QTableWidgetItem(task.status))
            self.table.setItem(row, 2, QTableWidgetItem(task.error))
            if task.status == 'failed':
                retry = PushButton('重试', self.table)
                retry.clicked.connect(lambda checked=False, current=task: self.retry_task(current))
                self.table.setCellWidget(row, 3, retry)
            else:
                self.table.setCellWidget(row, 3, QWidget(self.table))
