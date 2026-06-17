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
