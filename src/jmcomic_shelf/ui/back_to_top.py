"""固定在书库视口右下角的返回顶部按钮。"""

from math import atan2, degrees

from PySide6.QtCore import QEvent, QEasingCurve, QPoint, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QConicalGradient, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient, QRegion
from PySide6.QtWidgets import QAbstractButton, QWidget
from qfluentwidgets import isDarkTheme


class BackToTopButton(QAbstractButton):
    def __init__(self, scroll):
        viewport = scroll.viewport()
        super().__init__(viewport)
        self.scroll = scroll
        self.light_angle = 125.0
        self.setMouseTracking(True)
        self.setFixedSize(48, 48)
        self.setAccessibleName('返回顶部')
        self.setToolTip('返回顶部')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.hover_amount = 0.0
        self.hover_animation = QVariantAnimation(self)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.hover_animation.valueChanged.connect(self._set_hover_amount)

        viewport.installEventFilter(self)
        bar = scroll.verticalScrollBar()
        bar.valueChanged.connect(self._update_visibility)
        self.clicked.connect(lambda: scroll.delegate.vScrollBar.scrollTo(bar.minimum()))
        self._position()
        self._update_visibility(bar.value())

    def _position(self):
        viewport = self.parentWidget()
        self.move(max(0, viewport.width() - self.width() - 12),
                  max(0, viewport.height() - self.height() - 8))

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Resize:
            self._position()
        return super().eventFilter(obj, event)

    def _update_visibility(self, value):
        self.setVisible(value > 0)
        if value > 0:
            self.raise_()

    def enterEvent(self, event):
        self._animate_hover(1.0)
        super().enterEvent(event)

    def mouseMoveEvent(self, event):
        offset = event.position() - QRectF(self.rect()).center()
        if offset.manhattanLength() > 3:
            self.light_angle = degrees(atan2(-offset.y(), offset.x()))
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def _animate_hover(self, target):
        self.hover_animation.stop()
        self.hover_animation.setStartValue(self.hover_amount)
        self.hover_animation.setEndValue(target)
        self.hover_animation.setDuration(round(160 * abs(target - self.hover_amount)))
        self.hover_animation.start()

    def _set_hover_amount(self, value):
        self.hover_amount = value
        self.update()

    def _sample_content(self):
        # 只绘制按钮下方的区域。空白处保留透明，避免把系统底色画进玻璃。
        content = self.scroll.widget()
        region = self.rect().translated(content.mapFrom(self.parentWidget(), self.pos()))
        if not content.rect().contains(region):
            return None
        ratio = self.devicePixelRatioF()
        sample = QPixmap(self.size() * ratio)
        sample.setDevicePixelRatio(ratio)
        sample.fill(Qt.GlobalColor.transparent)
        content.render(sample, QPoint(), QRegion(region), QWidget.RenderFlag.DrawChildren)
        return sample

    def paintEvent(self, event):
        dark = isDarkTheme()
        hover = self.hover_amount
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = 4 - hover + int(self.isDown())
        face = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        sample = self._sample_content()
        outline = QPainterPath()
        outline.addEllipse(face)
        painter.setPen(Qt.PenStyle.NoPen)
        shadow_center = face.center() + QPointF(0, 1)
        shadow = QRadialGradient(shadow_center, face.width() / 2 + 3)
        shadow.setColorAt(0.82, Qt.GlobalColor.transparent)
        shadow.setColorAt(0.94, QColor(0, 0, 0, 40))
        shadow.setColorAt(1, Qt.GlobalColor.transparent)
        painter.fillRect(self.rect(), shadow)

        # 中心直接透出原画面；只在弯曲的边缘逐层改变取样比例。
        if sample and not sample.isNull():
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            for depth in range(3):
                outer = face.adjusted(depth, depth, -depth, -depth)
                ring = QPainterPath()
                ring.addEllipse(outer)
                ring.addEllipse(outer.adjusted(1, 1, -1, -1))
                painter.save()
                painter.setClipPath(ring)
                spread = (3 - depth) * (1.35 + 0.45 * hover)
                target = QRectF(self.rect()).adjusted(-spread, -spread, spread, spread)
                painter.drawPixmap(target, sample, QRectF(sample.rect()))
                painter.restore()

            # 下方有实体内容时按实际明暗选择箭头颜色。
            tone = sample.toImage().scaled(1, 1, Qt.AspectRatioMode.IgnoreAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation).pixelColor(0, 0)
            if tone.alpha() > 180:
                dark = tone.lightnessF() < 0.48

        angle = 125 + hover * ((self.light_angle - 125 + 180) % 360 - 180)
        rim = QConicalGradient(face.center(), angle)
        for stop, color in ((0, QColor(255, 255, 255, 235)), (.22, QColor(130, 130, 130, 30)),
                            (.36, QColor(0, 0, 0, 70)), (.51, QColor(255, 255, 255, 185)),
                            (.73, QColor(0, 0, 0, 62)), (1, QColor(255, 255, 255, 235))):
            rim.setColorAt(stop, color)
        painter.fillPath(outline, QColor(255, 255, 255, round(5 + 6 * hover)))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(rim, 1.65 + 0.35 * hover))
        painter.drawEllipse(face)
        if self.hasFocus():
            painter.setPen(QPen(QColor(255, 255, 255, 150) if dark else QColor(0, 0, 0, 110), 1))
            painter.drawEllipse(face.adjusted(-2, -2, 2, 2))

        center = face.center() + QPointF(0, -2 * hover + int(self.isDown()))
        arrow = QPainterPath()
        arrow.moveTo(center + QPointF(0, 7))
        arrow.lineTo(center + QPointF(0, -7))
        arrow.moveTo(center + QPointF(-6, -1))
        arrow.lineTo(center + QPointF(0, -7))
        arrow.lineTo(center + QPointF(6, -1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor('#fafafa' if dark else '#303030'), 2.25)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(arrow)
