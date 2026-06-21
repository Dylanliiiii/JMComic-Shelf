from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    CaptionLabel,
    PrimaryPushButton,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
)

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
        desc = BodyLabel(
            '适用于封面能显示但点击无响应、作者目录下残留 JM 作品图片文件夹、手动删除漫画后数量不一致等情况。',
            action_card,
        )
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
        self.summary_host.setStyleSheet('background: transparent;')
        self.summary_layout = QGridLayout(self.summary_host)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)
        self.summary_layout.setHorizontalSpacing(10)
        self.summary_layout.setVerticalSpacing(10)
        self.summary_labels = {}
        for index, (key, title) in enumerate([
            ('found_dirs', '发现残留目录'),
            ('repaired_pdfs', '补全 PDF'),
            ('removed_dirs', '清理目录'),
            ('failed', '失败'),
            ('synced_count', '同步后数量'),
        ]):
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
