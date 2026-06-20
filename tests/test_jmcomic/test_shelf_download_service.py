from test_jmcomic import *
from tempfile import TemporaryDirectory


class FakeDownloadedAlbum:
    album_id = '211899'
    name = '作品A'
    authors = ['作者A', '作者B']
    tags = ['标签1']
    episode_list = [('211899', '1', '作品A')]


class TestShelfDownloadService(unittest.TestCase):

    def test_parse_album_ids_supports_space_newline_and_comma(self):
        from jmcomic_shelf.download_service import parse_album_ids

        self.assertEqual(
            parse_album_ids('211899 123456,p789\nJM654321'),
            ['211899', '123456', 'p789', '654321'],
        )

    def test_task_retry_resets_failed_state(self):
        from jmcomic_shelf.download_service import DownloadTask

        task = DownloadTask(jm_id='211899', status='failed', error='network')
        task.mark_waiting()

        self.assertEqual(task.status, 'waiting')
        self.assertEqual(task.error, '')

    def test_run_task_reports_missing_option_path(self):
        from jmcomic_shelf.download_service import DownloadService, DownloadTask

        task = DownloadTask(jm_id='211899')
        DownloadService('').run_task(task)

        self.assertEqual(task.status, 'failed')
        self.assertIn('请先在设置里选择配置文件', task.error)

    def test_run_task_indexes_downloaded_album(self):
        from jmcomic_shelf.database import ShelfDatabase
        from jmcomic_shelf.download_service import DownloadService, DownloadTask

        with TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'jmcomic-option.yml')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write('version: "2.1"\n')
            pdf_path = os.path.join(tmp, 'JM211899-作品A.pdf')
            with open(pdf_path, 'wb') as f:
                f.write(b'pdf')

            def fake_create_option(path):
                self.assertEqual(path, option_path)
                return object()

            def fake_download_album(jm_id, option):
                self.assertEqual(jm_id, '211899')
                return FakeDownloadedAlbum(), object()

            task = DownloadTask(jm_id='211899')
            service = DownloadService(
                option_path,
                app_data_dir=tmp,
                download_dir=tmp,
                option_factory=fake_create_option,
                download_func=fake_download_album,
            )

            service.run_task(task)

            self.assertEqual(task.status, 'success')
            db = ShelfDatabase(os.path.join(tmp, 'shelf.db'))
            db.open()
            try:
                records = db.query_albums('211899')
            finally:
                db.close()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].pdf_path, os.path.join(tmp, '作者A', 'JM211899-作品A.pdf'))
            self.assertEqual(records[0].authors, ['作者A'])

    def test_run_task_moves_pdf_to_first_author_dir_caches_cover_and_removes_images(self):
        from PIL import Image

        from jmcomic_shelf.download_service import DownloadService, DownloadTask

        with TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'jmcomic-option.yml')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write('version: "2.1"\n')
            album_dir = os.path.join(tmp, '作者A', 'JM211899-作品A')
            image_dir = os.path.join(album_dir, '第1章')
            os.makedirs(image_dir)
            Image.new('RGB', (120, 180), 'red').save(os.path.join(image_dir, '00001.jpg'))
            original_pdf = os.path.join(album_dir, 'JM211899-作品A.pdf')
            with open(original_pdf, 'wb') as f:
                f.write(b'%PDF-1.4\n')

            def fake_download_album(jm_id, option):
                return FakeDownloadedAlbum(), object()

            task = DownloadTask(jm_id='211899')
            service = DownloadService(
                option_path,
                app_data_dir=os.path.join(tmp, 'app'),
                download_dir=tmp,
                option_factory=lambda path: object(),
                download_func=fake_download_album,
            )

            service.run_task(task)

            final_pdf = os.path.join(tmp, '作者A', 'JM211899-作品A.pdf')
            final_cover = os.path.join(tmp, 'Cover', 'JM211899-作品A.jpg')
            self.assertEqual(task.status, 'success')
            self.assertTrue(os.path.exists(final_pdf))
            self.assertTrue(os.path.exists(final_cover))
            self.assertFalse(os.path.exists(original_pdf))
            self.assertFalse(os.path.exists(album_dir))

    def test_run_task_accepts_default_feature_pdf_name(self):
        from jmcomic_shelf.download_service import DownloadService, DownloadTask

        with TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'jmcomic-option.yml')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write('version: "2.1"\n')
            original_pdf = os.path.join(tmp, '[JM211899]作品A.pdf')
            with open(original_pdf, 'wb') as f:
                f.write(b'%PDF-1.4\n')

            def fake_download_album(jm_id, option):
                return FakeDownloadedAlbum(), object()

            task = DownloadTask(jm_id='211899')
            service = DownloadService(
                option_path,
                app_data_dir=os.path.join(tmp, 'app'),
                download_dir=tmp,
                option_factory=lambda path: object(),
                download_func=fake_download_album,
            )

            service.run_task(task)

            final_pdf = os.path.join(tmp, '作者A', 'JM211899-作品A.pdf')
            self.assertEqual(task.status, 'success')
            self.assertTrue(os.path.exists(final_pdf))
            self.assertFalse(os.path.exists(original_pdf))

    def test_run_task_fails_when_pdf_plugin_did_not_create_pdf(self):
        from jmcomic_shelf.download_service import DownloadService, DownloadTask

        with TemporaryDirectory() as tmp:
            option_path = os.path.join(tmp, 'jmcomic-option.yml')
            with open(option_path, 'w', encoding='utf-8') as f:
                f.write('version: "2.1"\n')

            def fake_download_album(jm_id, option):
                return FakeDownloadedAlbum(), object()

            task = DownloadTask(jm_id='211899')
            service = DownloadService(
                option_path,
                app_data_dir=tmp,
                download_dir=tmp,
                option_factory=lambda path: object(),
                download_func=fake_download_album,
            )

            service.run_task(task)

            self.assertEqual(task.status, 'failed')
            self.assertIn('PDF', task.error)

    def test_find_pdf_path_finds_long_path_pdf(self):
        from jmcomic_shelf.download_service import DownloadService
        from jmcomic_shelf.path_utils import path_for_open

        with TemporaryDirectory() as tmp:
            title = 'long-title-' * 18
            album_dir = os.path.join(tmp, 'author', 'JM211899-' + title)
            os.makedirs(path_for_open(album_dir))
            pdf_path = os.path.join(album_dir, 'JM211899-' + title + '.pdf')
            with open(path_for_open(pdf_path), 'wb') as f:
                f.write(b'%PDF-1.4\n')

            try:
                service = DownloadService('', download_dir=tmp)

                self.assertEqual(service.find_pdf_path('211899', title), pdf_path)
            finally:
                if os.path.exists(path_for_open(pdf_path)):
                    os.remove(path_for_open(pdf_path))
                if os.path.isdir(path_for_open(album_dir)):
                    os.rmdir(path_for_open(album_dir))

    def test_download_page_clears_input_after_starting_tasks(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.download_page import DownloadPage

        app = QApplication.instance() or QApplication([])
        page = DownloadPage()
        page.input.setPlainText('211899 123456')
        started = []
        page.run_tasks = lambda tasks: started.extend(tasks)

        page.start_download()

        self.assertEqual(page.input.toPlainText(), '')
        self.assertEqual([task.jm_id for task in started], ['211899', '123456'])
        self.assertIsNotNone(app)

    def test_download_page_title_uses_separate_row_from_start_button(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication, QHBoxLayout
        from qfluentwidgets import TitleLabel
        from jmcomic_shelf.ui.download_page import DownloadPage

        app = QApplication.instance() or QApplication([])
        page = DownloadPage()
        main_layout = page.layout()

        self.assertIsInstance(main_layout.itemAt(0).widget(), TitleLabel)
        action_row = main_layout.itemAt(1).layout()
        self.assertIsInstance(action_row, QHBoxLayout)
        self.assertIs(action_row.itemAt(action_row.count() - 1).widget(), page.start_button)
        self.assertIsNot(main_layout.itemAt(0).widget(), page.start_button)
        self.assertIsNotNone(app)

    def test_download_page_resets_progress_when_all_tasks_finish(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.download_service import DownloadTask
        from jmcomic_shelf.ui.download_page import DownloadPage

        app = QApplication.instance() or QApplication([])
        page = DownloadPage()
        page.tasks = [DownloadTask('211899', status='success')]
        page.progress.setValue(100)

        page.on_all_finished()

        self.assertEqual(page.progress.value(), 0)
        self.assertEqual(page.status.text(), '全部已完成。')
        self.assertIsNotNone(app)
