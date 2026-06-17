# JMComic Shelf 项目协作说明

## 默认语言

本项目的需求说明、开发记录、项目专属 Skill、注释、界面文案和后续新增中文文档默认使用中文。

以下内容可以使用英文：

- 第三方库、API、命令、文件名、协议和代码标识符。
- 面向开源协作或工具识别的文件名与目录名。
- 用户明确要求英文时。

## 开工前必读

每次开始修改代码或文档前，必须先阅读：

- 根目录 `AGENTS.md`。
- `.agents/skills/jmcomic-shelf-project/SKILL.md`。
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`。
- 与本次任务相关的 `docs/superpowers/specs/` 和 `docs/superpowers/plans/` 文件。
- 最近几条 `development-log.md`。

如果发现上述文件存在乱码、过期规则或互相矛盾，必须先修正协作说明或在 `development-log.md` 记录当前判断，再继续做代码更新。不能只凭上一次对话记忆或截图印象修改 UI。

## 项目定位

JMComic Shelf 是基于 `hect0x7/JMComic-Crawler-Python` 的个人漫画下载与本地书库管理工具。

当前项目仍保留上游 Python API、下载器、命令行和插件体系，并在其基础上增加个人本地收藏工作流：

- Windows 双击脚本下载和查看详情。
- 下载后自动转 PDF。
- 下载后维护 `catalog.md` 总目录。
- 总目录按作者分组，并记录封面、标题、JM ID、链接、标签和章节。
- 封面以内嵌 base64 写入 Markdown，方便单独上传目录文件。
- 下载路径尽量避免 Windows 长路径问题。
- 桌面端用 PySide6 + QFluentWidgets 封装书库、下载、查看详情和设置页。

后续目标是逐步封装为桌面应用，降低手写命令和 YAML 配置的成本。

## 上游关系

- 当前仓库：`https://github.com/Dylanliiiii/JMComic-Shelf`
- 上游仓库：`https://github.com/hect0x7/JMComic-Crawler-Python`
- 本地 remote 约定：
  - `origin` 指向 Dylanliiiii/JMComic-Shelf。
  - `upstream` 指向 hect0x7/JMComic-Crawler-Python。

本项目应明确保留对上游项目的致谢和来源说明，不应把上游能力描述成完全原创。

## 参考项目

桌面 UI 和项目协作规则参考用户提供的：

- `https://github.com/Dylanliiiii/LaunchDock`

只参考其 PySide6 + QFluentWidgets 的桌面工具组织方式、深色 Fluent 风格、项目协作说明结构和技术栈记录方式，不照搬 LaunchDock 的业务、图标、品牌素材或启动坞功能。

## 项目专属 Skill

本项目包含以下只服务于 JMComic Shelf 的项目专属 Skill：

- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`

这些 Skill 使用仓库相对路径，不能写成本机绝对路径。后续如果新增、修改、删除或移动任何 Skill，必须同步更新本文件中的项目专属 Skill 说明。

## 敏感配置

`jmcomic-option.yml` 是本地配置文件，可能包含账号、密码、下载目录、代理等个人信息，必须保持在 `.gitignore` 中。

不得提交以下内容：

- JMComic 账号密码。
- cookie、token、代理凭据。
- 用户本地下载目录中的漫画、PDF、封面、`catalog.md`。
- 任何只适用于维护者电脑的绝对路径配置。

文档中如需展示配置，应使用脱敏示例。

## 当前工作流约定

### 下载目录

当前推荐路径规则：

```yaml
dir_rule:
  base_dir: D:/path/to/JMComic
  rule: Bd / Aauthor / JM{Aid}-{Atitle} / 第{Pindex}章
  normalize_zh: null
