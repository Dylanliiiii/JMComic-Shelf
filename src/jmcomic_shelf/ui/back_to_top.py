"""固定在书库视口右下角的返回顶部按钮。"""

from PySide6.QtCore import QEvent, QEasingCurve, QPointF, QRectF, Qt, QVariantAnimation
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QAbstractButton
from qfluentwidgets import isDarkTheme


class BackToTopButton(QAbstractButton):
    def __init__(self, scroll):
        viewport = scroll.viewport()
        super().__init__(viewport)
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

    def paintEvent(self, event):
        dark = isDarkTheme()
        hover = self.hover_amount
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = 4 - hover + int(self.isDown())
        face = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(12, 33, 39, 28))
        painter.drawEllipse(face.translated(0, 1.5))
        glass = QLinearGradient(face.topLeft(), face.bottomRight())
        glass.setColorAt(0, QColor(86, 106, 112, 220) if dark else QColor(255, 255, 255, 235))
        glass.setColorAt(0.48, QColor(44, 60, 68, 200) if dark else QColor(243, 253, 255, 210))
        glass.setColorAt(1, QColor(39, 101, 108, 205) if dark else QColor(183, 226, 232, 200))
        painter.setBrush(glass)
        rim = QColor(106, 200, 208, 210) if self.hasFocus() else QColor(91, 158, 166, round(110 + 90 * hover))
        painter.setPen(QPen(rim, 1.5 if self.hasFocus() else 1))
        painter.drawEllipse(face)
        painter.setPen(QPen(QColor(255, 255, 255, round(110 + 115 * hover)), 1.5))
        painter.drawArc(face.adjusted(2, 2, -2, -2), 45 * 16, 105 * 16)

        center = face.center() + QPointF(0, -2 * hover + int(self.isDown()))
        arrow = QPainterPath()
        arrow.moveTo(center + QPointF(0, 7))
        arrow.lineTo(center + QPointF(0, -7))
        arrow.moveTo(center + QPointF(-6, -1))
        arrow.lineTo(center + QPointF(0, -7))
        arrow.lineTo(center + QPointF(6, -1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        pen = QPen(QColor('#e4fdff' if dark else '#205761'), 2.25)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(arrow)
