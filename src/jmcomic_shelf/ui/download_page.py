from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QHeaderView, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, PrimaryPushButton, ProgressBar, PushButton, TextEdit, TitleLabel

from jmcomic_shelf.download_service import DownloadService, DownloadTask, parse_album_ids
from jmcomic_shelf.paths import get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import apply_page_style, prepare_table


STATUS_TEXT = {
    'waiting': '等待中',
    'running': '下载中',
    'success': '已完成',
    'failed': '失败',
}


class DownloadWorker(QObject):
    task_started = Signal(object, int, int)
    task_finished = Signal(object, int, int)
    all_finished = Signal()

    def __init__(self, tasks, settings):
        super().__init__()
        self.tasks = tasks
        self.settings = settings

    @Slot()
    def run(self):
        total = len(self.tasks)
        service = DownloadService(
            self.settings.option_path,
            app_data_dir=self.settings.app_data_dir,
            download_dir=self.settings.download_dir,
        )
        for index, task in enumerate(self.tasks, start=1):
            task.mark_running()
            self.task_started.emit(task, index, total)
            service.run_task(task)
            self.task_finished.emit(task, index, total)
        self.all_finished.emit()


class DownloadPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('downloadPage')
        self.tasks = []
        self.thread = None
        self.worker = None
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

        self.progress = ProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)

        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(['JM号', '状态', '错误', '操作'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 130)
        prepare_table(self.table)

        self.status = QLabel('', self)
        self.status.setWordWrap(True)

        layout.addLayout(header)
        layout.addWidget(note)
        layout.addWidget(self.input)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        layout.addWidget(self.table, 1)

    def start_download(self):
        if self.is_running():
            self.status.setText('当前下载任务仍在运行，请等待完成后再开始新的任务。')
            return
        self.tasks = [DownloadTask(jm_id=jm_id) for jm_id in parse_album_ids(self.input.toPlainText())]
        if not self.tasks:
            self.status.setText('请输入至少一个 JM 号。')
            return
        self.status.setText(f'已加入 {len(self.tasks)} 个下载任务，准备开始。')
        self.progress.setValue(0)
        self.render_tasks()
        self.run_tasks(self.tasks)

    def retry_task(self, task: DownloadTask):
        if self.is_running():
            self.status.setText('当前下载任务仍在运行，请等待完成后再重试。')
            return
        task.mark_waiting()
        self.render_tasks()
        self.progress.setValue(0)
        self.run_tasks([task])

    def run_tasks(self, tasks):
        settings = ShelfSettings.load(get_settings_path())
        self.start_button.setEnabled(False)
        self.thread = QThread(self)
        self.worker = DownloadWorker(tasks, settings)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.task_started.connect(self.on_task_started)
        self.worker.task_finished.connect(self.on_task_finished)
        self.worker.all_finished.connect(self.on_all_finished)
        self.worker.all_finished.connect(self.thread.quit)
        self.worker.all_finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.clear_worker)
        self.thread.start()

    @Slot(object, int, int)
    def on_task_started(self, task, index, total):
        self.status.setText(f'正在下载 {index}/{total}：JM{task.jm_id}')
        self.render_tasks()

    @Slot(object, int, int)
    def on_task_finished(self, task, index, total):
        percent = int(index / total * 100) if total else 0
        self.progress.setValue(percent)
        if task.status == 'failed':
            self.status.setText(f'JM{task.jm_id} 下载失败：{task.error}')
        else:
            self.status.setText(f'已完成 {index}/{total}：JM{task.jm_id}')
        self.render_tasks()

    @Slot()
    def on_all_finished(self):
        failed_count = sum(1 for task in self.tasks if task.status == 'failed')
        if failed_count:
            self.status.setText(f'下载结束：{failed_count} 个任务失败，其余任务已更新书库索引。')
        else:
            self.status.setText('全部下载完成，已更新书库索引。')
        self.start_button.setEnabled(True)

    @Slot()
    def clear_worker(self):
        self.thread = None
        self.worker = None

    def is_running(self):
        return bool(self.thread and self.thread.isRunning())

    def render_tasks(self):
        self.table.setRowCount(len(self.tasks))
        for row, task in enumerate(self.tasks):
            self.table.setItem(row, 0, QTableWidgetItem(f'JM{task.jm_id}'))
            self.table.setItem(row, 1, QTableWidgetItem(STATUS_TEXT.get(task.status, task.status)))
            self.table.setItem(row, 2, QTableWidgetItem(task.error))
            if task.status == 'failed':
                retry = PushButton('重试', self.table)
                retry.setEnabled(not self.is_running())
                retry.clicked.connect(lambda checked=False, current=task: self.retry_task(current))
                self.table.setCellWidget(row, 3, retry)
            else:
                self.table.setCellWidget(row, 3, QWidget(self.table))
