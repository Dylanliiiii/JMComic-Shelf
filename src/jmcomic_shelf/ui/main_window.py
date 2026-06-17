from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition, Theme, setTheme, setThemeColor

from .detail_page import DetailPage
from .download_page import DownloadPage
from .library_page import LibraryPage
from .settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)
        setThemeColor('#00c8d7')
        self.setWindowTitle('JMComic Shelf')
        self.resize(1100, 720)
        self.setFont(QFont(self.font().family(), 11))
        self.setMicaEffectEnabled(True)

        self.library_page = LibraryPage(self)
        self.download_page = DownloadPage(self)
        self.detail_page = DetailPage(self)
        self.settings_page = SettingsPage(self)

        self.library_page.setObjectName('libraryPage')
        self.download_page.setObjectName('downloadPage')
        self.detail_page.setObjectName('detailPage')
        self.settings_page.setObjectName('settingsPage')

        self.addSubInterface(self.library_page, FluentIcon.LIBRARY, '书库')
        self.addSubInterface(self.download_page, FluentIcon.DOWNLOAD, '下载')
        self.addSubInterface(self.detail_page, FluentIcon.INFO, '查看详情')
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
        self.stackedWidget.setStyleSheet(
            'QStackedWidget {'
            '  background: #241b1f;'
            '  border: 1px solid #34282c;'
            '  border-radius: 8px;'
            '}'
        )
        self.stackedWidget.currentChanged.connect(self.reload_current_page)

    def reload_current_page(self):
        widget = self.stackedWidget.currentWidget()
        reload = getattr(widget, 'reload', None)
        if callable(reload):
            reload()
