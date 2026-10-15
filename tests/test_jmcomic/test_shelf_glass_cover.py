from test_jmcomic import *
from tempfile import TemporaryDirectory


def _distance_to_center(point, center):
    return ((point.x() - center.x()) ** 2 + (point.y() - center.y()) ** 2) ** 0.5


def _non_transparent_pixels(image, step=4):
    count = 0
    for x in range(0, image.width(), step):
        for y in range(0, image.height(), step):
            if image.pixelColor(x, y).alpha() > 0:
                count += 1
    return count


class TestShelfGlassCover(unittest.TestCase):

    def _view(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.glass_cover import GlassCoverView

        app = QApplication.instance() or QApplication([])
        view = GlassCoverView()
        return app, view

    def test_pointer_presses_the_corner_under_the_cursor(self):
        app, view = self._view()
        rect = view.cover_rect()
        center = rect.center()
        flat_top_left = _distance_to_center(rect.topLeft(), center)
        flat_bottom_right = _distance_to_center(rect.bottomRight(), center)

        view.set_pointer(-1.0, -1.0, animated=False)
        quad = view.dip_quad()

        self.assertLess(_distance_to_center(quad[0], center), flat_top_left)
        self.assertGreater(_distance_to_center(quad[2], center), flat_bottom_right)
        self.assertIsNotNone(app)

    def test_opposite_corner_presses_when_pointer_moves(self):
        app, view = self._view()
        rect = view.cover_rect()
        center = rect.center()
        flat_bottom_right = _distance_to_center(rect.bottomRight(), center)
        flat_top_left = _distance_to_center(rect.topLeft(), center)

        view.set_pointer(1.0, 1.0, animated=False)
        quad = view.dip_quad()

        self.assertLess(_distance_to_center(quad[2], center), flat_bottom_right)
        self.assertGreater(_distance_to_center(quad[0], center), flat_top_left)
        self.assertIsNotNone(app)

    def test_pointer_is_clamped_to_unit_range(self):
        app, view = self._view()

        view.set_pointer(4.0, -9.0, animated=False)

        self.assertEqual(view.pointer().x(), 1.0)
        self.assertEqual(view.pointer().y(), -1.0)
        self.assertIsNotNone(app)

    def test_hover_animation_end_values_and_durations(self):
        app, view = self._view()
        from PySide6.QtCore import QPointF

        view.hover_in()
        self.assertEqual(view.hover_animation.endValue(), 1.0)
        self.assertEqual(view.hover_animation.duration(), 160)

        view.set_pointer(-1.0, -1.0, animated=False)
        view.hover_out()
        self.assertEqual(view.hover_animation.endValue(), 0.0)
        self.assertEqual(view.hover_animation.duration(), 220)
        self.assertEqual(view.tilt_animation.endValue(), QPointF(0.0, 0.0))
        self.assertIsNotNone(app)

    def test_hover_lift_grows_the_tile(self):
        app, view = self._view()
        rect = view.cover_rect()

        view.set_pointer(0.0, 0.0, animated=False)
        flat = view.dip_quad()
        view.hoverProgress = 1.0
        lifted = view.dip_quad()

        self.assertGreater(_distance_to_center(lifted[0], rect.center()), _distance_to_center(flat[0], rect.center()))
        self.assertIsNotNone(app)

    def test_render_produces_visible_pixels_and_responds_to_tilt(self):
        app, view = self._view()

        idle = view.grab().toImage()
        view.hoverProgress = 1.0
        view.set_pointer(-1.0, -1.0, animated=False)
        tilted = view.grab().toImage()

        self.assertFalse(idle.isNull())
        self.assertTrue(idle.hasAlphaChannel())
        self.assertGreater(_non_transparent_pixels(idle), 0)
        self.assertNotEqual(bytes(idle.constBits()), bytes(tilted.constBits()))
        self.assertIsNotNone(app)

    def test_missing_cover_falls_back_to_placeholder(self):
        app, view = self._view()

        with TemporaryDirectory() as tmp:
            view.set_cover_path(os.path.join(tmp, 'missing.png'))

        self.assertFalse(view.has_cover())
        self.assertGreater(_non_transparent_pixels(view.grab().toImage()), 0)
        self.assertIsNotNone(app)

    def test_existing_cover_is_loaded_and_scaled(self):
        app, view = self._view()
        from PySide6.QtGui import QColor, QPixmap
        from jmcomic_shelf.ui.glass_cover import COVER_HEIGHT, COVER_WIDTH

        with TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'cover.png')
            pixmap = QPixmap(300, 420)
            pixmap.fill(QColor('#00c8d7'))
            self.assertTrue(pixmap.save(path))

            view.set_cover_path(path)

        self.assertTrue(view.has_cover())
        self.assertLessEqual(view._cover.width(), COVER_WIDTH)
        self.assertLessEqual(view._cover.height(), COVER_HEIGHT)
        self.assertIsNotNone(app)

    def test_cover_card_uses_glass_view_inside_card_width(self):
        app, view = self._view()
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.ui.glass_cover import COVER_HEIGHT, COVER_WIDTH, TILE_PADDING
        from jmcomic_shelf.ui.library_page import CoverCard

        card = CoverCard(AlbumRecord('211899', '作品A'))

        self.assertIsInstance(card.cover, type(view))
        self.assertEqual(card.cover.width(), COVER_WIDTH + TILE_PADDING * 2)
        self.assertEqual(card.cover.height(), COVER_HEIGHT + TILE_PADDING * 2)
        self.assertLessEqual(card.cover.width(), CoverCard.card_width)
        self.assertEqual(card.caption.text(), 'JM211899 作品A')
        self.assertIsNotNone(app)

    def test_caption_stays_flat_and_selectable_while_cover_is_hovered(self):
        app, view = self._view()
        from PySide6.QtCore import Qt
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.ui.library_page import CoverCard

        card = CoverCard(AlbumRecord('211899', '作品A'))
        card.show()
        app.processEvents()
        original_style = card.caption.styleSheet()
        idle_caption = card.caption.grab().toImage()

        card.cover.hoverProgress = 1.0
        card.cover.set_pointer(-1.0, -1.0, animated=False)
        app.processEvents()
        hovered_caption = card.caption.grab().toImage()

        selectable = Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        self.assertEqual(card.caption.textInteractionFlags(), selectable)
        self.assertEqual(card.caption.styleSheet(), original_style)
        self.assertFalse(card.caption.isHidden())
        self.assertEqual(bytes(idle_caption.constBits()), bytes(hovered_caption.constBits()))
        self.assertIsNotNone(app)

    def test_card_keeps_cover_tilt_without_touching_caption(self):
        app, view = self._view()
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.ui.library_page import CoverCard

        card = CoverCard(AlbumRecord('211899', '作品A'))
        card.show()
        app.processEvents()
        idle_cover = card.cover.grab().toImage()

        card.cover.hoverProgress = 1.0
        card.cover.set_pointer(-1.0, -1.0, animated=False)
        app.processEvents()
        hovered_cover = card.cover.grab().toImage()

        self.assertNotEqual(bytes(idle_cover.constBits()), bytes(hovered_cover.constBits()))
        self.assertIsNotNone(app)

    def test_cover_card_paints_no_background_frame(self):
        app, view = self._view()
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.ui.library_page import COVER_CARD_STYLE, CoverCard

        card = CoverCard(AlbumRecord('211899', '作品A'))
        card.show()
        app.processEvents()
        image = card.grab().toImage()

        self.assertIn('background: transparent', COVER_CARD_STYLE)
        self.assertIn('border: none', COVER_CARD_STYLE)
        for point in (
            (card.width() // 2, 1),
            (1, card.height() // 2),
            (card.width() - 2, card.height() // 2),
            (card.width() // 2, card.height() - 2),
        ):
            self.assertEqual(image.pixelColor(*point).alpha(), 0, point)
        self.assertIsNotNone(app)

    def test_selected_card_draws_accent_border_instead_of_frame(self):
        app, view = self._view()
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.ui.library_page import CoverCard

        card = CoverCard(AlbumRecord('211899', '作品A'))
        card.show()
        app.processEvents()

        card.set_selected(True)
        app.processEvents()
        selected = card.grab().toImage()

        color = selected.pixelColor(1, card.height() // 2)
        self.assertGreaterEqual(color.green(), 150)
        self.assertGreaterEqual(color.blue(), 150)

        card.set_selected(False)
        app.processEvents()
        self.assertEqual(card.grab().toImage().pixelColor(1, card.height() // 2).alpha(), 0)
        self.assertIsNotNone(app)
