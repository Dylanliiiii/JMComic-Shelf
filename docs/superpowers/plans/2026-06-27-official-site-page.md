# “禁漫官网”功能页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在桌面端新增“禁漫官网”导航页，以 Fluent 分组卡片展示用户提供的全部官方地址，并通过系统默认浏览器打开。

**Architecture:** 新页面 `OfficialSitePage` 自带不可变链接数据、卡片渲染和统一的 `open_url()` 入口；裸域名保持原始文本并通过 `QUrl.fromUserInput()` 解析，最终交给 `QDesktopServices.openUrl()`。`MainWindow` 仅负责实例化页面、使用 `FluentIcon.GLOBE` 注册导航并纳入主题刷新。

**Tech Stack:** Python、PySide6、QFluentWidgets、`unittest`。

---

## File Structure

- Create: `src/jmcomic_shelf/ui/official_site_page.py`
  - 保存官网分组数据，渲染 Fluent 滚动卡片，并将链接交给系统默认浏览器。
- Create: `tests/test_jmcomic/test_shelf_official_site_page.py`
  - 覆盖链接数据、裸域名、默认浏览器调用和主窗口导航顺序。
- Modify: `src/jmcomic_shelf/ui/main_window.py`
  - 注册 `OfficialSitePage`，位置在“书库修复”和底部“设置”之间。
- Modify: `README.md`
  - 在桌面端功能中说明“禁漫官网”入口。
- Modify: `assets/readme/README-en.md`
  - 同步英文 README 的桌面端能力概述。
- Modify: `AGENTS.md`
  - 记录新增导航页和默认浏览器打开规则。
- Modify: `.agents/skills/jmcomic-shelf-project/SKILL.md`
  - 更新桌面 UI 模块说明和链接页边界。
- Modify: `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
  - 补充“禁漫官网”页面结构。
- Modify: `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
  - 更新桌面端基线和页面任务。
- Modify: `development-log.md`
  - 将规划记录补充为完整实现和验证记录。
- Modify: `TASKS.md`
  - 按步骤更新状态，全部验证通过后清空。

## Task 1: 页面行为和导航 RED 测试

**Files:**
- Create: `tests/test_jmcomic/test_shelf_official_site_page.py`
- Create later: `src/jmcomic_shelf/ui/official_site_page.py`
- Modify later: `src/jmcomic_shelf/ui/main_window.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_jmcomic/test_shelf_official_site_page.py`:

```python
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
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_official_site_page -v
```

Expected: FAIL or ERROR because `jmcomic_shelf.ui.official_site_page` and `window.official_site_page` do not exist.

## Task 2: 实现 OfficialSitePage 并接入导航

**Files:**
- Create: `src/jmcomic_shelf/ui/official_site_page.py`
- Modify: `src/jmcomic_shelf/ui/main_window.py`
- Test: `tests/test_jmcomic/test_shelf_official_site_page.py`

- [ ] **Step 1: Create the Fluent page**

Create `src/jmcomic_shelf/ui/official_site_page.py`:

