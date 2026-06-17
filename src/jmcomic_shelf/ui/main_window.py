from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget, QStyle, QVBoxLayout, QWidget

from .detail_page import DetailPage
from .download_page import DownloadPage
from .library_page import LibraryPage
from .settings_page import SettingsPage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JMComic Shelf')
        self.resize(1100, 720)
        self.setFont(QFont(self.font().family(), 11))
        self.setStyleSheet("""
            QWidget {
                background: #fbf7f7;
                color: #1f1f1f;
            }
            QListWidget {
                background: #fbf7f7;
                border: none;
                font-size: 16px;
                outline: none;
            }
            QListWidget::item {
                height: 54px;
                padding-left: 14px;
                border-radius: 8px;
                margin: 3px 8px;
            }
            QListWidget::item:selected {
                background: #eee7e7;
                border-left: 3px solid #00a7b3;
            }
            QListWidget::item:hover {
                background: #f3eeee;
            }
        """)

        self.nav = QListWidget()
        self.nav.setFixedWidth(178)
        self.nav.setSpacing(2)
        self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.stack = QStackedWidget()

        self.pages = [
            ('书库', '浏览本地 PDF', QStyle.SP_DirIcon, LibraryPage(self)),
            ('下载', '输入 JM 号下载', QStyle.SP_ArrowDown, DownloadPage(self)),
            ('查看详情', '查询单本信息', QStyle.SP_MessageBoxInformation, DetailPage(self)),
            ('设置', '配置路径缓存', QStyle.SP_FileDialogDetailedView, SettingsPage(self)),
        ]

        for title, subtitle, icon, page in self.pages:
            item = QListWidgetItem(f'{title}\n{subtitle}')
            item.setIcon(self.style().standardIcon(icon))
            item.setTextAlignment(Qt.AlignVCenter)
            self.nav.addItem(item)
            self.stack.addWidget(page)

        shell = QHBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        nav_host = QWidget()
        nav_layout = QVBoxLayout(nav_host)
        nav_layout.setContentsMargins(8, 16, 0, 8)
        nav_layout.addWidget(self.nav)
        shell.addWidget(nav_host)
        shell.addWidget(self.stack, 1)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
