from PySide6.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, PushButton, StrongBodyLabel

from jmcomic_shelf.cover_cache import CoverCache
from jmcomic_shelf.paths import get_cover_cache_dir, get_default_app_data_dir, get_settings_path
from jmcomic_shelf.settings import ShelfSettings


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_path = get_settings_path()
        self.settings = ShelfSettings.load(self.settings_path)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        layout.addWidget(StrongBodyLabel('设置'))

        form = QFormLayout()
        self.download_dir = QLineEdit(self.settings.download_dir)
        self.option_path = QLineEdit(self.settings.option_path)
        self.app_data_dir = QLineEdit(self.settings.app_data_dir or get_default_app_data_dir())
        self.app_data_dir.setReadOnly(True)

        form.addRow('下载目录', self._with_button(self.download_dir, '选择', self.choose_download_dir))
        form.addRow('配置文件', self._with_button(self.option_path, '选择', self.choose_option_path))
        form.addRow('应用数据目录', self.app_data_dir)

        actions = QHBoxLayout()
        self.save_button = PushButton('保存设置')
        self.clear_cache_button = PushButton('清理封面缓存')
        self.rebuild_button = PushButton('重建索引')
        self.rebuild_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_settings)
        self.clear_cache_button.clicked.connect(self.clear_cache)
        actions.addWidget(self.save_button)
        actions.addWidget(self.clear_cache_button)
        actions.addWidget(self.rebuild_button)
        actions.addStretch(1)

        self.status = BodyLabel('')

        layout.addLayout(form)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def _with_button(self, editor, text, slot):
        host = QWidget()
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        button = PushButton(text)
        button.clicked.connect(slot)
        layout.addWidget(editor, 1)
        layout.addWidget(button)
        return host

    def choose_download_dir(self):
        directory = QFileDialog.getExistingDirectory(self, '选择下载目录', self.download_dir.text())
        if directory:
            self.download_dir.setText(directory)

    def choose_option_path(self):
        filepath, _ = QFileDialog.getOpenFileName(self, '选择 jmcomic-option.yml', self.option_path.text(), 'YAML (*.yml *.yaml)')
        if filepath:
            self.option_path.setText(filepath)

    def save_settings(self):
        self.settings.download_dir = self.download_dir.text().strip()
        self.settings.option_path = self.option_path.text().strip()
        self.settings.app_data_dir = self.app_data_dir.text().strip()
        self.settings.save(self.settings_path)
        self.status.setText('设置已保存')

    def clear_cache(self):
        count = CoverCache(get_cover_cache_dir(self.app_data_dir.text().strip())).clear()
        self.status.setText(f'已清理 {count} 个封面缩略图')
