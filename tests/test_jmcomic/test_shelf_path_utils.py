from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfPathUtils(unittest.TestCase):

    def test_long_path_file_is_detected(self):
        from jmcomic_shelf.path_utils import path_exists, path_for_open

        with TemporaryDirectory() as tmp:
            name = 'JM123456-' + ('长标题' * 45)
            album_dir = os.path.join(tmp, name)
            os.makedirs(album_dir)
            pdf_path = os.path.join(album_dir, name + '.pdf')

            with open(path_for_open(pdf_path), 'wb') as f:
                f.write(b'%PDF-1.4\n')

            self.assertTrue(path_exists(pdf_path))
            os.remove(path_for_open(pdf_path))
