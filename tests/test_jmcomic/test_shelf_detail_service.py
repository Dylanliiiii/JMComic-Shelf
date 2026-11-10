from test_jmcomic import *


class TestShelfDetailService(unittest.TestCase):

    def test_detail_text_follows_app_theme_with_light_system_text(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        from PySide6.QtGui import QColor, QPalette
        from PySide6.QtWidgets import QApplication
        from qfluentwidgets import Theme, qconfig, setTheme
        from jmcomic_shelf.ui.detail_page import DetailPage

        app = QApplication.instance() or QApplication([])
        original_palette = app.palette()
        original_theme = qconfig.theme
        palette = QPalette(original_palette)
        palette.setColor(QPalette.ColorRole.WindowText, QColor('white'))
        app.setPalette(palette)
        page = DetailPage()
        from jmcomic_shelf.models import AlbumRecord
        page._add_card(AlbumRecord('123', '测试作品'))
        title = page.cards.itemAt(0).widget().title
        page.show()
        try:
            for theme, expected in ((Theme.LIGHT, '#000000'), (Theme.DARK, '#ffffff'), (Theme.LIGHT, '#000000')):
                with self.subTest(theme=theme):
                    setTheme(theme, lazy=False)
                    app.processEvents()
                    self.assertEqual(title.palette().color(QPalette.ColorRole.WindowText).name(), expected)
                    self.assertEqual(title.text(), '测试作品')
        finally:
            page.close()
            app.setPalette(original_palette)
            setTheme(original_theme, lazy=False)


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


    def test_parse_preview_ids_preserves_order_and_reports_invalid_tokens(self):
        from jmcomic_shelf.detail_service import parse_preview_ids
        self.assertEqual(
            parse_preview_ids('0123，jm456 JM 789；JM123、坏编号\nＪＭ　９０１ 123abc 0'),
            (['123', '456', '789', '901'], ['坏编号', '123abc', '0']),
        )

    def test_batch_query_shows_cards_and_reports_failures_at_end(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import patch
        from PIL import Image
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QApplication
        from jmcomic.jm_exception import MissingAlbumPhotoException
        from jmcomic_shelf.detail_service import DetailResult
        from jmcomic_shelf.settings import ShelfSettings
        from jmcomic_shelf.ui.detail_page import DetailPage

        app = QApplication.instance() or QApplication([])
        page = DetailPage()
        page.show()
        with tempfile.TemporaryDirectory() as tmp:
            cover = str(Path(tmp) / 'cover.jpg')
            Image.new('RGB', (80, 120), 'green').save(cover)
            def fetch(option, jm_id, cache, local_cover):
                if jm_id == '2':
                    raise MissingAlbumPhotoException('missing', {})
                if jm_id == '3':
                    raise OSError('连接超时')
                album = SimpleNamespace(album_id=jm_id, name='作品' + jm_id, authors=['作者'],
                                        tags=['标签一', '标签二'], episode_list=[])
                return DetailResult(album, cover)

            with patch('jmcomic_shelf.ui.detail_page.ShelfSettings.load', return_value=ShelfSettings(app_data_dir=tmp)), \
                 patch('jmcomic_shelf.ui.detail_page.fetch_album_detail_result', side_effect=fetch) as fetch_mock:
                page.input.setText('1，jm2 JM 3、错误 JM4 jm1')
                page.input.returnPressed.emit()
                self.assertFalse(page.query_button.isEnabled())
                import time
                deadline = time.monotonic() + 5
                while page.query is not None and time.monotonic() < deadline:
                    QTest.qWait(10)
                self.assertTrue(page.query_button.isEnabled())
                self.assertEqual([call.args[1] for call in fetch_mock.call_args_list], ['1', '2', '3', '4'])
                cards = [page.cards.itemAt(i).widget() for i in range(page.cards.count())]
                self.assertEqual([c.title.text() for c in cards], ['作品1', '作品4'])
                self.assertFalse(cards[0].cover.pixmap().isNull())
                for msg in ['错误', 'JM2：作品不存在', 'JM3：查询失败，连接超时']:
                    self.assertIn(msg, page.info.text())
                page.input.setText('bad')
                page.query_button.click()
                self.assertEqual(page.cards.count(), 0)
                self.assertIn('号码格式有误', page.info.text())
        page.close()
