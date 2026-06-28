from test_jmcomic import *


class TestShelfPackaging(unittest.TestCase):

    def test_pyappify_runs_from_working_tree_source_entry(self):
        import pathlib
        import yaml

        pyappify = pathlib.Path('pyappify.yml')
        data = yaml.safe_load(pyappify.read_text(encoding='utf-8'))
        release_profile = data['profiles'][0]

        self.assertEqual(release_profile['main_script'], 'run-jmcomic-shelf.py')
        self.assertNotEqual(release_profile['main_script'], 'jmcomic-shelf')

        launcher = pathlib.Path(release_profile['main_script'])
        source = launcher.read_text(encoding='utf-8')
        self.assertIn('sys.path.insert(0, str(SRC_DIR))', source)
        self.assertIn('from jmcomic_shelf.app import main', source)

    def test_pyappify_source_entry_prefers_current_working_tree_src(self):
        import pathlib
        import runpy
        import sys

        launcher = pathlib.Path('run-jmcomic-shelf.py').resolve()
        expected_src = launcher.parent / 'src'
        old_path = list(sys.path)
        old_modules = {
            name: sys.modules.pop(name)
            for name in list(sys.modules)
            if name == 'jmcomic_shelf' or name.startswith('jmcomic_shelf.')
        }

        try:
            sys.path = [
                item for item in sys.path
                if pathlib.Path(item or '.').resolve() != expected_src
            ]
            namespace = runpy.run_path(str(launcher), run_name='__pyappify_test__')

            self.assertEqual(pathlib.Path(sys.path[0]).resolve(), expected_src)
            self.assertEqual(namespace['main'].__module__, 'jmcomic_shelf.app')
        finally:
            sys.path = old_path
            for name in list(sys.modules):
                if name == 'jmcomic_shelf' or name.startswith('jmcomic_shelf.'):
                    sys.modules.pop(name)
            sys.modules.update(old_modules)

    def test_pyappify_keeps_dependency_install_from_project_root(self):
        import pathlib
        import yaml

        data = yaml.safe_load(pathlib.Path('pyappify.yml').read_text(encoding='utf-8'))
        release_profile = data['profiles'][0]

        self.assertEqual(release_profile['requirements'], '.')

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

    def test_desktop_package_includes_pdf_generation_dependency(self):
        import pathlib
        import tomllib

        pyproject = pathlib.Path('pyproject.toml')
        data = tomllib.loads(pyproject.read_text(encoding='utf-8'))
        dependencies = {item.lower() for item in data['project']['dependencies']}
        setup_py = pathlib.Path('setup.py').read_text(encoding='utf-8').lower()

        self.assertIn('img2pdf', dependencies)
        self.assertIn("'img2pdf'", setup_py)

    def test_setup_py_reads_desktop_app_version(self):
        import pathlib

        setup_py = pathlib.Path('setup.py').read_text(encoding='utf-8')

        self.assertIn("name='JMComic-Shelf'", setup_py)
        self.assertIn('./src/jmcomic_shelf/__init__.py', setup_py)
        self.assertIn("line.startswith('__version__')", setup_py)
        self.assertNotIn("./src/jmcomic/__init__.py", setup_py)
