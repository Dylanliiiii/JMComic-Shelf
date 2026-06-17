from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfDeleteService(unittest.TestCase):

    def test_delete_album_files_removes_download_dir_album_assets_only(self):
        from jmcomic_shelf.delete_service import delete_album_files
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            download_dir = os.path.join(tmp, 'downloads')
            album_dir = os.path.join(download_dir, '作者A', 'JM211899-作品A')
            os.makedirs(album_dir)
            image_path = os.path.join(album_dir, '第1章', '00001.jpg')
            os.makedirs(os.path.dirname(image_path))
            with open(image_path, 'wb') as f:
                f.write(b'image')
            pdf_path = os.path.join(download_dir, 'JM211899-作品A.pdf')
            with open(pdf_path, 'wb') as f:
                f.write(b'pdf')

            outside_pdf = os.path.join(tmp, 'outside.pdf')
            with open(outside_pdf, 'wb') as f:
                f.write(b'outside')

            result = delete_album_files(
                [
                    AlbumRecord('211899', '作品A', pdf_path=pdf_path, album_dir=album_dir),
                    AlbumRecord('123456', '作品B', pdf_path=outside_pdf),
                    AlbumRecord('654321', '作品C', album_dir=download_dir),
                ],
                download_dir,
            )

            self.assertEqual(result.deleted_count, 2)
            self.assertFalse(os.path.exists(album_dir))
            self.assertFalse(os.path.exists(pdf_path))
            self.assertTrue(os.path.exists(download_dir))
            self.assertTrue(os.path.exists(outside_pdf))
            self.assertIn(outside_pdf, result.skipped_paths)
            self.assertIn(download_dir, result.skipped_paths)
