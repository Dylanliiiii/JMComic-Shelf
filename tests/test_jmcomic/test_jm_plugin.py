from test_jmcomic import *
from tempfile import TemporaryDirectory


class FakeCatalogAlbum:

    def __init__(self, album_id, name, authors, tags, episode_list=None):
        self.album_id = str(album_id)
        self.name = name
        self.authors = authors
        self.tags = tags
        self.episode_list = episode_list or [(str(album_id), '1', name)]


class FakeCatalogPhoto:

    def __init__(self, index):
        self.index = index


class FakeCatalogImage:

    def __init__(self, index):
        self.index = index


class FakeCatalogDownloader:

    def __init__(self, album, photo_dict):
        self.download_success_dict = {album: photo_dict}


class Test_CatalogPlugin(unittest.TestCase):

    def test_catalog_plugin_embeds_first_downloaded_image_as_cover(self):
        from jmcomic.jm_plugin import CatalogPlugin

        album = FakeCatalogAlbum(
            '211899',
            '\u4f5c\u54c1A',
            ['\u4f5c\u8005A'],
            ['\u6807\u7b7e1'],
        )

        with TemporaryDirectory() as tmp:
            catalog_path = os.path.join(tmp, 'catalog.md')
            first_image_path = os.path.join(tmp, '00001.jpg')
            second_image_path = os.path.join(tmp, '00002.jpg')
            with open(first_image_path, 'wb') as f:
                f.write(b'first-page')
            with open(second_image_path, 'wb') as f:
                f.write(b'second-page')

            photo = FakeCatalogPhoto(1)
            downloader = FakeCatalogDownloader(
                album,
                {
                    photo: [
                        (second_image_path, FakeCatalogImage(2)),
                        (first_image_path, FakeCatalogImage(1)),
                    ],
                },
            )

            plugin = CatalogPlugin(None)
            plugin.invoke(album=album, filepath=catalog_path, downloader=downloader)

            with open(catalog_path, encoding='utf-8-sig') as f:
                content = f.read()

            self.assertIn(
                '<img src="data:image/jpeg;base64,Zmlyc3QtcGFnZQ==" alt="JM211899" width="120" style="vertical-align: top;">',
                content,
            )
            self.assertNotIn('c2Vjb25kLXBhZ2U=', content)

    def test_catalog_plugin_preserves_existing_cover_on_update(self):
        from jmcomic.jm_plugin import CatalogPlugin

        album = FakeCatalogAlbum(
            '211899',
            '\u4f5c\u54c1A',
            ['\u4f5c\u8005A'],
            ['\u6807\u7b7e1'],
        )

        with TemporaryDirectory() as tmp:
            catalog_path = os.path.join(tmp, 'catalog.md')
            with open(catalog_path, 'w', encoding='utf-8-sig') as f:
                f.write(
                    '# \u4f5c\u8005A\n'
                    '1. <img src="data:image/jpeg;base64,Y292ZXItYnl0ZXM=" alt="JM211899" width="120" style="vertical-align: top;">\n'
                    '\n'
                    '   - \U0001f4d6 \u6807\u9898\uff1a\u4f5c\u54c1A\n'
                    '   - \U0001f194 ID\uff1aJM211899\n'
                    '   - \U0001f517 \u94fe\u63a5\uff1ahttps://18comic.vip/album/211899/\n'
                    '   - \U0001f3f7\ufe0f \u6807\u7b7e\uff1a\u6807\u7b7e1\n'
                    '   - \U0001f4d1 \u7ae0\u8282\uff1a\u7b2c1\u8bdd \u4f5c\u54c1A (id: 211899)\n'
                )

            plugin = CatalogPlugin(None)
            plugin.invoke(album=album, filepath=catalog_path)

            with open(catalog_path, encoding='utf-8-sig') as f:
                content = f.read()

            self.assertEqual(content.count('data:image/jpeg;base64,Y292ZXItYnl0ZXM='), 1)

    def test_catalog_plugin_writes_author_grouped_index(self):
        from jmcomic.jm_plugin import CatalogPlugin

        album_a = FakeCatalogAlbum(
            '211899',
            '\u4f5c\u54c1A',
            ['\u4f5c\u8005A', '\u4f5c\u8005B'],
            ['\u6807\u7b7e1', '\u6807\u7b7e2'],
        )
        album_b = FakeCatalogAlbum(
            '123456',
            '\u4f5c\u54c1B',
            ['\u4f5c\u8005A'],
            ['\u6807\u7b7e3'],
        )

        with TemporaryDirectory() as tmp:
            catalog_path = os.path.join(tmp, 'catalog.md')
            plugin = CatalogPlugin(None)

            plugin.invoke(album=album_a, filepath=catalog_path)
            plugin.invoke(album=album_b, filepath=catalog_path)
            plugin.invoke(album=album_a, filepath=catalog_path)

            with open(catalog_path, encoding='utf-8-sig') as f:
                content = f.read()

            self.assertEqual(
                content,
                '# \u4f5c\u8005A\n'
                '1. \U0001f4d6 \u6807\u9898\uff1a\u4f5c\u54c1A\n'
                '   - \U0001f194 ID\uff1aJM211899\n'
                '   - \U0001f517 \u94fe\u63a5\uff1ahttps://18comic.vip/album/211899/\n'
                '   - \U0001f3f7\ufe0f \u6807\u7b7e\uff1a\u6807\u7b7e1, \u6807\u7b7e2\n'
                '   - \U0001f4d1 \u7ae0\u8282\uff1a\u7b2c1\u8bdd \u4f5c\u54c1A (id: 211899)\n'
                '\n'
                '2. \U0001f4d6 \u6807\u9898\uff1a\u4f5c\u54c1B\n'
                '   - \U0001f194 ID\uff1aJM123456\n'
                '   - \U0001f517 \u94fe\u63a5\uff1ahttps://18comic.vip/album/123456/\n'
                '   - \U0001f3f7\ufe0f \u6807\u7b7e\uff1a\u6807\u7b7e3\n'
                '   - \U0001f4d1 \u7ae0\u8282\uff1a\u7b2c1\u8bdd \u4f5c\u54c1B (id: 123456)\n'
                '\n'
                '# \u4f5c\u8005B\n'
                '1. \U0001f4d6 \u6807\u9898\uff1a\u4f5c\u54c1A\n'
                '   - \U0001f194 ID\uff1aJM211899\n'
                '   - \U0001f517 \u94fe\u63a5\uff1ahttps://18comic.vip/album/211899/\n'
                '   - \U0001f3f7\ufe0f \u6807\u7b7e\uff1a\u6807\u7b7e1, \u6807\u7b7e2\n'
                '   - \U0001f4d1 \u7ae0\u8282\uff1a\u7b2c1\u8bdd \u4f5c\u54c1A (id: 211899)\n',
            )

    def test_catalog_plugin_preserves_original_text(self):
        from jmcomic.jm_plugin import CatalogPlugin

        album = FakeCatalogAlbum(
            '211899',
            '\u7570\u4e16\u754c\u6deb\u4e82\u5f8c\u5bae',
            ['\u8d64\u6708\u307f\u3085\u3046\u3068'],
            ['\u5f8c\u5bae', '\u5de8\u4e73'],
        )

        with TemporaryDirectory() as tmp:
            catalog_path = os.path.join(tmp, 'catalog.md')
            plugin = CatalogPlugin(None)
            plugin.invoke(album=album, filepath=catalog_path)

            with open(catalog_path, encoding='utf-8-sig') as f:
                content = f.read()

            self.assertIn('\u7570\u4e16\u754c\u6deb\u4e82\u5f8c\u5bae', content)
            self.assertIn('\u5f8c\u5bae', content)


