from test_jmcomic import *


class TestShelfDetailService(unittest.TestCase):

    def test_fetch_album_detail_requires_option_path(self):
        from jmcomic_shelf.detail_service import fetch_album_detail

        with self.assertRaisesRegex(ValueError, '请先在设置里选择配置文件'):
            fetch_album_detail('', '211899')

    def test_detail_page_enter_key_triggers_query(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from unittest.mock import patch

        from PySide6.QtWidgets import QApplication

        from jmcomic_shelf.settings import ShelfSettings
        from jmcomic_shelf.ui.detail_page import DetailPage

        class Album:
            album_id = '211899'
            name = '作品A'
            authors = ['作者A']
            tags = []
            episode_list = []

        app = QApplication.instance() or QApplication([])
        page = DetailPage()
        page.input.setText('211899')

        with patch('jmcomic_shelf.ui.detail_page.ShelfSettings.load', return_value=ShelfSettings(option_path='option.yml')):
            with patch.object(page, '_sync_index'):
                with patch('jmcomic_shelf.ui.detail_page.fetch_album_detail', return_value=Album()) as fetch:
                    page.input.returnPressed.emit()

        fetch.assert_called_once()
        self.assertIsNotNone(app)

    def test_detail_page_shows_searching_state_while_query_runs(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from unittest.mock import patch

        from PySide6.QtWidgets import QApplication

        from jmcomic_shelf.settings import ShelfSettings
        from jmcomic_shelf.ui.detail_page import DetailPage

        class Album:
            album_id = '211899'
            name = '作品A'
            authors = ['作者A']
            tags = []
            episode_list = []

        app = QApplication.instance() or QApplication([])
        page = DetailPage()
        page.input.setText('211899')

        def fake_fetch(option_path, jm_id):
            self.assertIn('正在搜索', page.info.text())
            self.assertFalse(page.query_button.isEnabled())
            return Album()

        with patch('jmcomic_shelf.ui.detail_page.ShelfSettings.load', return_value=ShelfSettings(option_path='option.yml')):
            with patch.object(page, '_sync_index'):
                with patch('jmcomic_shelf.ui.detail_page.fetch_album_detail', side_effect=fake_fetch):
                    page.load_detail()

        self.assertTrue(page.query_button.isEnabled())
        self.assertIn('标题：作品A', page.info.text())
        self.assertIsNotNone(app)