```

说明：

- 保留作者和作品标题，便于人工浏览。
- 章节目录使用短名称，避免标题重复导致 Windows 路径过长。
- 不强制繁简转换，标题、作者和标签保持来源文本。

### PDF

下载完成后通过 `img2pdf` 插件生成 PDF。PDF 命名保持 `JM号-作品名.pdf`。

### Markdown 总目录

`catalog` 插件负责维护下载根目录下的 `catalog.md`：

- 按作者分组。
- 每个作者下独立编号。
- 同一作品如有多个作者，会在每个作者下各登记一份索引。
- 同一作者下按 JM ID 去重更新，不重复追加。
- 封面优先使用本次下载成功的第一章第一张图片。
- 封面以内嵌 base64 写入 Markdown。
- 默认封面宽度为 `120`。

### 桌面端索引

桌面端使用 SQLite 作为结构化索引，默认在 `%APPDATA%/JMComic Shelf/shelf.db`。

- `catalog.md` 继续作为用户可直接打开的 Markdown 总目录，不作为桌面端唯一数据源。
- 书库页必须能从当前设置的下载目录递归扫描现有漫画和 PDF，并同步到 SQLite。
- 启动、切换回书库页、保存设置后重建索引，都应能显示新下载或手动放入下载目录的作品。
- 扫描规则至少支持 `作者 / JM{Aid}-{Atitle} / 第{Pindex}章 / 图片` 以及下载根目录或子目录中的 `JM{Aid}-{Atitle}.pdf`。

### Windows 脚本

- `download-jmcomic.bat`：输入一个或多个 JM 号后下载。
- `view-jmcomic.bat`：输入 JM 号后查看详情。
- `start-jmcomic-shelf.bat`：从源码仓库启动桌面端。

脚本应保持简单，适合不熟悉 PowerShell 的用户使用。

## 桌面 UI 要求

桌面端技术栈固定为 PySide6 + QFluentWidgets，除非用户明确要求重构技术栈。

UI 必须遵守以下方向：

- 整体是工具型 Windows 桌面应用，不是网页后台、营销页或 HTML 风格页面。
- 风格参考 Windows 11 Settings / WinUI 3 / QFluentWidgets 深色 Fluent 应用。
- 左侧使用 QFluentWidgets 的 `FluentWindow` / 导航接口，导航项包含图标和中文文字。
- 右侧主区域使用透明背景、低对比度表面和 QFluentWidgets 原生控件。
- 页面和卡片优先使用 `TitleLabel`、`SubtitleLabel`、`CaptionLabel`、`CardWidget`、`SmoothScrollArea`、`PrimaryPushButton`、`PushButton` 等 QFluentWidgets 控件。
- 使用青色作为强调色，当前建议 `#00c8d7`。
- 不要给全局 `QWidget` 强行设置白底或黑底；避免破坏 QFluentWidgets 自带主题。
- 不要出现大块突兀黑色矩形、白色画布、黑底白字说明条或网页式分区。
- 页面区域背景应透明或与主窗口一致；卡片负责信息分组。
- 设置页和列表页使用横向或网格卡片，卡片圆角和间距克制。
- 书库封面必须完整等比例显示，不裁剪、不截断。
- 文案必须是正常中文，不能提交 mojibake 乱码。

如果 UI 截图出现“白色大纸 + 黑色内容块”或中文乱码，应视为阻断级缺陷，先修 UI 基础样式和编码，再继续加功能。

## 技术栈与当前限制

当前已确认技术栈与限制：

- 仓库内部分历史中文文档和测试数据出现 mojibake 乱码，需要逐步清理；新增或本次修改过的项目规则、界面文案和开发记录必须保持正常 UTF-8 中文。
- 桌面端仍是 PySide6 + QFluentWidgets 实现，不是原生 WinUI 3；因此 UI 要用 QFluentWidgets 模拟 Fluent 风格，不能混用网页式样式表堆色块。
- 书库索引不能只依赖下载完成后的 SQLite 写入；必须支持从现有下载目录重建，否则用户已有漫画不会显示。
- `jmcomic-option.yml` 是真实本地配置，测试和文档不能泄露其中内容。
- 下载目录可能很大，后续需要考虑扫描性能、增量索引和后台线程；当前先保证正确显示。

## 质量要求

- 修改下载、PDF、目录插件或路径规则时，优先添加或更新测试。
- 修改 `CatalogPlugin` 时至少运行：

```powershell
python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v
python -m py_compile src\jmcomic\jm_plugin.py
```

- 修改桌面端索引、书库扫描或 UI 时，至少运行相关 `test_shelf_*.py` 测试和 `py_compile`。
- 修改 README、AGENTS、Skill 或开发记录时，至少检查相关链接、路径和项目名是否一致。
- 文档或开发记录中如果提到用户提供的参考项目、教程、工具或外部资料，应写出完整 URL。
- 每次修改代码或文档后，检查 README、`AGENTS.md`、项目专属 Skill、开发记录是否需要同步更新。
- 每次交付附带新增功能、修改文件结构、改变工作流或调整用户可见行为时，不能只更新 `development-log.md`；必须同步判断 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/` 是否需要更新，并在开发记录中写明检查结果。

## 开发记录

每次生成或修改代码、脚本、README、AGENTS 或项目专属 Skill 时，都要同步更新 `development-log.md`。

`development-log.md` 不只记录已经落地的代码或文档修改；当进入重要规划阶段、形成关键设计思路、确认技术路线、拆分里程碑、发现技术栈限制或暂停在某个阶段时，也应记录当前进度和下一步。

记录内容应包括：

- 修改日期和具体时间。
- 修改范围。
- 涉及文件。
- 具体做了什么。
- 如属于规划或设计阶段，需要记录当前结论、待确认问题和下一步。
- 是否运行验证或测试。
- 如果没有运行验证或测试，需要说明原因。

日常修改不记录版本号。只有用户明确要求发版、打包或创建 release 时，才使用版本号记录。

## GitHub 维护规则

- 普通代码或文档修改完成并验证后，直接 commit 并 push 到 GitHub。
- 默认推送到 `origin master`。
- 不自动创建 tag，不自动创建 GitHub Release。
- 只有用户明确要求“release / 发版 / 打包 / 发布新版本”时，才准备 release。
- 如果用户表达“更新一下”“更新 GitHub”等，按普通 commit + push 处理。
- 提交前确认 `jmcomic-option.yml` 仍是 ignored，且没有账号密码进入 diff。

## 未来方向

- 将当前命令行和 bat 脚本流程封装为桌面应用。
- 提供图形化配置向导，减少手写 YAML。
- 提供下载任务管理、失败重试和补图入口。
- 提供本地书库浏览、筛选、搜索和标签管理。
- 在正式桌面应用阶段再设计 release、打包和版本更新规则。