class Test_ShelfIndexPlugin(unittest.TestCase):

    def test_shelf_index_plugin_updates_sqlite(self):
        from jmcomic.jm_plugin import ShelfIndexPlugin
        from jmcomic_shelf.database import ShelfDatabase

        album = FakeCatalogAlbum('211899', '作品A', ['作者A'], ['标签1'])

        with TemporaryDirectory() as tmp:
            db_path = os.path.join(tmp, 'shelf.db')
            plugin = ShelfIndexPlugin(None)
            plugin.invoke(album=album, db_path=db_path, pdf_path=os.path.join(tmp, 'JM211899-作品A.pdf'))

            db = ShelfDatabase(db_path)
            db.open()
            try:
                result = db.query_albums('211899')
            finally:
                db.close()

            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].title, '作品A')
            self.assertEqual(result[0].authors, ['作者A'])


class Test_Plugin(JmTestConfigurable):

    def test_plugin_missing_album_context(self):
        """
        source: https://github.com/hect0x7/JMComic-Crawler-Python/issues/523
        """
        photo_id = '350234'
        option = self.new_option()

        flawed_rule = {
            'base_dir': option.dir_rule.base_dir,
            'rule': '{Atitle}/{Aid}_photo.jpg'
        }

        from jmcomic.jm_downloader import DoNotDownloadImage

        test_plugins = ['download_cover', 'img2pdf', 'long_img', 'zip']
        option.plugins['before_photo'] = [
            {
                'plugin': plugin_key,
                'kwargs': {'dir_rule': flawed_rule},
                'safe': False
            }
            for plugin_key in test_plugins
        ]

        download_photo(photo_id, option, downloader=DoNotDownloadImage)
        print('All folder rule plugins assert completed safely without KeyError.')
