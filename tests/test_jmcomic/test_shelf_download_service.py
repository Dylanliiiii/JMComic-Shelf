from test_jmcomic import *


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
