# Development Log

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
