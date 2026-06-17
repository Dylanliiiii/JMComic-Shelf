from test_jmcomic import *


class TestShelfDetailService(unittest.TestCase):

    def test_fetch_album_detail_requires_option_path(self):
        from jmcomic_shelf.detail_service import fetch_album_detail

        with self.assertRaisesRegex(ValueError, '请先在设置里选择配置文件'):
            fetch_album_detail('', '211899')
