from test_jmcomic import *
from tempfile import TemporaryDirectory

from PIL import Image


class TestShelfCoverCache(unittest.TestCase):

    def test_thumbnail_preserves_portrait_aspect_ratio_without_crop(self):
        from jmcomic_shelf.cover_cache import CoverCache

        with TemporaryDirectory() as tmp:
            source = os.path.join(tmp, 'source.jpg')
            Image.new('RGB', (1000, 1600), 'red').save(source)

            cache = CoverCache(os.path.join(tmp, 'covers'), max_width=240)
            output = cache.create_thumbnail('211899', source)

            with Image.open(output) as img:
                self.assertEqual(img.size, (240, 384))

    def test_thumbnail_preserves_landscape_aspect_ratio_without_crop(self):
        from jmcomic_shelf.cover_cache import CoverCache

        with TemporaryDirectory() as tmp:
            source = os.path.join(tmp, 'source.jpg')
            Image.new('RGB', (1600, 1000), 'blue').save(source)

            cache = CoverCache(os.path.join(tmp, 'covers'), max_width=240)
            output = cache.create_thumbnail('123456', source)

            with Image.open(output) as img:
                self.assertEqual(img.size, (240, 150))
