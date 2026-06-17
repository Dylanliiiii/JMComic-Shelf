from test_jmcomic import *


class FakeShelfAlbum:
    def __init__(self):
        self.album_id = '211899'
        self.name = '作品A'
        self.authors = ['作者A', '作者B']
        self.tags = ['标签1', '标签2']
        self.episode_list = [('211899', '1', '作品A')]


class TestShelfIndexService(unittest.TestCase):

    def test_record_from_album_uses_album_metadata(self):
        from jmcomic_shelf.index_service import record_from_album

        record = record_from_album(FakeShelfAlbum(), pdf_path='D:/downloads/JM211899-作品A.pdf', cover_path='cover.jpg')

        self.assertEqual(record.jm_id, '211899')
        self.assertEqual(record.title, '作品A')
        self.assertEqual(record.authors, ['作者A', '作者B'])
        self.assertEqual(record.tags, ['标签1', '标签2'])
        self.assertEqual(record.chapters, [{'id': '211899', 'index': '1', 'title': '作品A'}])

    def test_group_by_author_for_library_display(self):
        from jmcomic_shelf.index_service import group_by_author
        from jmcomic_shelf.models import AlbumRecord

        records = [
            AlbumRecord('1', 'A', authors=['作者A', '作者B']),
            AlbumRecord('2', 'B', authors=['作者A']),
        ]

        grouped = group_by_author(records)

        self.assertEqual([x.jm_id for x in grouped['作者A']], ['1', '2'])
        self.assertEqual([x.jm_id for x in grouped['作者B']], ['1'])

    def test_rebuild_index_from_download_dir_finds_existing_pdf_and_images(self):
        from tempfile import TemporaryDirectory

        from PIL import Image

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.index_service import rebuild_index_from_download_dir

        with TemporaryDirectory() as tmp:
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A', '第1章')
            os.makedirs(album_dir)
            cover_path = os.path.join(album_dir, '00001.jpg')
            Image.new('RGB', (120, 180), 'red').save(cover_path)
            pdf_path = os.path.join(tmp, 'JM211899-作品A.pdf')
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\n')

            db_path = os.path.join(tmp, 'app', 'shelf.db')
            count = rebuild_index_from_download_dir(tmp, db_path, os.path.join(tmp, 'app', 'covers'))

            db = ShelfDatabase(db_path)
            db.open()
            try:
                records = db.query_albums('211899')
            finally:
                db.close()

            self.assertEqual(count, 1)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].title, '作品A')
            self.assertEqual(records[0].authors, ['作者A'])
            self.assertEqual(records[0].pdf_path, pdf_path)
            self.assertTrue(os.path.exists(records[0].cover_path))
