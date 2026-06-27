from dataclasses import dataclass

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
    CaptionLabel,
    PushButton,
    SmoothScrollArea,
    SubtitleLabel,
    TitleLabel,
)

from .styles import TRANSPARENT_SCROLL_STYLE, apply_page_style


@dataclass(frozen=True)
class OfficialSiteLink:
    label: str
    display: str
    target: str


@dataclass(frozen=True)
class OfficialSiteGroup:
    title: str
    description: str
    links: tuple[OfficialSiteLink, ...]


OFFICIAL_SITE_GROUPS = (
    OfficialSiteGroup('禁漫发布页', '', (
        OfficialSiteLink('', 'https://jmcomicog.net/', 'https://jmcomicog.net/'),
    )),
    OfficialSiteGroup('国际通用域名', '不支持日本/韩国路线', (
        OfficialSiteLink('', '18comic.vip', '18comic.vip'),
        OfficialSiteLink('', '18comic.ink', '18comic.ink'),
    )),
    OfficialSiteGroup('东南亚路线建议使用', '', (
        OfficialSiteLink('', 'jmcomic-zzz.one', 'jmcomic-zzz.one'),
        OfficialSiteLink('', 'http://jmcomic-zzz.org', 'http://jmcomic-zzz.org'),
    )),
    OfficialSiteGroup('大陆域名', '请使用 Chrome 浏览器打开', (
        OfficialSiteLink('大陆域名', 'https://comic18j-codi.cc', 'https://comic18j-codi.cc'),
        OfficialSiteLink('分流1', 'https://comic18j-yodo.club', 'https://comic18j-yodo.club'),
        OfficialSiteLink('分流2', 'https://comic18j-codi.club', 'https://comic18j-codi.club'),
    )),
    OfficialSiteGroup('APP 软件下载安装！！！', '', (
        OfficialSiteLink('', 'http://jm-88.cc/ZNPJam', 'http://jm-88.cc/ZNPJam'),
    )),
    OfficialSiteGroup(
        '联系方式',
        '如果地址无法打开，欢迎发送邮件告知：',
        (
            OfficialSiteLink('邮箱', 're18comic＠gmail.com', 'http://gmail.com'),
            OfficialSiteLink(
                '或是直接到 DC 群或 TG 找管理员处理问题',
                'http://discord.gg/V74p7HM',
                'http://discord.gg/V74p7HM',
            ),
            OfficialSiteLink('Telegram', 'http://t.me/hcomic18', 'http://t.me/hcomic18'),
        ),
    ),
)


class OfficialSitePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('officialSitePage')
        self.link_buttons = {}
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(TitleLabel('禁漫官网', self))

        note = CaptionLabel('点击地址后将在系统默认浏览器中打开；具体可用性可能受地区和网络路线影响。', self)
        note.setWordWrap(True)
        layout.addWidget(note)

        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(self.scroll.Shape.NoFrame)
        self.scroll.setStyleSheet(TRANSPARENT_SCROLL_STYLE)

        content = QWidget(self.scroll)
        content.setStyleSheet('background: transparent;')
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 14, 0)
        content_layout.setSpacing(12)
        for group in OFFICIAL_SITE_GROUPS:
            content_layout.addWidget(self._create_group_card(group, content))
        content_layout.addStretch(1)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll, 1)

        self.status = CaptionLabel('', self)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

    def _create_group_card(self, group: OfficialSiteGroup, parent):
        card = CardWidget(parent)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)
        card_layout.addWidget(SubtitleLabel(group.title, card))
        if group.description:
            description = CaptionLabel(group.description, card)
            description.setWordWrap(True)
            card_layout.addWidget(description)
        for link in group.links:
            row = QHBoxLayout()
            if link.label:
                row.addWidget(BodyLabel(link.label, card))
            else:
                row.addStretch(1)
            button = PushButton(link.display, card)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, target=link.target: self.open_url(target))
            self.link_buttons[link.target] = button
            row.addWidget(button)
            card_layout.addLayout(row)
        return card

    def open_url(self, raw_url: str):
        url = QUrl.fromUserInput(raw_url)
        if not QDesktopServices.openUrl(url):
            self.status.setText(f'无法交给默认浏览器打开：{raw_url}')
            return
        self.status.setText(f'已交给默认浏览器打开：{raw_url}')
