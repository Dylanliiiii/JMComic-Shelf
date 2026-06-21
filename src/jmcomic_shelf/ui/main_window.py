from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition, isDarkTheme

from jmcomic_shelf.paths import get_app_icon_path, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import apply_page_style, prepare_table
from .theme import apply_app_theme
from .detail_page import DetailPage
from .download_page import DownloadPage
from .library_page import LibraryPage
from .repair_page import RepairPage
from .settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.settings = ShelfSettings.load(get_settings_path())
        self.setWindowTitle('JMComic Shelf')
        self.setWindowIcon(QIcon(get_app_icon_path()))
        self.resize(1100, 720)
        self.setFont(QFont(self.font().family(), 11))
        self.setMicaEffectEnabled(True)

        self.library_page = LibraryPage(self)
        self.download_page = DownloadPage(self)
        self.detail_page = DetailPage(self)
        self.repair_page = RepairPage(self)
        self.settings_page = SettingsPage(self)
        self.settings_page.theme_changed.connect(self.apply_theme_mode)
        self.download_page.downloads_finished.connect(self.library_page.reload_for_activation)

        self.library_page.setObjectName('libraryPage')
        self.download_page.setObjectName('downloadPage')
        self.detail_page.setObjectName('detailPage')
        self.repair_page.setObjectName('repairPage')
        self.settings_page.setObjectName('settingsPage')

        self.addSubInterface(self.library_page, FluentIcon.LIBRARY, '本地书库')
        self.addSubInterface(self.download_page, FluentIcon.DOWNLOAD, '禁漫下载')
        self.addSubInterface(self.detail_page, FluentIcon.INFO, '禁漫预览')
        self.addSubInterface(self.repair_page, FluentIcon.SYNC, '书库修复')
        self.addSubInterface(
            self.settings_page,
            FluentIcon.SETTING,
            '设置',
            NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setExpandWidth(180)
        self.navigationInterface.expand(useAni=False)
        self.stackedWidget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.stackedWidget.setContentsMargins(24, 18, 24, 24)
        self.refresh_theme_styles()
        self.stackedWidget.currentChanged.connect(self.reload_current_page)

    def reload_current_page(self):
        widget = self.stackedWidget.currentWidget()
        reload = getattr(widget, 'reload_for_activation', None)
        if not callable(reload):
            reload = getattr(widget, 'reload', None)
        if callable(reload):
            reload()

    def apply_theme_mode(self, theme_mode: str):
        apply_app_theme(theme_mode)
        self.refresh_theme_styles()

    def refresh_theme_styles(self):
        if isDarkTheme():
            background = '#241b1f'
            border = '#34282c'
        else:
            background = '#fffafb'
            border = '#eadfe3'
        self.stackedWidget.setStyleSheet(
            'QStackedWidget {'
            f'  background: {background};'
            f'  border: 1px solid {border};'
            '  border-radius: 8px;'
            '}'
        )
        for page in (self.library_page, self.download_page, self.detail_page, self.repair_page, self.settings_page):
            apply_page_style(page)
        prepare_table(self.download_page.table)
