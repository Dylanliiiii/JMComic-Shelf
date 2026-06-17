from PySide6.QtGui import QFont
from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition, Theme, setTheme

from .detail_page import DetailPage
from .download_page import DownloadPage
from .library_page import LibraryPage
from .settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        setTheme(Theme.AUTO)
        self.setWindowTitle('JMComic Shelf')
        self.resize(1100, 720)
        self.setFont(QFont(self.font().family(), 11))
        self.setMicaEffectEnabled(False)
        self.setStyleSheet('MainWindow, FluentWindow, QWidget { background: #fbf7f7; }')

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
        self.navigationInterface.setStyleSheet(
            'NavigationInterface { background: #fbf7f7; }'
            'NavigationPanel { background: #fbf7f7; }'
        )
        self.stackedWidget.currentChanged.connect(self.reload_current_page)

    def reload_current_page(self):
        widget = self.stackedWidget.currentWidget()
        reload = getattr(widget, 'reload', None)
        if callable(reload):
            reload()
