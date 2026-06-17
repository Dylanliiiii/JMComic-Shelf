from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, CaptionLabel, ComboBox, PushButton, SubtitleLabel, TitleLabel

from jmcomic_shelf.cover_cache import CoverCache
from jmcomic_shelf.index_service import rebuild_index_from_download_dir
from jmcomic_shelf.option_service import update_option_download_dir
from jmcomic_shelf.paths import get_cover_cache_dir, get_database_path, get_default_app_data_dir, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import apply_page_style
from .theme import THEME_LABELS, THEME_VALUES, normalize_theme_mode


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('settingsPage')
        self.settings_path = get_settings_path()
        self.settings = ShelfSettings.load(self.settings_path)
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(TitleLabel('设置', self))
        note = CaptionLabel(
            '第一次使用先设置下载目录和 jmcomic-option.yml。下载目录保存漫画、PDF 和 catalog.md，应用数据目录只保存软件索引和缩略图。',
            self,
        )
        note.setWordWrap(True)
        layout.addWidget(note)

        self.download_dir = QLineEdit(self.settings.download_dir)
        self.option_path = QLineEdit(self.settings.option_path)
        self.app_data_dir = QLineEdit(self.settings.app_data_dir or get_default_app_data_dir())
        self.app_data_dir.setReadOnly(True)
        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(list(THEME_LABELS.values()))
        self.theme_combo.setCurrentText(THEME_LABELS[normalize_theme_mode(self.settings.theme_mode)])
        self.theme_combo.currentTextChanged.connect(self.preview_theme)

        layout.addWidget(self._path_row(
            '下载目录',
            '漫画图片、PDF 和 catalog.md 会保存到这里；书库页会递归扫描这个目录来显示现有作品。',
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
            '软件自己的 settings.json、shelf.db 和封面缩略图缓存，通常不用手动修改。',
            self.app_data_dir,
        ))
        layout.addWidget(self._theme_row())

        actions = QHBoxLayout()
        self.save_button = PushButton('保存设置', self)
        self.clear_cache_button = PushButton('清理封面缓存', self)
        self.rebuild_button = PushButton('重建索引', self)
        self.save_button.clicked.connect(self.save_settings)
        self.clear_cache_button.clicked.connect(self.clear_cache)
        self.rebuild_button.clicked.connect(self.rebuild_index)
        actions.addWidget(self.save_button)
        actions.addWidget(self.clear_cache_button)
        actions.addWidget(self.rebuild_button)
        actions.addStretch(1)

        self.status = BodyLabel('', self)

        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addStretch(1)

    def _path_row(self, title, description, editor, button_text=None, slot=None):
        host = CardWidget(self)
        outer = QVBoxLayout(host)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(8)
        outer.addWidget(SubtitleLabel(title, host))
        desc = CaptionLabel(description, host)
        desc.setWordWrap(True)
        outer.addWidget(desc)
        line = QHBoxLayout()
        line.addWidget(editor, 1)
        if button_text and slot:
            button = PushButton(button_text, host)
            button.clicked.connect(slot)
            line.addWidget(button)
        outer.addLayout(line)
        return host

    def _theme_row(self):
        host = CardWidget(self)
        outer = QVBoxLayout(host)
        outer.setContentsMargins(18, 16, 18, 16)
        outer.setSpacing(8)
        outer.addWidget(SubtitleLabel('外观主题', host))
        desc = CaptionLabel('选择桌面端使用浅色、深色，或跟随系统主题。选择后会立即预览，保存设置后下次启动继续使用。', host)
        desc.setWordWrap(True)
        outer.addWidget(desc)
        line = QHBoxLayout()
        line.addWidget(self.theme_combo)
        line.addStretch(1)
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
        self.settings.theme_mode = self.current_theme_mode()
        self.settings.save(self.settings_path)
        update_option_download_dir(self.settings.option_path, self.settings.download_dir)
        self.status.setText('设置已保存；如果选择了配置文件，下载目录也已同步到 jmcomic-option.yml。')

    def current_theme_mode(self):
        return THEME_VALUES.get(self.theme_combo.currentText(), 'auto')

    def preview_theme(self, *_):
        self.theme_changed.emit(self.current_theme_mode())

    def clear_cache(self):
        count = CoverCache(get_cover_cache_dir(self.app_data_dir.text().strip())).clear()
        self.status.setText(f'已清理 {count} 个封面缩略图。')

    def rebuild_index(self):
        self.save_settings()
        count = rebuild_index_from_download_dir(
            self.settings.download_dir,
            get_database_path(self.settings.app_data_dir),
            get_cover_cache_dir(self.settings.app_data_dir),
        )
        self.status.setText(f'索引已重建：扫描到 {count} 本本地漫画。')
