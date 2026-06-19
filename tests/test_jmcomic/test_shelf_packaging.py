from test_jmcomic import *


class TestShelfPackaging(unittest.TestCase):

    def test_pyproject_uses_desktop_app_distribution_name(self):
        import pathlib
        import tomllib

        pyproject = pathlib.Path('pyproject.toml')
        data = tomllib.loads(pyproject.read_text(encoding='utf-8'))

        self.assertEqual(data['project']['name'], 'JMComic-Shelf')

    def test_pyproject_version_uses_desktop_app_version(self):
        import pathlib
        import tomllib

        pyproject = pathlib.Path('pyproject.toml')
        data = tomllib.loads(pyproject.read_text(encoding='utf-8'))

        self.assertEqual(
            data['tool']['setuptools']['dynamic']['version']['attr'],
            'jmcomic_shelf.__version__',
        )

    def test_setup_py_reads_desktop_app_version(self):
        import pathlib

        setup_py = pathlib.Path('setup.py').read_text(encoding='utf-8')

        self.assertIn("name='JMComic-Shelf'", setup_py)
        self.assertIn('./src/jmcomic_shelf/__init__.py', setup_py)
        self.assertNotIn("./src/jmcomic/__init__.py", setup_py)
