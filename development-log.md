# Development Log

## 2026-06-18 01:26:23 +08:00

### 修改范围

- 桌面应用 UI 可用性修复
- 下载与查看详情错误提示
- 设置页路径说明与配置同步
- 源码启动默认配置路径
- 开发记录

### 涉及文件

- `src/jmcomic_shelf/settings.py`
- `src/jmcomic_shelf/download_service.py`
- `src/jmcomic_shelf/detail_service.py`
- `src/jmcomic_shelf/option_service.py`
- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `src/jmcomic_shelf/ui/download_page.py`
- `src/jmcomic_shelf/ui/detail_page.py`
- `src/jmcomic_shelf/ui/settings_page.py`
- `src/jmcomic_shelf/ui/styles.py`
- `start-jmcomic-shelf.bat`
- `tests/test_jmcomic/test_shelf_settings.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `tests/test_jmcomic/test_shelf_detail_service.py`
- `tests/test_jmcomic/test_shelf_option_service.py`
- `development-log.md`

### 具体内容

- 根据用户实际试用反馈，移除桌面页面中由 QScrollArea/QTableWidget/FluentWindow 默认样式暴露出的深色大块背景，改为浅色 Windows 风格工作区。
- 将主窗口从 `FluentWindow` 默认导航改为项目可控的浅色左侧栏，默认展开，宽度收敛到适配导航文字；导航项包含主标题和一句小字说明。
- 书库、下载、查看详情、设置页均补充一句简短操作说明，避免只有标题和输入框。
- 下载服务在 `jmcomic-option.yml` 未选择或路径不存在时，直接返回中文可读错误，不再把空路径传给上游导致 `unknown mode: '', acceptable modes=['yml', 'json', 'pickle']`。
- 查看详情服务同样校验配置文件路径，详情页捕获异常并显示在页面中，避免用户点击后无反应。
- 设置页改为分块说明：下载目录用于保存漫画图片、PDF 和 `catalog.md`；配置文件是 `jmcomic-option.yml`；应用数据目录用于 `settings.json`、`shelf.db` 和封面缩略图缓存。
- 保存设置时，如果选择了 `jmcomic-option.yml` 和下载目录，会同步更新配置文件中的 `dir_rule.base_dir`，让 UI 里设置的下载目录真正作用于下载流程。
- 源码启动脚本 `start-jmcomic-shelf.bat` 新增 `JMCOMIC_SHELF_PROJECT_DIR` 环境变量；桌面端默认配置文件路径会自动指向源码根目录下的 `jmcomic-option.yml`，减少首次使用的猜测成本。

### 验证情况

- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_settings tests.test_jmcomic.test_shelf_download_service tests.test_jmcomic.test_shelf_detail_service tests.test_jmcomic.test_shelf_option_service -v`，结果通过。
- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_library_page -v`，结果通过。
- 已运行 `python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\settings.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\option_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，结果通过。
- 已用 offscreen 主窗口截图检查深色像素比例，深色区域约 `0.0046`，用于确认不再出现大面积黑色背景。
- 本次未实际触发下载，不涉及账号密码、cookie、token、代理凭据、下载内容、PDF、封面缓存或本地 `catalog.md`。

## 2026-06-18 01:05:32 +08:00

### 修改范围

- 桌面应用源码启动脚本
- README 桌面端启动说明
- 开发记录

### 涉及文件

- `start-jmcomic-shelf.bat`
- `README.md`
- `assets/readme/README-en.md`
- `development-log.md`

### 具体内容

- 用户直接在项目根目录运行 `python -m jmcomic_shelf.app` 时，当前 Python 环境找不到 `src/jmcomic_shelf`，报错 `ModuleNotFoundError: No module named 'jmcomic_shelf'`。
- 根因是桌面端代码当前仍以源码形式放在 `src/` 下，尚未通过 `pip install -e .` 或正式打包安装到 Python 环境；直接 `python -m ...` 不会自动把 `src` 加入模块搜索路径。
- 新增 `start-jmcomic-shelf.bat`，双击时自动设置 `PYTHONPATH=%~dp0src`，再运行 `python -m jmcomic_shelf.app`，让源码仓库阶段也能直接启动桌面应用。
- README 和英文 README 补充说明：源码仓库阶段优先双击 `start-jmcomic-shelf.bat`；安装包或 editable install 后才使用 `jmcomic-shelf` 命令。

### 验证情况

- 已运行 `$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; python -c "from PySide6.QtWidgets import QApplication; from jmcomic_shelf.ui.main_window import MainWindow; app=QApplication([]); window=MainWindow(); print(window.windowTitle())"`，结果输出 `JMComic Shelf`。
- 本次未实际触发下载，不涉及账号密码、cookie、token、代理凭据、下载内容、PDF、封面缓存或本地 `catalog.md`。

