from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition

from .detail_page import DetailPage
from .download_page import DownloadPage
from .library_page import LibraryPage
from .settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JMComic Shelf')
        self.resize(1100, 720)

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
