from test_jmcomic import *
from unittest.mock import patch


class TestShelfFileActions(unittest.TestCase):

    def test_open_pdf_accepts_long_path_that_needs_prefix(self):
        from jmcomic_shelf.file_actions import open_pdf

        long_path = 'D:/' + ('long-title/' * 30) + 'JM123456-title.pdf'

        with patch('jmcomic_shelf.file_actions.path_exists', return_value=True):
            with patch('jmcomic_shelf.file_actions.path_for_open', return_value='//?/D:/long.pdf') as path_for_open:
                with patch('os.startfile') as startfile:
                    open_pdf(long_path)

        path_for_open.assert_called_once_with(long_path)
        startfile.assert_called_once_with('//?/D:/long.pdf')
