from test_jmcomic import *
from unittest.mock import patch


class TestShelfOfficialSitePage(unittest.TestCase):

    def test_page_contains_all_requested_links_and_keeps_bare_domains(self):
        from jmcomic_shelf.ui.official_site_page import OFFICIAL_SITE_GROUPS

        links = [link for group in OFFICIAL_SITE_GROUPS for link in group.links]
        targets = [link.target for link in links]
        displays = [link.display for link in links]

        self.assertEqual(targets, [
            'https://jmcomicog.net/',
            '18comic.vip',
            '18comic.ink',
            'jmcomic-zzz.one',
            'http://jmcomic-zzz.org',
            'https://comic18j-codi.cc',
            'https://comic18j-yodo.club',
            'https://comic18j-codi.club',
            'http://jm-88.cc/ZNPJam',
            'http://gmail.com',
            'http://discord.gg/V74p7HM',
            'http://t.me/hcomic18',
        ])
        self.assertEqual(displays, [
            'https://jmcomicog.net/',
            '18comic.vip',
            '18comic.ink',
            'jmcomic-zzz.one',
            'jmcomic-zzz.org',
            'https://comic18j-codi.cc',
            'https://comic18j-yodo.club',
            'https://comic18j-codi.club',
            'jm-88.cc/ZNPJam',
            're18comic＠gmail.com',
            'discord.gg/V74p7HM',
            't.me/hcomic18',
        ])
        self.assertNotIn('https://18comic.vip', targets)
        self.assertNotIn('https://18comic.ink', targets)
        self.assertNotIn('https://jmcomic-zzz.one', targets)

    def test_open_url_uses_qt_user_input_parser_and_default_browser(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtCore import QUrl
        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.official_site_page import OfficialSitePage

        app = QApplication.instance() or QApplication([])
        page = OfficialSitePage()

        with patch('jmcomic_shelf.ui.official_site_page.QDesktopServices.openUrl', return_value=True) as open_url:
            page.open_url('18comic.vip')

        open_url.assert_called_once_with(QUrl.fromUserInput('18comic.vip'))
        self.assertIn('18comic.vip', page.status.text())
        self.assertIsNotNone(app)

    def test_page_preserves_requested_group_and_route_text(self):
        from jmcomic_shelf.ui.official_site_page import OFFICIAL_SITE_GROUPS

        groups = {group.title: group for group in OFFICIAL_SITE_GROUPS}

        self.assertEqual(groups['国际通用域名'].description, '不支持日本/韩国路线')
        self.assertEqual(groups['东南亚路线建议使用'].description, '')
        self.assertEqual(groups['大陆域名'].description, '请使用 Chrome 浏览器打开')
        self.assertIn('分流1', [link.label for link in groups['大陆域名'].links])
        self.assertIn('分流2', [link.label for link in groups['大陆域名'].links])
        self.assertIn('APP 软件下载安装！！！', groups)
        self.assertEqual(groups['联系方式'].description, '如果地址无法打开，欢迎发送邮件告知：')
        self.assertIn(
            '或是直接到 DC 群或 TG 找管理员处理问题',
            [link.label for link in groups['联系方式'].links],
        )

    def test_open_url_shows_error_when_default_browser_rejects_link(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.official_site_page import OfficialSitePage

        app = QApplication.instance() or QApplication([])
        page = OfficialSitePage()

        with patch('jmcomic_shelf.ui.official_site_page.QDesktopServices.openUrl', return_value=False):
            page.open_url('18comic.vip')

        self.assertEqual(page.status.text(), '无法交给默认浏览器打开：18comic.vip')
        self.assertIsNotNone(app)

    def test_main_window_places_official_site_between_repair_and_settings(self):
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

        from PySide6.QtWidgets import QApplication
        from jmcomic_shelf.ui.main_window import MainWindow

        app = QApplication.instance() or QApplication([])
        window = MainWindow()

        self.assertEqual(window.official_site_page.objectName(), 'officialSitePage')
        self.assertLess(
            window.stackedWidget.indexOf(window.repair_page),
            window.stackedWidget.indexOf(window.official_site_page),
        )
        self.assertLess(
            window.stackedWidget.indexOf(window.official_site_page),
            window.stackedWidget.indexOf(window.settings_page),
        )
        window.close()
        self.assertIsNotNone(app)
