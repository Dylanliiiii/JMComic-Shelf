"""预览结果卡：封面、作品资料和本地操作。"""

from PySide6.QtCore import QEasingCurve, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QBoxLayout, QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel, CaptionLabel, FlowLayout, HyperlinkButton, PushButton,
    SubtitleLabel, isDarkTheme, setCustomStyleSheet,
)

from jmcomic_shelf.file_actions import open_pdf, reveal_in_explorer
from jmcomic_shelf.path_utils import path_exists


# 让链接背景伸入正文左侧的留白，同时保持正文与封面的原始位置。
LINK_PADDING = 8
CARD_MARGIN = 22


class PreviewCard(QWidget):
    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.sweep = QVariantAnimation(self)
        self.sweep.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.sweep.valueChanged.connect(self._set_progress)

        self.row = QBoxLayout(QBoxLayout.Direction.LeftToRight, self)
        self.row.setContentsMargins(CARD_MARGIN - LINK_PADDING, 20, CARD_MARGIN, 20)
        self.row.setSpacing(CARD_MARGIN - LINK_PADDING)
        self.cover = QLabel(self)
        self.cover.setContentsMargins(LINK_PADDING, 0, 0, 0)
        image = QPixmap(record.cover_path) if record.cover_path else QPixmap()
        if not image.isNull():
            self.cover.setPixmap(image.scaled(190, 245, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation))
            self.row.addWidget(self.cover, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        else:
            self.cover.hide()

        column = QVBoxLayout()
        column.setSpacing(8)
        self.row.addLayout(column, 1)
        details = QVBoxLayout()
        details.setContentsMargins(LINK_PADDING, 0, 0, 0)
        details.setSpacing(8)
        column.addLayout(details)
        details.addWidget(CaptionLabel(f'JM{record.jm_id}   ·   共 {len(record.chapters)} 章', self))
        self.title = SubtitleLabel(self)
        self.title.setTextFormat(Qt.TextFormat.PlainText)
        self.title.setText(record.title)
        self.title.setWordWrap(True)
        self.title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        details.addWidget(self.title)
        authors = [a for a in record.authors if a.strip().lower() not in ('', 'n/a', 'default_author')]
        author = BodyLabel(self)
        author.setTextFormat(Qt.TextFormat.PlainText)
        author.setText('作者  ' + '、'.join(authors) if authors else '作者未标注')
        author.setWordWrap(True)
        details.addWidget(author)

        if record.tags:
            tag_host = QWidget(self)
            tags = FlowLayout(tag_host)
            tags.setContentsMargins(0, 3, 0, 3)
            tags.setHorizontalSpacing(6)
            tags.setVerticalSpacing(6)
            for tag in record.tags:
                chip = CaptionLabel(tag_host)
                chip.setTextFormat(Qt.TextFormat.PlainText)
                chip.setText(tag)
                chip.setWordWrap(chip.fontMetrics().horizontalAdvance(tag) > 224)
                chip.setMaximumWidth(240)
                chip.setToolTip(tag)
                chip.setContentsMargins(8, 3, 8, 3)
                setCustomStyleSheet(chip, 'CaptionLabel {background: #f3eef1; border-radius: 5px;}',
                                    'CaptionLabel {background: #45383e; border-radius: 5px;}')
                tags.addWidget(chip)
            details.addWidget(tag_host)

        column.addStretch(1)
        action_host = QWidget(self)
        actions = FlowLayout(action_host)
        actions.setContentsMargins(0 if record.link else LINK_PADDING, 4, 0, 0)
        actions.setHorizontalSpacing(8)
        actions.setVerticalSpacing(6)
        if record.link:
            link = HyperlinkButton(record.link, '查看作品页 ↗', action_host)
            link_style = f'HyperlinkButton[hasIcon=false] {{ padding: 6px {LINK_PADDING}px; }}'
            setCustomStyleSheet(link, link_style, link_style)
            link.setToolTip(record.link)
            actions.addWidget(link)
        if record.pdf_path and path_exists(record.pdf_path):
            for text, action in [('打开 PDF', open_pdf), ('定位文件', reveal_in_explorer)]:
                button = PushButton(text, action_host)
                button.clicked.connect(lambda checked=False, fn=action: fn(record.pdf_path))
                actions.addWidget(button)
        column.addWidget(action_host)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        direction = QBoxLayout.Direction.TopToBottom if self.width() < 560 else QBoxLayout.Direction.LeftToRight
        if self.row.direction() != direction:
            self.row.setDirection(direction)
            self.row.setSpacing(CARD_MARGIN if direction == QBoxLayout.Direction.TopToBottom else CARD_MARGIN - LINK_PADDING)
            self.updateGeometry()

    def enterEvent(self, event):
        self._animate_to(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(0.0)
        super().leaveEvent(event)

    def _animate_to(self, target):
        self.sweep.stop()
        self.sweep.setStartValue(self.progress)
        self.sweep.setEndValue(target)
        self.sweep.setDuration(max(1, round(190 * abs(target - self.progress))))
        self.sweep.start()

    def _set_progress(self, value):
        self.progress = value
        self.update()

    def paintEvent(self, event):
        dark = isDarkTheme()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = 2.5 - 2 * self.progress
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        outline = QPainterPath()
        outline.addRoundedRect(rect, 11, 11)
        painter.fillPath(outline, QColor('#342c30' if dark else '#ffffff'))
        painter.save()
        painter.setClipPath(outline)
        tint = QColor('#00b8c6')
        tint.setAlpha(25 if dark else 16)
        painter.fillRect(QRectF(rect.left(), rect.top(), rect.width() * self.progress, rect.height()), tint)
        painter.restore()
        painter.setPen(QPen(QColor('#51434b' if dark else '#e5dce0'), 1))
        painter.drawPath(outline)