```python
from dataclasses import dataclass

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, CaptionLabel, PushButton, SmoothScrollArea, SubtitleLabel, TitleLabel

from .styles import TRANSPARENT_SCROLL_STYLE, apply_page_style


@dataclass(frozen=True)
class OfficialSiteLink:
    label: str
    display: str
    target: str


@dataclass(frozen=True)
class OfficialSiteGroup:
    title: str
    description: str
    links: tuple[OfficialSiteLink, ...]


OFFICIAL_SITE_GROUPS = (
    OfficialSiteGroup('禁漫发布页', '', (
        OfficialSiteLink('', 'https://jmcomicog.net/', 'https://jmcomicog.net/'),
    )),
    OfficialSiteGroup('国际通用域名', '不支持日本/韩国路线', (
        OfficialSiteLink('', '18comic.vip', '18comic.vip'),
        OfficialSiteLink('', '18comic.ink', '18comic.ink'),
    )),
    OfficialSiteGroup('东南亚路线建议使用', '', (
        OfficialSiteLink('', 'jmcomic-zzz.one', 'jmcomic-zzz.one'),
        OfficialSiteLink('', 'jmcomic-zzz.org', 'http://jmcomic-zzz.org'),
    )),
    OfficialSiteGroup('大陆域名', '请使用 Chrome 浏览器打开', (
        OfficialSiteLink('大陆域名', 'https://comic18j-codi.cc', 'https://comic18j-codi.cc'),
        OfficialSiteLink('分流1', 'https://comic18j-yodo.club', 'https://comic18j-yodo.club'),
        OfficialSiteLink('分流2', 'https://comic18j-codi.club', 'https://comic18j-codi.club'),
    )),
    OfficialSiteGroup('APP 软件下载安装！！！', '', (
        OfficialSiteLink('', 'jm-88.cc/ZNPJam', 'http://jm-88.cc/ZNPJam'),
    )),
    OfficialSiteGroup('联系方式', '如果地址无法打开，欢迎发送邮件告知：', (
        OfficialSiteLink('邮箱', 're18comic＠gmail.com', 'http://gmail.com'),
        OfficialSiteLink('或是直接到 DC 群或 TG 找管理员处理问题', 'discord.gg/V74p7HM', 'http://discord.gg/V74p7HM'),
        OfficialSiteLink('Telegram', 't.me/hcomic18', 'http://t.me/hcomic18'),
    )),
)


class OfficialSitePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('officialSitePage')
        self.link_buttons = {}
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)
        layout.addWidget(TitleLabel('禁漫官网', self))

        note = CaptionLabel('点击地址后将在系统默认浏览器中打开；具体可用性可能受地区和网络路线影响。', self)
        note.setWordWrap(True)
        layout.addWidget(note)

        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(self.scroll.Shape.NoFrame)
        self.scroll.setStyleSheet(TRANSPARENT_SCROLL_STYLE)

        content = QWidget(self.scroll)
        content.setStyleSheet('background: transparent;')
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 14, 0)
        content_layout.setSpacing(12)
        for group in OFFICIAL_SITE_GROUPS:
            content_layout.addWidget(self._create_group_card(group, content))
        content_layout.addStretch(1)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll, 1)

        self.status = CaptionLabel('', self)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

    def _create_group_card(self, group: OfficialSiteGroup, parent):
        card = CardWidget(parent)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)
        card_layout.addWidget(SubtitleLabel(group.title, card))
        if group.description:
            description = CaptionLabel(group.description, card)
            description.setWordWrap(True)
            card_layout.addWidget(description)
        for link in group.links:
            row = QHBoxLayout()
            if link.label:
                row.addWidget(BodyLabel(link.label, card))
            else:
                row.addStretch(1)
            button = PushButton(link.display, card)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, target=link.target: self.open_url(target))
            self.link_buttons[link.target] = button
            row.addWidget(button)
            card_layout.addLayout(row)
        return card

    def open_url(self, raw_url: str):
        url = QUrl.fromUserInput(raw_url)
        if not QDesktopServices.openUrl(url):
            self.status.setText(f'无法交给默认浏览器打开：{raw_url}')
            return
        self.status.setText(f'已交给默认浏览器打开：{raw_url}')
```

- [ ] **Step 2: Register the page in MainWindow**

Modify `src/jmcomic_shelf/ui/main_window.py`:

```python
from .official_site_page import OfficialSitePage
```

Instantiate after `RepairPage`:

```python
self.official_site_page = OfficialSitePage(self)
```

Set its object name and register it after `书库修复`:

```python
self.official_site_page.setObjectName('officialSitePage')
self.addSubInterface(self.official_site_page, FluentIcon.GLOBE, '禁漫官网')
```

Include it in `refresh_theme_styles()`:

```python
for page in (
    self.library_page,
    self.download_page,
    self.detail_page,
    self.repair_page,
    self.official_site_page,
    self.settings_page,
):
    apply_page_style(page)
```

