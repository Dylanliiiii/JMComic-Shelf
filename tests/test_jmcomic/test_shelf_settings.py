from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfSettings(unittest.TestCase):

    def test_default_app_data_dir_uses_appdata_when_present(self):
        from jmcomic_shelf.paths import get_default_app_data_dir

        old = os.environ.get('APPDATA')
        with TemporaryDirectory() as tmp:
            os.environ['APPDATA'] = tmp
            try:
                self.assertEqual(
                    get_default_app_data_dir(),
                    os.path.join(tmp, 'JMComic Shelf'),
                )
            finally:
                if old is None:
                    os.environ.pop('APPDATA', None)
                else:
                    os.environ['APPDATA'] = old

    def test_settings_round_trip(self):
        from jmcomic_shelf.settings import ShelfSettings

        with TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'settings.json')
            settings = ShelfSettings(
                download_dir='D:/path/to/JMComic',
                option_path='D:/path/to/JMComic Shelf/jmcomic-option.yml',
                app_data_dir=tmp,
            )

            settings.save(path)
            loaded = ShelfSettings.load(path)

            self.assertEqual(loaded.download_dir, 'D:/path/to/JMComic')
            self.assertEqual(loaded.option_path, 'D:/path/to/JMComic Shelf/jmcomic-option.yml')
            self.assertEqual(loaded.app_data_dir, tmp)

    def test_default_option_path_uses_project_dir_when_present(self):
        from jmcomic_shelf.settings import ShelfSettings

        old = os.environ.get('JMCOMIC_SHELF_PROJECT_DIR')
        with TemporaryDirectory() as tmp:
            os.environ['JMCOMIC_SHELF_PROJECT_DIR'] = tmp
            try:
                settings = ShelfSettings()
                self.assertEqual(settings.option_path, os.path.join(tmp, 'jmcomic-option.yml'))
            finally:
                if old is None:
                    os.environ.pop('JMCOMIC_SHELF_PROJECT_DIR', None)
                else:
                    os.environ['JMCOMIC_SHELF_PROJECT_DIR'] = old
