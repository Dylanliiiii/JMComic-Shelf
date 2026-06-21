from test_jmcomic import *
from tempfile import TemporaryDirectory
from unittest.mock import patch


class TestShelfRepairService(unittest.TestCase):

    def test_repair_library_builds_missing_pdf_removes_image_dir_and_rebuilds_index(self):
        from PIL import Image

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.repair_service import repair_library

        with TemporaryDirectory() as tmp:
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A')
            chapter_dir = os.path.join(album_dir, '第1章')
            os.makedirs(chapter_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(chapter_dir, '00001.jpg'))
            Image.new('RGB', (120, 180), 'blue').save(os.path.join(chapter_dir, '00002.jpg'))

            db_path = os.path.join(tmp, 'app', 'shelf.db')
            result = repair_library(tmp, db_path, os.path.join(tmp, 'app', 'covers'))

            final_pdf = os.path.join(tmp, '作者A', 'JM211899-作品A.pdf')
            final_cover = os.path.join(tmp, 'Cover', 'JM211899-作品A.jpg')
            self.assertEqual(result.found_dirs, 1)
            self.assertEqual(result.repaired_pdfs, 1)
            self.assertEqual(result.removed_dirs, 1)
            self.assertEqual(result.failed, 0)
            self.assertEqual(result.synced_count, 1)
            self.assertTrue(os.path.exists(final_pdf))
            self.assertGreater(os.path.getsize(final_pdf), 0)
            self.assertTrue(os.path.exists(final_cover))
            self.assertFalse(os.path.exists(album_dir))

            db = ShelfDatabase(db_path)
            db.open()
            try:
                records = db.query_albums('211899')
            finally:
                db.close()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].pdf_path, final_pdf)

    def test_repair_library_removes_residual_image_dir_when_pdf_already_exists(self):
        from PIL import Image

        from jmcomic_shelf.repair_service import repair_library

        with TemporaryDirectory() as tmp:
            author_dir = os.path.join(tmp, '作者A')
            album_dir = os.path.join(author_dir, 'JM211899-作品A')
            chapter_dir = os.path.join(album_dir, '第1章')
            os.makedirs(chapter_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(chapter_dir, '00001.jpg'))
            final_pdf = os.path.join(author_dir, 'JM211899-作品A.pdf')
            with open(final_pdf, 'wb') as f:
                f.write(b'%PDF-1.4\n')

            result = repair_library(tmp, os.path.join(tmp, 'app', 'shelf.db'))

            self.assertEqual(result.found_dirs, 1)
            self.assertEqual(result.repaired_pdfs, 0)
            self.assertEqual(result.removed_dirs, 1)
            self.assertEqual(result.failed, 0)
            self.assertFalse(os.path.exists(album_dir))
            self.assertTrue(os.path.exists(final_pdf))

    def test_repair_library_keeps_image_dir_when_pdf_generation_fails(self):
        from PIL import Image

        from jmcomic_shelf.repair_service import repair_library

        with TemporaryDirectory() as tmp:
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A')
            chapter_dir = os.path.join(album_dir, '第1章')
            os.makedirs(chapter_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(chapter_dir, '00001.jpg'))

            with patch('jmcomic_shelf.repair_service._convert_images_to_pdf', side_effect=RuntimeError('broken pdf')):
                result = repair_library(tmp, os.path.join(tmp, 'app', 'shelf.db'))

            final_pdf = os.path.join(tmp, '作者A', 'JM211899-作品A.pdf')
            self.assertEqual(result.found_dirs, 1)
            self.assertEqual(result.repaired_pdfs, 0)
            self.assertEqual(result.removed_dirs, 0)
            self.assertEqual(result.failed, 1)
            self.assertTrue(os.path.exists(album_dir))
            self.assertFalse(os.path.exists(final_pdf))
            self.assertIn('broken pdf', result.entries[0].message)
