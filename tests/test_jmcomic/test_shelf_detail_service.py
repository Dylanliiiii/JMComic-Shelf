from test_jmcomic import *


class TestShelfDetailService(unittest.TestCase):

    def test_fetch_album_detail_requires_option_path(self):
        from jmcomic_shelf.detail_service import fetch_album_detail

        with self.assertRaisesRegex(ValueError, '请先在设置里选择配置文件'):
            fetch_album_detail('', '211899')

    def test_fetch_album_detail_result_prefers_local_cover(self):
        import tempfile

        from PIL import Image

        from jmcomic_shelf.detail_service import fetch_album_detail_result

        class Album:
            album_id = '211899'

        class Client:
            def __init__(self):
                self.download_cover_called = False

            def get_album_detail(self, jm_id):
                return Album()

            def download_album_cover(self, jm_id, save_path):
                self.download_cover_called = True

        class Option:
            def __init__(self, client):
                self.client = client

            def build_jm_client(self):
                return self.client

        with tempfile.TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'option.yml')
            local_cover = os.path.join(tmp, 'local.jpg')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write('dir_rule: {}\n')
            Image.new('RGB', (40, 60), 'red').save(local_cover)
            client = Client()

            result = fetch_album_detail_result(
                option_path,
                '211899',
                os.path.join(tmp, 'covers'),
                local_cover,
                option_factory=lambda _path: Option(client),
            )

        self.assertEqual(result.cover_path, local_cover)
        self.assertFalse(client.download_cover_called)

    def test_fetch_album_detail_result_caches_online_cover(self):
        import tempfile

        from PIL import Image

        from jmcomic_shelf.detail_service import fetch_album_detail_result

        class Album:
            album_id = '211899'

        class Client:
            def get_album_detail(self, jm_id):
                return Album()

            def download_album_cover(self, jm_id, save_path):
                Image.new('RGB', (40, 60), 'blue').save(save_path)

        class Option:
            def build_jm_client(self):
                return Client()

        with tempfile.TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'option.yml')
            cover_cache_dir = os.path.join(tmp, 'covers')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write('dir_rule: {}\n')

            result = fetch_album_detail_result(
                option_path,
                '211899',
                cover_cache_dir,
                option_factory=lambda _path: Option(),
            )

            self.assertEqual(result.cover_path, os.path.join(cover_cache_dir, 'JM211899.jpg'))
            self.assertTrue(os.path.exists(result.cover_path))

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

        from jmcomic_shelf.detail_service import DetailResult

        with patch('jmcomic_shelf.ui.detail_page.ShelfSettings.load', return_value=ShelfSettings(option_path='option.yml')):
            with patch.object(page, '_sync_index'):
                with patch.object(page, 'find_local_record', return_value=None):
                    with patch('jmcomic_shelf.ui.detail_page.fetch_album_detail_result', return_value=DetailResult(Album())) as fetch:
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

        from jmcomic_shelf.detail_service import DetailResult

        with patch('jmcomic_shelf.ui.detail_page.ShelfSettings.load', return_value=ShelfSettings(option_path='option.yml')):
            with patch.object(page, '_sync_index'):
                with patch.object(page, 'find_local_record', return_value=None):
                    with patch('jmcomic_shelf.ui.detail_page.fetch_album_detail_result', side_effect=lambda *args: DetailResult(fake_fetch(*args[:2]))):
                        page.load_detail()

        self.assertTrue(page.query_button.isEnabled())
        self.assertIn('标题：作品A', page.info.text())
        self.assertIsNotNone(app)

    def test_detail_page_shows_cover_above_detail_text(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        import tempfile
        from unittest.mock import patch

        from PIL import Image
        from PySide6.QtWidgets import QApplication

        from jmcomic_shelf.detail_service import DetailResult
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

        with tempfile.TemporaryDirectory() as tmp:
            cover_path = os.path.join(tmp, 'cover.jpg')
            Image.new('RGB', (80, 120), 'green').save(cover_path)
            settings = ShelfSettings(option_path='option.yml', app_data_dir=tmp)

            with patch('jmcomic_shelf.ui.detail_page.ShelfSettings.load', return_value=settings):
                with patch.object(page, '_sync_index'):
                    with patch.object(page, 'find_local_record', return_value=None):
                        with patch(
                            'jmcomic_shelf.ui.detail_page.fetch_album_detail_result',
                            return_value=DetailResult(Album(), cover_path),
                        ):
                            page.load_detail()

        self.assertFalse(page.cover.isHidden())
        self.assertIsNotNone(page.cover.pixmap())
        self.assertIn('标题：作品A', page.info.text())
        self.assertIsNotNone(app)
