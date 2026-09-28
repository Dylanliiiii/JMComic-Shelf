from test_jmcomic import *
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile


class TestShelfShareService(unittest.TestCase):
    def test_existing_pdf_paths_skips_missing_files(self):
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.share_service import existing_pdf_paths

        with TemporaryDirectory() as tmp:
            present = Path(tmp) / 'present.pdf'
            present.write_bytes(b'%PDF')
            records = [AlbumRecord('1', '有', pdf_path=str(present)), AlbumRecord('2', '无', pdf_path=str(Path(tmp) / 'missing.pdf'))]
            paths, missing = existing_pdf_paths(records)

        self.assertEqual(paths, [str(present)])
        self.assertEqual(missing, ['2'])

    def test_create_pdf_archive_sanitizes_names_and_deduplicates(self):
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.share_service import create_pdf_archive

        with TemporaryDirectory() as tmp:
            first = Path(tmp) / 'a.pdf'
            second = Path(tmp) / 'b.pdf'
            first.write_bytes(b'a')
            second.write_bytes(b'b')
            output = Path(tmp) / 'out.zip'
            records = [
                AlbumRecord('1', 'A:/B', pdf_path=str(first)),
                AlbumRecord('2', 'A:/B', pdf_path=str(second)),
            ]
            create_pdf_archive(records, str(output))
            with ZipFile(output) as archive:
                names = archive.namelist()
                self.assertEqual(names, ['JM1-A__B.pdf', 'JM2-A__B.pdf'])
                self.assertEqual(archive.read(names[0]), b'a')

    def test_file_urls_uses_only_existing_pdf_files(self):
        from jmcomic_shelf.models import AlbumRecord
        from jmcomic_shelf.share_service import file_urls

        with TemporaryDirectory() as tmp:
            present = Path(tmp) / 'present.pdf'
            present.write_bytes(b'%PDF')
            urls, missing = file_urls([
                AlbumRecord('1', '有', pdf_path=str(present)),
                AlbumRecord('2', '无', pdf_path=str(Path(tmp) / 'missing.pdf')),
            ])

        self.assertEqual([Path(url.toLocalFile()) for url in urls], [present])
        self.assertEqual(missing, ['2'])
