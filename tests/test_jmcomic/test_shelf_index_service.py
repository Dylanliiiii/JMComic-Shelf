from test_jmcomic import *
from unittest.mock import patch


class FakeShelfAlbum:
    def __init__(self):
        self.album_id = '211899'
        self.name = '作品A'
        self.authors = ['作者A', '作者B']
        self.tags = ['标签1', '标签2']
        self.episode_list = [('211899', '1', '作品A')]


class TestShelfIndexService(unittest.TestCase):

    def test_record_from_album_uses_album_metadata_and_first_author(self):
        from jmcomic_shelf.index_service import record_from_album

        record = record_from_album(FakeShelfAlbum(), pdf_path='D:/downloads/JM211899-作品A.pdf', cover_path='cover.jpg')

        self.assertEqual(record.jm_id, '211899')
        self.assertEqual(record.title, '作品A')
        self.assertEqual(record.authors, ['作者A'])
        self.assertEqual(record.tags, ['标签1', '标签2'])
        self.assertEqual(record.chapters, [{'id': '211899', 'index': '1', 'title': '作品A'}])

    def test_group_by_author_for_library_display_uses_first_author_only(self):
        from jmcomic_shelf.index_service import group_by_author
        from jmcomic_shelf.models import AlbumRecord

        records = [
            AlbumRecord('1', 'A', authors=['作者A', '作者B']),
            AlbumRecord('2', 'B', authors=['作者A']),
        ]

        grouped = group_by_author(records)

        self.assertEqual([x.jm_id for x in grouped['作者A']], ['1', '2'])
        self.assertNotIn('作者B', grouped)

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
            self.assertEqual(records[0].album_dir, os.path.dirname(album_dir))
            self.assertTrue(os.path.exists(records[0].cover_path))

    def test_rebuild_index_from_download_dir_writes_records_in_one_batch(self):
        from tempfile import TemporaryDirectory

        from jmcomic_shelf.index_service import rebuild_index_from_download_dir

        calls = []

        class FakeDatabase:
            def __init__(self, db_path):
                self.db_path = db_path

            def open(self):
                calls.append(('open', self.db_path))

            def upsert_albums(self, records):
                calls.append(('batch', [record.jm_id for record in records]))

            def upsert_album(self, record):
                calls.append(('single', record.jm_id))

            def close(self):
                calls.append(('close', self.db_path))

        with TemporaryDirectory() as tmp:
            author_dir = os.path.join(tmp, 'A作者')
            os.makedirs(author_dir)
            for jm_id in ['100', '200']:
                with open(os.path.join(author_dir, f'JM{jm_id}-作品{jm_id}.pdf'), 'wb') as f:
                    f.write(b'%PDF-1.4\n')

            with patch('jmcomic_shelf.index_service.ShelfDatabase', FakeDatabase):
                count = rebuild_index_from_download_dir(tmp, os.path.join(tmp, 'app', 'shelf.db'))

        self.assertEqual(count, 2)
        self.assertEqual([call[0] for call in calls], ['open', 'batch', 'close'])
        self.assertEqual(calls[1][1], ['200', '100'])

    def test_rebuild_index_from_pdf_only_author_dir_uses_cover_folder(self):
        from tempfile import TemporaryDirectory

        from PIL import Image

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.index_service import rebuild_index_from_download_dir

        with TemporaryDirectory() as tmp:
            author_dir = os.path.join(tmp, '作者A')
            os.makedirs(author_dir)
            pdf_path = os.path.join(author_dir, 'JM211899-作品A.pdf')
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\n')
            cover_dir = os.path.join(tmp, 'Cover')
            os.makedirs(cover_dir)
            cover_path = os.path.join(cover_dir, 'JM211899.jpg')
            Image.new('RGB', (120, 180), 'red').save(cover_path)

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
            self.assertEqual(records[0].album_dir, author_dir)
            self.assertTrue(os.path.exists(records[0].cover_path))

    def test_rebuild_index_from_download_dir_merges_tags_from_catalog(self):
        from tempfile import TemporaryDirectory

        from PIL import Image

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.index_service import rebuild_index_from_download_dir

        with TemporaryDirectory() as tmp:
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A', '第1章')
            os.makedirs(album_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(album_dir, '00001.jpg'))
            with open(os.path.join(tmp, 'catalog.md'), 'w', encoding='utf-8-sig') as f:
                f.write('# 作者A\n')
                f.write('1. JM211899-作品A\n')
                f.write('   - 标签：後宮, 巨乳\n')

            db_path = os.path.join(tmp, 'app', 'shelf.db')
            rebuild_index_from_download_dir(tmp, db_path, os.path.join(tmp, 'app', 'covers'))

            db = ShelfDatabase(db_path)
            db.open()
            try:
                records = db.query_albums('211899')
                tags = db.list_tags()
            finally:
                db.close()

            self.assertEqual(records[0].tags, ['后宫', '巨乳'])
            self.assertEqual(tags, ['后宫', '巨乳'])

    def test_rebuild_index_from_catalog_keeps_only_first_author_for_existing_duplicates(self):
        from tempfile import TemporaryDirectory

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.index_service import rebuild_index_from_download_dir

        with TemporaryDirectory() as tmp:
            author_dir = os.path.join(tmp, '作者A')
            os.makedirs(author_dir)
            with open(os.path.join(author_dir, 'JM211899-作品A.pdf'), 'wb') as f:
                f.write(b'%PDF-1.4\n')
            with open(os.path.join(tmp, 'catalog.md'), 'w', encoding='utf-8-sig') as f:
                f.write(
                    '# 作者A\n'
                    '1. 📖 标题：作品A\n'
                    '   - 🆔 ID：JM211899\n'
                    '   - 🏷️ 标签：标签1\n'
                    '\n'
                    '# 作者B\n'
                    '1. 📖 标题：作品A\n'
                    '   - 🆔 ID：JM211899\n'
                    '   - 🏷️ 标签：标签1\n'
                )

            db_path = os.path.join(tmp, 'app', 'shelf.db')
            rebuild_index_from_download_dir(tmp, db_path)

            db = ShelfDatabase(db_path)
            db.open()
            try:
                records = db.query_albums('211899')
            finally:
                db.close()

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].authors, ['作者A'])

    def test_rebuild_index_from_download_dir_finds_long_path_pdf(self):
        from tempfile import TemporaryDirectory

        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.index_service import rebuild_index_from_download_dir
        from jmcomic_shelf.path_utils import path_for_open

        with TemporaryDirectory() as tmp:
            title = 'long-title-' * 18
            author_dir = os.path.join(tmp, 'author')
            album_dir = os.path.join(author_dir, 'JM211899-' + title)
            os.makedirs(path_for_open(album_dir))
            pdf_path = os.path.join(album_dir, 'JM211899-' + title + '.pdf')
            with open(path_for_open(pdf_path), 'wb') as f:
                f.write(b'%PDF-1.4\n')

            try:
                db_path = os.path.join(tmp, 'app', 'shelf.db')
                count = rebuild_index_from_download_dir(tmp, db_path)

                db = ShelfDatabase(db_path)
                db.open()
                try:
                    records = db.query_albums('211899')
                finally:
                    db.close()

                self.assertEqual(count, 1)
                self.assertEqual(records[0].pdf_path, pdf_path)
            finally:
                if os.path.exists(path_for_open(pdf_path)):
                    os.remove(path_for_open(pdf_path))
                if os.path.isdir(path_for_open(album_dir)):
                    os.rmdir(path_for_open(album_dir))