## 2026-06-18 00:45:23 +08:00

### 修改范围

- 桌面应用 v1 基础实现
- 桌面书库 SQLite 索引
- 非裁剪封面缩略图缓存
- 下载、详情、文件操作服务
- PySide6 + QFluentWidgets 桌面入口和页面
- README 桌面端说明
- 开发记录

### 涉及文件

- `src/jmcomic_shelf/__init__.py`
- `src/jmcomic_shelf/paths.py`
- `src/jmcomic_shelf/settings.py`
- `src/jmcomic_shelf/models.py`
- `src/jmcomic_shelf/database.py`
- `src/jmcomic_shelf/cover_cache.py`
- `src/jmcomic_shelf/index_service.py`
- `src/jmcomic_shelf/download_service.py`
- `src/jmcomic_shelf/detail_service.py`
- `src/jmcomic_shelf/file_actions.py`
- `src/jmcomic_shelf/app.py`
- `src/jmcomic_shelf/ui/`
- `src/jmcomic/jm_plugin.py`
- `tests/test_jmcomic/test_shelf_settings.py`
- `tests/test_jmcomic/test_shelf_database.py`
- `tests/test_jmcomic/test_shelf_cover_cache.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- `tests/test_jmcomic/test_jm_plugin.py`
- `pyproject.toml`
- `setup.py`
- `README.md`
- `assets/readme/README-en.md`
- `development-log.md`

### 具体内容

- 新增 `jmcomic_shelf` 桌面端包，提供 Windows 用户数据目录、`settings.json`、`shelf.db` 和封面缓存目录的统一路径入口。
- 新增 `ShelfSettings`，保存当前下载目录、`jmcomic-option.yml` 路径和应用数据目录；桌面端第一版仍只管理当前设置里的一个下载目录。
- 新增 `ShelfDatabase` SQLite 索引，保存作品、作者、标签、章节、PDF 路径和封面缩略图路径；空查询对应 UI 的 `全部`，不把 `全部` 写成真实标签。
- 新增 `CoverCache`，只生成桌面端使用的 JPEG 缩略图，按宽度等比例缩小和压缩画质，不裁剪、不截断、不保存原图副本。
- 新增 `record_from_album` 和 `group_by_author`，复用现有 `CatalogPlugin.build_album_info()`，让 Markdown 总目录和桌面 SQLite 索引共享同一套作者、标签和章节提取逻辑。
- 在 `src/jmcomic/jm_plugin.py` 中新增 `shelf_index` 插件，用于下载后写入桌面端 SQLite 索引；原 `catalog` 插件继续维护下载目录下的 `catalog.md`。
- 新增下载服务，支持空格、逗号和换行输入多个 JM 号，保留失败任务重试状态。
- 新增详情服务和文件操作服务，用于获取单个 JM 号详情、打开 PDF、在文件资源管理器中定位 PDF。
- 新增 `jmcomic-shelf` 命令和 PySide6 + QFluentWidgets 依赖，建立左侧图标文字导航：`书库`、`下载`、`查看详情`、`设置`。
- 书库页实现 `全部`、JM 号/作者/标签搜索、作者分组、封面卡片、点击打开 PDF 和右键资源管理器定位；当 `%APPDATA%/JMComic Shelf/` 暂不可写或索引不可读时，页面显示空状态而不是导致应用启动失败。
- 下载页实现多 JM 号输入、任务表格和失败重试按钮。
- 查看详情页实现单 JM 号查询，不保存查询历史；本地索引有 PDF 时可打开或定位。
- 设置页实现下载目录、配置文件、应用数据目录展示和封面缓存清理；重建索引按钮先作为后续扫描服务入口预留。
- README 和英文 README 补充桌面端命令、数据位置、下载内容与 `catalog.md` 的保留规则，并记录完整参考链接：`https://github.com/ok-oldking/ok-script`、`https://github.com/ok-oldking/pyappify`。

### 验证情况

- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_settings -v`，结果通过。
- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_database -v`，结果通过。
- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_cover_cache -v`，结果通过。
- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_index_service -v`，结果通过。
- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_download_service -v`，结果通过。
- 已运行 `python -m unittest tests.test_jmcomic.test_shelf_library_page -v`，结果通过。
- 已运行 `python -m unittest discover -s tests -p test_jm_plugin.py -k shelf_index -v`，结果通过。
- 已运行 `python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v`，结果通过。
- 已运行 `python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py`，结果通过。
- 已运行主窗口 offscreen 构造检查，能成功实例化并输出 `JMComic Shelf`。
- 本次未提交 `jmcomic-option.yml`、账号密码、cookie、token、代理凭据、下载内容、PDF、封面缓存或本地 `catalog.md`。

## 2026-06-18 00:03:12 +08:00

### 修改范围

- 外部参考链接记录规则
- 桌面应用设计文档确认项收束
- 桌面应用 v1 实现计划
- 项目协作说明
- 项目专属 Skill
- 开发记录

### 涉及文件

- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 用户确认设计文档中的三个默认建议：下载页第一版支持失败重试按钮；查看详情页第一版不保存查询历史；设置页第一版只显示应用数据目录和清理缓存，不做应用数据目录迁移。
- 将设计文档中的“待用户确认”改为“已确认决策”，避免后续实现计划存在悬空项。
- 在设计文档中补充完整参考链接：`ok-oldking/ok-script` 使用 `https://github.com/ok-oldking/ok-script`，`ok-oldking/pyappify` 使用 `https://github.com/ok-oldking/pyappify`。
- 用户要求后续文档或开发记录引用参考项目、教程、工具或外部资料时，应尽量保留完整 URL，不能只写项目名；已同步写入 `AGENTS.md` 和项目专属 Skill，方便新对话或其他智能体追溯来源。
- 新增桌面应用 v1 实现计划，拆分为设置路径、SQLite、封面缓存、索引服务、索引插件、下载服务、文件操作、桌面入口、UI 页面、README 和最终验证等任务。

### 验证情况

- 本次为协作规则、设计文档和实现计划更新，未运行代码单元测试。
- 已检查文档内容未记录账号、密码、cookie、token、真实本地下载目录、PDF 或 `catalog.md` 内容。

## 2026-06-17 23:57:24 +08:00

### 修改范围

- 桌面应用 v1 设计文档
- 开发记录

### 涉及文件

- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `development-log.md`

### 具体内容

- 新增桌面应用 v1 设计文档，收束目前已确认的 PySide6 + QFluentWidgets 技术方向、方案 A 左侧导航工作台、书库页、下载页、查看详情页、设置页、SQLite 数据存储、Markdown 总目录保留、封面缓存规则、数据流、错误处理、测试策略和非目标。
- 设计文档明确第一版只管理当前设置里的一个下载目录，SQLite 作为桌面端主索引，`catalog.md` 继续作为用户可直接打开查看的总目录。
- 设计文档明确封面缩略图只能等比例缩小和压缩画质，不允许裁剪、截断或取局部画面。
- 下一步需要用户审阅设计文档中的待确认项，再进入实现计划阶段。

### 验证情况

- 本次为设计文档更新，未运行代码单元测试。
- 已检查文档内容未记录账号、密码、cookie、token、真实本地下载目录、PDF 或 `catalog.md` 内容。

## 2026-06-17 23:48:32 +08:00

### 修改范围

- 桌面书库数据架构规划
- 下载目录与用户数据位置规划
- 封面缓存规则确认
- 开发记录

### 涉及文件

- `development-log.md`

### 具体内容

- 用户确认第一版桌面书库只管理当前设置里的一个下载目录，也只更新这一个下载目录。
- 桌面端主数据源采用独立结构化索引，优先设计为 SQLite 数据库；原有 `catalog.md` 继续保留，作为用户可直接打开查看的 Markdown 总目录，不作为桌面端主索引。
- 下载目录仍由用户自定义，下载后的图片、PDF 和 `catalog.md` 保持在用户选择的下载根目录下，目录结构继续接近当前 `作者 / JM号-作品名 / 第N章` 的规则。
- 桌面应用用户数据默认放在 Windows 用户数据目录，例如 `%APPDATA%/JMComic Shelf/`，用于保存 `shelf.db`、`settings.json` 和封面缓存；程序安装目录只放应用代码，避免后续自动更新覆盖用户数据。
- 用户担心数据库放在 C 盘可能变大；当前判断是 SQLite 文本索引本身体积很小，主要空间来自封面缓存。设计上封面缓存应可清理、可重建，后续可预留高级设置迁移应用数据目录。
- 封面缓存只保存桌面端使用的缩略图，不保存原图；缩略图必须完整保留封面内容，只允许等比例缩小和适度压缩画质，不允许裁剪、截断或只取局部画面。
- “全部”作为桌面端内置筛选器实现，不写成每本作品的真实标签；默认展示全部已下载作品。

### 验证情况

- 本次为规划记录更新，未运行代码单元测试。
- 已确认未记录账号、密码、cookie、token、真实本地下载目录、PDF 或 `catalog.md` 内容。

## 2026-06-17 23:26:41 +08:00

### 修改范围

- 桌面应用布局方案确认
- 书库筛选规则规划
- 开发记录

### 涉及文件

