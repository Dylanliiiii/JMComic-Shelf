# “禁漫官网”功能页设计

## 背景

JMComic Shelf 当前左侧导航包含“本地书库”“禁漫下载”“禁漫预览”“书库修复”和底部“设置”。用户希望在“书库修复”和“设置”之间新增“禁漫官网”入口，集中展示禁漫发布页、分流域名、APP 下载地址以及官方联系方式，并通过系统默认浏览器打开所选地址。

## 目标

- 在左侧导航新增“禁漫官网”，位置位于“书库修复”之后、底部“设置”之前。
- 使用 `FluentWindow.addSubInterface()` 和 QFluentWidgets 内置图标，保持现有导航样式。
- 页面使用 QFluentWidgets 原生标题、滚动区域、卡片和链接按钮，保持深色 Fluent 工具应用观感。
- 完整保留用户提供的说明文字、域名、邮箱、Discord 和 Telegram 地址。
- 点击地址后交给系统默认浏览器打开，不在应用内嵌网页。
- 不对 `18comic.vip`、`18comic.ink`、`jmcomic-zzz.one` 三个裸域名硬编码补写 `https://`；显示和保存的地址保持原样，点击时使用 Qt 的用户输入 URL 解析能力。

## 页面结构

页面文件为 `src/jmcomic_shelf/ui/official_site_page.py`，对象名为 `officialSitePage`。

页面顶部包含：

- 标题：`禁漫官网`。
- 说明：提示链接将在系统默认浏览器中打开，具体可用性可能受地区和网络路线影响。

正文使用 `SmoothScrollArea` 承载以下分组卡片：

1. 禁漫发布页
   - `https://jmcomicog.net/`
2. 国际通用域名
   - 说明：`不支持日本/韩国路线`
   - `18comic.vip`
   - `18comic.ink`
3. 东南亚路线
   - 说明：`东南亚路线建议使用`
   - `jmcomic-zzz.one`
   - `http://jmcomic-zzz.org`
4. 大陆域名
   - 说明：`请使用 Chrome 浏览器打开`
   - `https://comic18j-codi.cc`
   - 分流 1：`https://comic18j-yodo.club`
   - 分流 2：`https://comic18j-codi.club`
5. APP 软件下载安装
   - `http://jm-88.cc/ZNPJam`
6. 联系方式
   - 说明：`如果地址无法打开，欢迎发送邮件告知：`
   - 邮箱：`re18comic＠gmail.com`，对应浏览器地址 `http://gmail.com`
   - 说明：`或是直接到 DC 群或 TG 找管理员处理问题`
   - Discord：`http://discord.gg/V74p7HM`
   - Telegram：`http://t.me/hcomic18`

卡片只负责信息分组，不使用网页式大色块。地址按钮显示原始地址文本，避免用户无法判断将要打开的目标。

## 链接打开行为

- 页面统一通过一个小型打开函数处理地址，便于测试和错误隔离。
- 使用 `QUrl.fromUserInput(raw_url)` 解析用户提供的字符串，因此裸域名无需在项目数据中补写协议。
- 使用 `QDesktopServices.openUrl()` 交给 Windows 默认浏览器。
- 如果 Qt 无法接受某个地址，页面显示中文状态提示，不让应用崩溃。
- 网站返回 403、地区限制或浏览器安全拦截属于目标站点和网络环境行为；应用只保证把地址正确交给默认浏览器。

## 技术边界

- 不引入 Qt WebEngine，不在应用内嵌浏览器。
- 不主动请求、抓取或缓存官网内容。
- 不自动探测域名可用性，避免页面启动时产生网络请求或因地区网络差异误判。
- 不修改下载、预览、账号、SQLite 或本地漫画工作流。

## 测试要求

- 主窗口存在 `official_site_page`，对象名为 `officialSitePage`，堆栈顺序位于 `repair_page` 之后和 `settings_page` 之前。
- 页面数据包含用户提供的全部地址，三个裸域名保持不带协议。
- 点击链接时使用 `QUrl.fromUserInput()` 的解析结果调用 `QDesktopServices.openUrl()`。
- 页面使用可滚动 Fluent 卡片布局，链接按钮显示原始地址文本。
- 完整运行 `test_shelf_*.py` 和桌面端 `py_compile`。

## 文档同步判断

本次新增用户可见导航页和使用入口，需要同步更新：

- `README.md`：桌面端能力列表增加“禁漫官网”。
- `AGENTS.md`：桌面 UI 页面结构和默认浏览器打开约定。
- `.agents/skills/jmcomic-shelf-project/SKILL.md`：桌面端页面模块说明。
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`：补充页面结构。
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`：补充既有桌面端实施基线。
- `development-log.md`：记录设计、实现、验证和版本判断。

本次是日常功能更新，不更新项目版本号，不创建 tag，也不发布 GitHub Release。
