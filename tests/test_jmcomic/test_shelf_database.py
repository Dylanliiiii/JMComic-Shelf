from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfDatabase(unittest.TestCase):

    def test_upsert_album_and_query_all(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                db.upsert_album(AlbumRecord(
                    jm_id='211899',
                    title='作品A',
                    link='https://18comic.vip/album/211899/',
                    pdf_path=os.path.join(tmp, 'JM211899-作品A.pdf'),
                    cover_path=os.path.join(tmp, 'covers', 'JM211899.jpg'),
                    authors=['作者A', '作者B'],
                    tags=['标签1', '标签2'],
                    chapters=[{'id': '211899', 'index': '1', 'title': '作品A'}],
                ))

                result = db.query_albums('')
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0].jm_id, '211899')
                self.assertEqual(result[0].authors, ['作者A', '作者B'])
                self.assertEqual(result[0].tags, ['标签1', '标签2'])
            finally:
                db.close()

    def test_query_by_jm_id_author_and_tag(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                db.upsert_album(AlbumRecord('211899', '作品A', '', '', '', ['作者A'], ['后宫'], []))
                db.upsert_album(AlbumRecord('123456', '作品B', '', '', '', ['作者B'], ['全彩'], []))

                self.assertEqual([x.jm_id for x in db.query_albums('JM211899')], ['211899'])
                self.assertEqual([x.jm_id for x in db.query_albums('作者B')], ['123456'])
                self.assertEqual([x.jm_id for x in db.query_albums('后宫')], ['211899'])
            finally:
                db.close()

    def test_list_tags_and_query_by_exact_tag(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                db.upsert_album(AlbumRecord('211899', '作品A', authors=['作者A'], tags=['后宫', '巨乳']))
                db.upsert_album(AlbumRecord('123456', '作品B', authors=['作者B'], tags=['后宫', '全彩']))

                self.assertEqual(db.list_tags(), ['全彩', '后宫', '巨乳'])
                self.assertEqual({x.jm_id for x in db.query_albums_by_tag('后宫')}, {'123456', '211899'})
                self.assertEqual([x.jm_id for x in db.query_albums_by_tag('巨')], [])
            finally:
                db.close()

    def test_query_albums_by_tags_matches_any_selected_tag(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                db.upsert_album(AlbumRecord('211899', '作品A', authors=['作者A'], tags=['后宫', '巨乳']))
                db.upsert_album(AlbumRecord('123456', '作品B', authors=['作者B'], tags=['全彩']))
                db.upsert_album(AlbumRecord('654321', '作品C', authors=['作者C'], tags=['校园']))

                result = db.query_albums_by_tags(['後宮', '全彩'])

                self.assertEqual({x.jm_id for x in result}, {'123456', '211899'})
                self.assertEqual([x.jm_id for x in db.query_albums_by_tags([])], [])
            finally:
                db.close()

    def test_query_albums_order_is_stable_after_reindex_upserts(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                db.upsert_album(AlbumRecord('100', 'B', authors=['B作者'], tags=['tag']))
                db.upsert_album(AlbumRecord('200', 'A', authors=['A作者'], tags=['tag']))
                db.conn.execute("UPDATE albums SET updated_at = '2030-01-01 00:00:00' WHERE jm_id = '100'")
                db.conn.execute("UPDATE albums SET updated_at = '2020-01-01 00:00:00' WHERE jm_id = '200'")
                db.conn.commit()

                first_order = [x.jm_id for x in db.query_albums('')]
                self.assertEqual(first_order, ['200', '100'])
                self.assertEqual([x.jm_id for x in db.query_albums('')], first_order)
                self.assertEqual([x.jm_id for x in db.query_albums_by_tag('tag')], first_order)
                self.assertEqual([x.jm_id for x in db.query_albums_by_tags(['tag'])], first_order)
            finally:
                db.close()

    def test_delete_albums_removes_selected_records(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.models import AlbumRecord

        with TemporaryDirectory() as tmp:
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                db.upsert_album(AlbumRecord('211899', '作品A', authors=['作者A'], tags=['标签1']))
                db.upsert_album(AlbumRecord('123456', '作品B', authors=['作者B'], tags=['标签2']))

                deleted = db.delete_albums(['211899'])

                self.assertEqual(deleted, 1)
                self.assertEqual([x.jm_id for x in db.query_albums('')], ['123456'])
            finally:
                db.close()