- `development-log.md`

### 具体内容

- 用户确认采用桌面应用布局方案 A：左侧导航工作台作为主框架。
- 左侧导航后续实现时应使用“图标 + 文字”的功能入口，不使用只有图标的窄导航；入口至少包含书库、下载、查看详情和设置。
- 书库筛选数据中需要保留“全部”入口；默认状态展示已经下载的全部内容，再根据 JM 号、作者名或标签进行筛选。
- 本地可视化草图 `.superpowers/brainstorm/desktop-app/layout-preview.html` 已同步更新为方案 A 的“图标 + 文字”导航与“全部”筛选展示；该目录已被 `.gitignore` 忽略，不作为正式项目文件提交。
- 下一步需要继续确认书库索引的数据来源：直接解析现有 `catalog.md`，还是在下载后同步维护一个更适合桌面端读取的结构化索引。

### 验证情况

- 本次为规划记录更新，未运行代码单元测试。
- 已确认未记录账号、密码、cookie、token、真实本地下载目录、PDF 或 `catalog.md` 内容。

## 2026-06-17 23:07:55 +08:00

### 修改范围

- 桌面应用前期规划记录
- 项目协作说明
- 项目专属 Skill
- 可视化草图文件忽略规则

### 涉及文件

- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `.gitignore`
- `development-log.md`

### 具体内容

- 确认下一阶段目标是把当前脚本式工作流整理为 Windows 桌面应用，计划以 PySide6 + QFluentWidgets 实现，并参考 `ok-oldking/ok-script` 的原生 Windows 风格。
- 初步需求包括：下载功能、查看详情功能、本地书库查找功能、按 JM 号/作者/标签筛选、按作者分组展示命中作品、封面卡片展示、点击封面打开 PDF、右键在文件资源管理器中打开 PDF 所在位置。
- 后续打包方向倾向研究 `ok-oldking/pyappify`，避免默认使用 PyInstaller，并预留自动更新能力。
- 用户确认开发记录也应记录必要的前期思路、规划结论和阶段进度；因此更新 `AGENTS.md` 和项目专属 Skill，把这条作为后续协作规则。
- 用户确认可使用 brainstorming 可视化伴随来展示 UI 草图；将 `.superpowers/` 加入 `.gitignore`，避免本地草图会话文件进入仓库。

### 验证情况

- 本次为项目协作规则与规划记录更新，未运行代码单元测试。
- 已检查本次记录未包含账号、密码、cookie、token、真实本地下载目录、PDF 或 `catalog.md` 内容。

## 2026-06-17 21:32:32 +08:00

### 修改范围

- 本地项目目录命名
- 项目文档与协作说明检查

### 涉及文件

- `development-log.md`

### 具体内容

- 准备将本地项目文件夹从 `JMComic-Crawler-Python` 重命名为 `JMComic-Shelf`，与 GitHub 仓库名保持一致。
- 检查 README、英文 README、`AGENTS.md` 和项目专属 Skill 中的 `JMComic-Crawler-Python` 引用，确认这些引用均指向上游原作者项目，应保留作为来源说明，不应误改为当前仓库名。
- 确认当前仓库远程仍为 `origin -> Dylanliiiii/JMComic-Shelf`，`upstream -> hect0x7/JMComic-Crawler-Python`。

### 验证情况

- 已运行文本检索，确认没有需要修改的本地旧目录名引用。
- 已确认 `D:\Others\JMComic-Shelf` 当前不存在，可以用于重命名。

## 2026-06-17 21:31:00 +08:00

### 修改范围

- 项目协作说明
- 项目专属 Skill
- 开发记录

### 涉及文件

- `AGENTS.md`
- `README.md`
- `assets/readme/README-en.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-project/agents/openai.yaml`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/agents/openai.yaml`
- `development-log.md`

### 具体内容

- 新增 `AGENTS.md`，记录项目定位、上游关系、敏感配置、下载目录、PDF、Markdown 总目录、Windows 脚本、质量要求和 GitHub 维护规则。
- 新增 `jmcomic-shelf-project` 项目专属 Skill，用于后续维护下载工作流、目录插件、README、脚本和桌面应用规划。
- 新增 `jmcomic-shelf-maintenance` 项目专属 Skill，用于后续每次修改后的开发记录、验证、commit 和 GitHub push。
- 新增 `development-log.md`，用于记录项目后续演进。
- 将 README 中的本机绝对路径示例改为相对配置文件示例，避免开源文档依赖维护者电脑路径。

### 验证情况

- 本次为项目协作说明、Skill 和 README 文档更新，未运行应用单元测试。
- 已参考 LaunchDock 的 `AGENTS.md`、项目专属 Skill 和 `development-log.md` 结构。
