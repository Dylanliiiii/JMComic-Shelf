"""书库封面瓦片的液态玻璃与透视倾斜绘制。

本模块只负责把一张封面图渲染成带玻璃质感的瓦片，并在鼠标悬停时按指针
位置做透视倾斜。它不读取书库数据、不处理点击、右键菜单和选中逻辑，
这些仍由 `CoverCard` 负责。
"""

import math
import os

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QPointF,
    QPropertyAnimation,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import QWidget
from qfluentwidgets import isDarkTheme

COVER_WIDTH = 150
COVER_HEIGHT = 210
TILE_PADDING = 9
TILE_RADIUS = 8.0

MAX_TILT_DEGREES = 6.0
EYE_DISTANCE = 240.0
HOVER_LIFT = 0.03
TILT_DIRECTION = 1.0
TILT_Y_DIRECTION = 1.0

SHADOW_BLUR = 14.0
SHADOW_ALPHA_DARK = 96
SHADOW_ALPHA_LIGHT = 52
SHADOW_OFFSET = 2.0
SHADOW_HOVER_OFFSET = 3.0
SHADOW_MIN_OPACITY = 0.55

HOVER_IN_DURATION = 160
HOVER_OUT_DURATION = 220
TILT_DURATION = 140
HOVER_EASING = QEasingCurve.Type.OutCubic
TILT_EASING = QEasingCurve.Type.OutQuad

ACCENT = QColor(0, 200, 215)


def dip_quad(rect: QRectF, pointer: QPointF, hover: float) -> QPolygonF:
    """把矩形平面按指针位置做透视投影，返回左上、右上、右下、左下四个角点。

    近指针的一角向屏幕内侧下压，对角微微抬起；`hover` 控制整体放大。
    """
    center = rect.center()
    half_w = rect.width() / 2.0
    half_h = rect.height() / 2.0
    angle_x = math.radians(pointer.x() * TILT_DIRECTION * MAX_TILT_DEGREES)
    angle_y = math.radians(-pointer.y() * TILT_DIRECTION * TILT_Y_DIRECTION * MAX_TILT_DEGREES)
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    lift = 1.0 + HOVER_LIFT * hover

    points = []
    for sign_x, sign_y in ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0)):
        x = sign_x * half_w
        y = sign_y * half_h
        rotated_x = x * cos_x
        rotated_z = -x * sin_x
        projected_y = y * cos_y - rotated_z * sin_y
        projected_z = y * sin_y + rotated_z * cos_y
        perspective = EYE_DISTANCE / (EYE_DISTANCE - projected_z)
        points.append(
            QPointF(
                center.x() + rotated_x * perspective * lift,
                center.y() + projected_y * perspective * lift,
            )
        )
    return QPolygonF(points)


def perspective_transform(rect: QRectF, pointer: QPointF, hover: float) -> QTransform:
    """返回把 `rect` 平面映射到透视变形后四角点的单应变换。"""
    source = QPolygonF([rect.topLeft(), rect.topRight(), rect.bottomRight(), rect.bottomLeft()])
    transform = QTransform()
    QTransform.quadToQuad(source, dip_quad(rect, pointer, hover), transform)
    return transform


