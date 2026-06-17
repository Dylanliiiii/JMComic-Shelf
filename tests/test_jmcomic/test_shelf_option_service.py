from test_jmcomic import *
from tempfile import TemporaryDirectory


class TestShelfOptionService(unittest.TestCase):

    def test_update_option_download_dir_updates_base_dir(self):
        from jmcomic_shelf.option_service import update_option_download_dir

        with TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'jmcomic-option.yml')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write(
                    'version: "2.1"\n'
                    'dir_rule:\n'
                    '  base_dir: D:/old\n'
                    '  rule: Bd / Aauthor / JM{Aid}-{Atitle} / 第{Pindex}章\n'
                    '  normalize_zh: null\n'
                    'download: {}\n'
                    'client: {}\n'
                    'plugins: {}\n'
                )

            update_option_download_dir(option_path, 'D:/new')

            with open(option_path, encoding='utf-8') as f:
                content = f.read()

            self.assertIn('base_dir: D:/new', content)
