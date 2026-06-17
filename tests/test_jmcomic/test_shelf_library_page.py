from test_jmcomic import *
from tempfile import TemporaryDirectory
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

    def test_library_page_activation_reload_skips_download_dir_scan(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.settings import ShelfSettings
        from jmcomic_shelf.ui.library_page import LibraryPage

        app = QApplication.instance() or QApplication([])
        page = LibraryPage()

        with TemporaryDirectory() as tmp:
            settings = ShelfSettings(download_dir=tmp, app_data_dir=os.path.join(tmp, 'app'))
            with patch('jmcomic_shelf.ui.library_page.ShelfSettings.load', return_value=settings):
                with patch('jmcomic_shelf.ui.library_page.rebuild_index_from_download_dir') as rebuild:
                    with patch.object(page, 'start_background_sync') as start_background_sync:
                        page.reload_for_activation()

        rebuild.assert_not_called()
        start_background_sync.assert_called_once()
        self.assertIsNotNone(app)

    def test_main_window_uses_lightweight_library_activation_reload(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        window = MainWindow()

        with patch.object(window.library_page, 'reload') as full_reload:
            with patch.object(window.library_page, 'reload_for_activation') as activation_reload:
                window.reload_current_page()

        activation_reload.assert_called_once()
        full_reload.assert_not_called()
        window.close()
        self.assertIsNotNone(app)