class GlassCoverView(QWidget):
    """把封面渲染成可随鼠标做透视倾斜的液态玻璃瓦片。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(COVER_WIDTH + TILE_PADDING * 2, COVER_HEIGHT + TILE_PADDING * 2)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._cover = None
        self._placeholder = '无封面'
        self._cache = None
        self._cache_key = None
        self._shadow_cache = None
        self._shadow_key = None
        self._hover = 0.0
        self._pointer = QPointF(0.0, 0.0)

        self.hover_animation = QPropertyAnimation(self, b'hoverProgress', self)
        self.hover_animation.setEasingCurve(HOVER_EASING)

        self.tilt_animation = QVariantAnimation(self)
        self.tilt_animation.setDuration(TILT_DURATION)
        self.tilt_animation.setEasingCurve(TILT_EASING)
        self.tilt_animation.valueChanged.connect(self._apply_pointer)

    # ---------- 对外接口 ----------

    def set_cover_path(self, path):
        """载入封面图；路径无效时退回占位文案。"""
        pixmap = None
        if path and os.path.exists(path):
            loaded = QPixmap(path)
            if not loaded.isNull():
                pixmap = loaded.scaled(
                    QSize(COVER_WIDTH, COVER_HEIGHT),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
        self._cover = pixmap
        self._cache = None
        self.update()

    def set_placeholder(self, text: str):
        self._placeholder = text
        self._cache = None
        self.update()

    def has_cover(self) -> bool:
        return self._cover is not None

    def hover_progress(self) -> float:
        return self._hover

    def pointer(self) -> QPointF:
        return QPointF(self._pointer)

    def set_pointer(self, x: float, y: float, animated: bool = True, duration: int = TILT_DURATION):
        """设置归一化指针位置，x/y 取值 -1..1，超出自动裁剪。"""
        target = QPointF(
            max(-1.0, min(1.0, float(x))),
            max(-1.0, min(1.0, float(y))),
        )
        self.tilt_animation.stop()
        if not animated or duration <= 0:
            self._apply_pointer(target)
            return
        self.tilt_animation.setDuration(duration)
        self.tilt_animation.setStartValue(QPointF(self._pointer))
        self.tilt_animation.setEndValue(target)
        self.tilt_animation.start()

    def hover_in(self):
        self._animate_hover(1.0, HOVER_IN_DURATION)

    def hover_out(self):
        self._animate_hover(0.0, HOVER_OUT_DURATION)
        self.set_pointer(0.0, 0.0, animated=True, duration=HOVER_OUT_DURATION)

    def cover_rect(self) -> QRectF:
        return QRectF(TILE_PADDING, TILE_PADDING, COVER_WIDTH, COVER_HEIGHT)

    def dip_quad(self) -> QPolygonF:
        """返回当前透视变形后的四角坐标（左上、右上、右下、左下）。"""
        return dip_quad(self.cover_rect(), self._pointer, self._hover)

    def view_transform(self) -> QTransform:
        """返回当前透视变换，供同一张卡片上的其它图层复用。"""
        return perspective_transform(self.cover_rect(), self._pointer, self._hover)

    # ---------- Qt 属性与事件 ----------

    def _get_hover_progress(self) -> float:
        return self._hover

    def _set_hover_progress(self, value: float):
        self._hover = float(value)
        self.update()

    hoverProgress = Property(float, _get_hover_progress, _set_hover_progress)

    def enterEvent(self, event):
        self.hover_in()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_out()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        position = event.position()
        rect = self.cover_rect()
        half_w = rect.width() / 2.0
        half_h = rect.height() / 2.0
        self.set_pointer(
            (position.x() - rect.center().x()) / half_w,
            (position.y() - rect.center().y()) / half_h,
        )
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        rect = self.cover_rect()
        painter.save()
        painter.setTransform(self.view_transform())
        self._draw_shadow(painter, rect)
        painter.drawPixmap(rect.topLeft(), self._cover_layer())
        self._draw_glass(painter, rect)
        painter.restore()
        painter.end()

    # ---------- 内部实现 ----------

    def _animate_hover(self, target: float, duration: int):
        self.hover_animation.stop()
        self.hover_animation.setDuration(duration)
        self.hover_animation.setStartValue(self._hover)
        self.hover_animation.setEndValue(float(target))
        self.hover_animation.start()

    def _apply_pointer(self, value):
        self._pointer = QPointF(value)
        self.update()

    def _rounded_path(self, rect: QRectF, radius: float) -> QPainterPath:
        path = QPainterPath()
        inset = rect.adjusted(0.75, 0.75, -0.75, -0.75)
        path.addRoundedRect(inset, radius, radius)
        return path

    def _cover_logical_size(self) -> QSize:
        if self._cover is None:
            return QSize(0, 0)
        ratio = self._cover.devicePixelRatio() or 1.0
        return QSize(
            int(round(self._cover.width() / ratio)),
            int(round(self._cover.height() / ratio)),
        )

    def _cover_layer(self) -> QPixmap:
        """缓存封面图层（圆角裁切 + 占位文案），玻璃叠层在悬停时实时绘制。"""
        dark = isDarkTheme()
        ratio = self.devicePixelRatioF() or 1.0
        key = (id(self._cover), self._cover is not None, dark, round(ratio, 2), self._placeholder)
        if self._cache is not None and self._cache_key == key:
            return self._cache

        rect = self.cover_rect()
        pixmap = QPixmap(int(rect.width() * ratio), int(rect.height() * ratio))
        pixmap.setDevicePixelRatio(ratio)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        local = QRectF(0.0, 0.0, rect.width(), rect.height())
        path = self._rounded_path(local, TILE_RADIUS)

        if self._cover is not None:
            size = self._cover_logical_size()
            offset = QPointF(
                local.left() + (local.width() - size.width()) / 2.0,
                local.top() + (local.height() - size.height()) / 2.0,
            )
            painter.save()
            painter.setClipPath(path)
            painter.drawPixmap(offset, self._cover)
            painter.restore()
        else:
            painter.setPen(QColor(232, 228, 230, 210) if dark else QColor(92, 82, 88))
            painter.drawText(local, Qt.AlignmentFlag.AlignCenter, self._placeholder)
        painter.end()

        self._cache = pixmap
        self._cache_key = key
        return pixmap

    def _glass_gradient(self, rect: QRectF, dark: bool, opacity: float) -> QLinearGradient:
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        if dark:
            stops = ((0.0, 46), (0.45, 16), (1.0, 8))
        else:
            stops = ((0.0, 150), (0.5, 70), (1.0, 36))
        for position, alpha in stops:
            gradient.setColorAt(position, QColor(255, 255, 255, int(alpha * opacity)))
        return gradient

    def _edge_gradient(self, rect: QRectF, dark: bool, opacity: float) -> QLinearGradient:
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if dark:
            stops = ((0.0, 96), (0.5, 30), (1.0, 0))
        else:
            stops = ((0.0, 190), (0.5, 110), (1.0, 0))
        for position, alpha in stops:
            gradient.setColorAt(position, QColor(255, 255, 255, int(alpha * opacity)))
        return gradient

    def _draw_glass(self, painter: QPainter, rect: QRectF):
        hover = max(0.0, min(1.0, self._hover))
        if hover <= 0.001:
            return
        dark = isDarkTheme()
        path = self._rounded_path(rect, TILE_RADIUS)
        painter.fillPath(path, self._glass_gradient(rect, dark, hover))

        center = QPointF(
            rect.left() + rect.width() * (self._pointer.x() + 1.0) / 2.0,
            rect.top() + rect.height() * (self._pointer.y() + 1.0) / 2.0,
        )
        radius = max(rect.width(), rect.height()) * 0.95
        highlight = 78 if dark else 120
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0.0, QColor(255, 255, 255, int(highlight * hover)))
        glow.setColorAt(0.45, QColor(255, 255, 255, int(highlight * 0.28 * hover)))
        glow.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.save()
        painter.setClipPath(path)
        painter.fillPath(path, glow)
        painter.restore()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QBrush(self._edge_gradient(rect, dark, hover)), 1.0))
        painter.drawPath(path)
        rim = QColor(ACCENT)
        rim.setAlpha(int(110 * hover))
        painter.setPen(QPen(rim, 1.4))
        painter.drawPath(path)

    def _shadow_pixmap(self) -> QPixmap:
        """缓存模糊后的瓦片剪影，用作柔和投影；用模糊而不是描边，避免出现硬边灰线。"""
        ratio = self.devicePixelRatioF() or 1.0
        dark = isDarkTheme()
        key = (dark, round(ratio, 2))
        if self._shadow_cache is not None and self._shadow_key == key:
            return self._shadow_cache

        rect = self.cover_rect()
        margin = SHADOW_BLUR
        width = max(1, int((rect.width() + margin * 2) * ratio))
        height = max(1, int((rect.height() + margin * 2) * ratio))
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, SHADOW_ALPHA_DARK if dark else SHADOW_ALPHA_LIGHT))
        painter.drawRoundedRect(
            QRectF(
                margin * ratio,
                margin * ratio,
                rect.width() * ratio,
                rect.height() * ratio,
            ),
            TILE_RADIUS * ratio,
            TILE_RADIUS * ratio,
        )
        painter.end()

        small = image.scaled(
            max(1, width // 6),
            max(1, height // 6),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        blurred = small.scaled(
            width,
            height,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        pixmap = QPixmap.fromImage(blurred)
        pixmap.setDevicePixelRatio(ratio)
        self._shadow_cache = pixmap
        self._shadow_key = key
        return pixmap

    def _draw_shadow(self, painter: QPainter, rect: QRectF):
        """在瓦片轮廓之外绘制柔和投影，瓦片内部不参与，避免封面留白处被压暗。"""
        margin = SHADOW_BLUR
        clip = QPainterPath()
        clip.addRect(rect.adjusted(-margin * 2, -margin * 2, margin * 2, margin * 2))
        clip = clip.subtracted(self._rounded_path(rect, TILE_RADIUS))

        hover = max(0.0, min(1.0, self._hover))
        painter.save()
        painter.setClipPath(clip, Qt.ClipOperation.ReplaceClip)
        painter.setOpacity(SHADOW_MIN_OPACITY + (1.0 - SHADOW_MIN_OPACITY) * hover)
        painter.translate(0.0, SHADOW_OFFSET + SHADOW_HOVER_OFFSET * hover)
        painter.drawPixmap(
            QPointF(rect.left() - margin, rect.top() - margin),
            self._shadow_pixmap(),
        )
        painter.restore()