- [ ] **Step 3: Run focused tests and verify GREEN**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_official_site_page -v
```

Expected: 5 tests pass.

- [ ] **Step 4: Commit the behavior change**

```powershell
git add src/jmcomic_shelf/ui/official_site_page.py src/jmcomic_shelf/ui/main_window.py tests/test_jmcomic/test_shelf_official_site_page.py
git commit -m "feat: add official site page"
```

## Task 3: 同步用户文档和项目规则

**Files:**
- Modify: `README.md:35-48,87-123`
- Modify: `assets/readme/README-en.md`
- Modify: `AGENTS.md:30-39,141-160`
- Modify: `.agents/skills/jmcomic-shelf-project/SKILL.md:61-80,93-111`
- Modify: `docs/superpowers/specs/2026-06-17-desktop-app-design.md:88-103`
- Modify: `docs/superpowers/plans/2026-06-18-desktop-app-v1.md:7-19,72-82`
- Modify: `development-log.md`
- Modify: `TASKS.md`

- [ ] **Step 1: Update README files**

Add this Chinese capability near the existing repair feature:

```markdown
- “禁漫官网”集中展示发布页、分流域名、APP 下载和联系方式，点击后使用系统默认浏览器打开。
```

Add the equivalent English capability to `assets/readme/README-en.md`:

```markdown
- The Official JMComic page groups the release page, mirror domains, app download, and support contacts, opening links in the system browser.
```

- [ ] **Step 2: Update AGENTS and project skill**

Record that `ui/official_site_page.py` is a QFluentWidgets card page registered with `addSubInterface()`, and that it keeps user-provided bare domains unchanged while `QUrl.fromUserInput()` and `QDesktopServices.openUrl()` hand clicks to the system browser. State that the page performs no startup network probes and embeds no web engine.

- [ ] **Step 3: Update the desktop spec and v1 plan**

Add a “禁漫官网” section to `docs/superpowers/specs/2026-06-17-desktop-app-design.md` covering navigation order, grouped cards, raw-domain preservation, default-browser behavior, and no embedded browser.

Add `ui/official_site_page.py` to the existing module baseline and a new official-site page item to `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`.

- [ ] **Step 4: Update planning state**

Mark design, plan, RED tests, implementation, and documentation items complete in `TASKS.md`. Expand the existing `2026-06-27` development-log entry with all touched files, the RED/GREEN evidence, documentation synchronization judgment, and the statement that this is a normal feature update without version bump or Release.

## Task 4: 完整验证、任务清理和发布普通更新

**Files:**
- Modify: `TASKS.md`
- Modify: `development-log.md`

- [ ] **Step 1: Run focused and full tests**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_official_site_page -v
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v
```

Expected: focused tests pass, then all shelf tests pass.

- [ ] **Step 2: Run syntax compilation**

Run:

```powershell
$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\repair_service.py src\jmcomic_shelf\database.py src\jmcomic_shelf\delete_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\repair_page.py src\jmcomic_shelf\ui\official_site_page.py
```

Expected: exit code 0.

- [ ] **Step 3: Run safety and documentation checks**

Run:

```powershell
rg -n "JMComic Shelf|official_site_page|禁漫官网|https://github.com/Dylanliiiii/LaunchDock" README.md assets/readme/README-en.md AGENTS.md .agents/skills/jmcomic-shelf-project/SKILL.md docs/superpowers/specs docs/superpowers/plans development-log.md
git diff --check
git check-ignore -v jmcomic-option.yml
git status --short
```

Expected: names and paths are consistent, no whitespace errors, the real configuration remains ignored, and only intended files are modified.

- [ ] **Step 4: Clear TASKS after verification**

Restore `TASKS.md` to the standard header followed by `暂无进行中任务。` only after every verification command succeeds.

- [ ] **Step 5: Commit and push the remaining documentation**

```powershell
git add README.md assets/readme/README-en.md AGENTS.md .agents/skills/jmcomic-shelf-project/SKILL.md docs/superpowers/specs/2026-06-17-desktop-app-design.md docs/superpowers/plans/2026-06-18-desktop-app-v1.md docs/superpowers/plans/2026-06-27-official-site-page.md development-log.md TASKS.md
git commit -m "docs: document official site page"
git push origin master
```

Expected: both commits are present on `origin/master`; no tag or GitHub Release is created.

## Self-Review

- Spec coverage: tasks cover navigation order, Fluent card layout, every requested address, bare-domain preservation, default-browser behavior, error status, tests, documentation, development log, task ledger, security checks, commit, and push.
- Placeholder scan: the plan contains no deferred implementation markers or unspecified code steps.
- Type consistency: `OfficialSiteLink`, `OfficialSiteGroup`, `OFFICIAL_SITE_GROUPS`, `OfficialSitePage`, `link_buttons`, `open_url()`, and `official_site_page` use the same names across tests and implementation.
