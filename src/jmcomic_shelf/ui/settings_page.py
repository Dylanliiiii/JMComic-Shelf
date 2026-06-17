from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, PushButton, StrongBodyLabel

from jmcomic_shelf.cover_cache import CoverCache
from jmcomic_shelf.option_service import update_option_download_dir
from jmcomic_shelf.paths import get_cover_cache_dir, get_default_app_data_dir, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import apply_page_style


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_path = get_settings_path()
        self.settings = ShelfSettings.load(self.settings_path)
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        title = StrongBodyLabel('设置')
        title.setFont(QFont(self.font().family(), 16, QFont.Bold))
        layout.addWidget(title)
        note = BodyLabel('第一次使用先设置下载目录和 jmcomic-option.yml。下载目录保存漫画/PDF/catalog.md，应用数据目录只保存软件索引和缩略图。')
        note.setWordWrap(True)
        layout.addWidget(note)

        self.download_dir = QLineEdit(self.settings.download_dir)
        self.option_path = QLineEdit(self.settings.option_path)
        self.app_data_dir = QLineEdit(self.settings.app_data_dir or get_default_app_data_dir())
        self.app_data_dir.setReadOnly(True)

        layout.addWidget(self._path_row(
            '下载目录',
            '漫画图片、PDF 和 catalog.md 会保存到这里；这是你真正收藏文件的位置。',
            self.download_dir,
            '选择',
            self.choose_download_dir,
        ))
        layout.addWidget(self._path_row(
            '配置文件',
            '选择项目根目录里的 jmcomic-option.yml；下载账号、插件和路径规则从这里读取。',
            self.option_path,
            '选择',
            self.choose_option_path,
        ))
        layout.addWidget(self._path_row(
            '应用数据目录',
            '软件自己的 settings.json、shelf.db 和封面缩略图缓存，通常不用手动改。',
            self.app_data_dir,
        ))

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

        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def _path_row(self, title, description, editor, button_text=None, slot=None):
        host = QFrame()
        host.setStyleSheet('QFrame { background: #ffffff; border: 1px solid #eee7e7; border-radius: 8px; }')
        outer = QVBoxLayout(host)
        outer.setContentsMargins(14, 12, 14, 12)
        outer.setSpacing(8)
        outer.addWidget(StrongBodyLabel(title))
        desc = BodyLabel(description)
        desc.setWordWrap(True)
        outer.addWidget(desc)
        line = QHBoxLayout()
        line.addWidget(editor, 1)
        if button_text and slot:
            button = PushButton(button_text)
            button.clicked.connect(slot)
            line.addWidget(button)
        outer.addLayout(line)
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
        update_option_download_dir(self.settings.option_path, self.settings.download_dir)
        self.status.setText('设置已保存；如果选择了配置文件，下载目录也已同步到 jmcomic-option.yml。')

    def clear_cache(self):
        count = CoverCache(get_cover_cache_dir(self.app_data_dir.text().strip())).clear()
        self.status.setText(f'已清理 {count} 个封面缩略图')
