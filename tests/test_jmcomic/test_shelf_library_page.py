from test_jmcomic import *
from unittest.mock import patch


class TestShelfLibraryPage(unittest.TestCase):

    def test_library_page_does_not_crash_when_database_is_unavailable(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.library_page import LibraryPage

        app = QApplication.instance() or QApplication([])
        with patch('jmcomic_shelf.ui.library_page.ShelfDatabase.open', side_effect=PermissionError('blocked')):
            page = LibraryPage()

        self.assertEqual(page.records, [])
        self.assertIn('blocked', page.load_error)
        self.assertIsNotNone(app)

    def test_library_page_debounces_resize_render(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtCore import QSize
        from PySide6.QtGui import QResizeEvent
        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.ui.library_page import LibraryPage

        app = QApplication.instance() or QApplication([])
        page = LibraryPage()
        page.records = [AlbumRecord('211899', '作品A')]
        page.current_columns = 999

        with patch.object(page, 'render_records') as render:
            page.resizeEvent(QResizeEvent(QSize(900, 700), QSize(800, 700)))

        render.assert_not_called()
        self.assertTrue(page.resize_render_timer.isActive())
        self.assertIsNotNone(app)
