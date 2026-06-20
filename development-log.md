# Development Log

## Version 0.2.2 - 2026-06-20 10:12:08 +08:00

### 修改范围

- 发布本地书库索引稳定性修复版。
- 将桌面端项目版本号从 `0.2.1` 更新为 `0.2.2`。

### 涉及文件

- `src/jmcomic_shelf/__init__.py`
- `development-log.md`

### 具体内容

- 发布前已按项目规则运行 `git ls-remote --tags origin`，确认当前 GitHub 远端最新 Release 基线为 `v0.2.1`。
- 本次发布包含上一条日常开发记录中的 bug 修复：稳定本地书库作者分组与作品排序，并让下载目录索引重建使用单次批量事务写入，减少从禁漫预览页切回书库时读到半更新状态的窗口。
- 本次属于修复版和小型稳定性改进，因此按语义化版本从 `v0.2.1` 升级到 `v0.2.2`。
- 同步更新 `src/jmcomic_shelf/__init__.py` 的桌面端版本号为 `0.2.2`，用于 PyAppify 自动更新链路识别新包版本。未修改 `src/jmcomic/__init__.py` 的上游核心库版本号。
- 已检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/`：本次是既有书库索引稳定性修复的正式发布，不新增用户入口、不改变目录规则，暂不需要同步正文。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_packaging -v`，3 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，53 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\database.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，通过。
- 已确认 `pyappify.yml`、`.github/workflows/release.yml`、`icons/icon.png` 和 `icons/icon.ico` 均存在。

## 2026-06-20 05:50:45 +08:00

### 修改范围

- 修复从禁漫预览页切回本地书库后，作者分组顺序和作品数量偶发不稳定的问题。
- 增加书库排序与后台索引重建的回归测试。

### 涉及文件

- `src/jmcomic_shelf/database.py`
- `src/jmcomic_shelf/index_service.py`
- `tests/test_jmcomic/test_shelf_database.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `TASKS.md`
- `development-log.md`

### 具体内容

- 排查确认根因：本地书库切回时会先轻量读取 SQLite，同时后台重建下载目录索引；旧实现按 `updated_at DESC` 展示作品，而重建索引会逐条 upsert 并刷新 `updated_at`，导致 UI 在不同刷新时机下看到的作者分组顺序可能变化。
- 旧实现重建索引时逐条提交记录，后台同步过程中 UI 可能先读到尚未完全同步后的 SQLite 状态，从而出现刷新几次后数量才稳定的观感。
- 将书库查询排序从 `updated_at DESC` 改为稳定的“第一作者名 + 数字 JM ID 倒序 + JM ID”顺序，普通查询、单标签筛选和多标签筛选保持一致。
- 为 `ShelfDatabase` 增加 `upsert_albums()` 批量写入接口，重建下载目录索引时使用单次事务提交整批记录，减少 UI 读到半更新状态的窗口。
- 下载目录扫描结果在写入 SQLite 前也按相同规则稳定排序，避免文件系统遍历顺序影响索引写入顺序。
- 新增回归测试，覆盖排序不受 `updated_at` 影响，以及 `rebuild_index_from_download_dir()` 使用批量写入。
- 已检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/`：本次是既有“切回书库轻量读取、后台扫描完成后刷新”设计的稳定性修复，不新增用户入口、不改变目录规则，暂不需要同步正文。
- 本次为日常 bug 修复，未更新项目版本号，也未发布 Release。

### 验证情况

- 已先运行新增排序回归测试并确认失败，失败原因为查询仍按 `updated_at DESC` 返回。
- 已先运行新增批量写入回归测试并确认失败，失败原因为索引重建仍逐条调用 `upsert_album()`。
- 修复后已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_database.TestShelfDatabase.test_query_albums_order_is_stable_after_reindex_upserts tests.test_jmcomic.test_shelf_index_service.TestShelfIndexService.test_rebuild_index_from_download_dir_writes_records_in_one_batch -v`，2 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，53 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\database.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，通过。

## Version 0.2.1 - 2026-06-20 04:30:00 +08:00

### 修改范围

- 修复 PyAppify 自动更新后仍运行旧代码的问题。
- 增加包装版本来源测试。

### 涉及文件

- `src/jmcomic_shelf/__init__.py`
- `pyproject.toml`
- `setup.py`
- `tests/test_jmcomic/test_shelf_packaging.py`
- `TASKS.md`
- `development-log.md`

### 具体内容

- 根据用户复现结果，确认“全新安装最新版本正常，应用内自动更新后仍缺少新预览功能和封面显示”，问题方向不是封面扫描本身，而是自动更新后安装包没有正确更新到最新应用代码。
- 排查发现当前源码能够从下载根目录 `Cover/` 扫到 90 张封面，应用数据目录也已有 90 张 `covers/JM号.jpg` 缩略图；封面缺失现象更符合自动更新后仍运行旧包的表现。
- 修复 `pyproject.toml` 的项目元数据：分发包名从上游 `jmcomic` 改为桌面端 `JMComic-Shelf`，动态版本来源从上游核心库 `jmcomic.__version__` 改为桌面端 `jmcomic_shelf.__version__`，并将主页指向当前仓库。
- 修复 `setup.py` 的项目元数据：分发包名从上游 `jmcomic` 改为桌面端 `JMComic-Shelf`，版本读取来源从 `src/jmcomic/__init__.py` 改为 `src/jmcomic_shelf/__init__.py`。
- 将桌面端版本号更新为 `0.2.1`，用于发布修复版，让 PyAppify 自动更新链路能识别 Python 包版本变化，避免继续复用旧的 `jmcomic==2.7.0` 包元数据。
- 新增 `tests/test_jmcomic/test_shelf_packaging.py`，防止后续再次把桌面端发布版本或分发包名误绑定到上游核心库。
- 本次未修改 `src/jmcomic/__init__.py` 的上游核心库版本号。

### 验证情况

- 已先运行新增包装测试并确认失败，失败原因分别为 `pyproject.toml` 使用 `jmcomic.__version__`、`setup.py` 读取 `src/jmcomic/__init__.py`。
- 修复后已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_packaging -v`，3 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，51 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，通过。
- 已运行 `$env:PYTHONPATH='src'; python -c "import jmcomic_shelf; print(jmcomic_shelf.__version__)"`，输出 `0.2.1`。
- 尝试运行 `python setup.py --version` 时，当前系统 Python `C:\Python314\python.exe` 缺少 `setuptools`，无法用该命令验证；已用测试直接校验 `setup.py` 和 `pyproject.toml` 的版本来源。

## Version 0.2.0 - 2026-06-20 03:55:00 +08:00

### 修改范围

- 禁漫预览页封面展示功能发布。
- Release 版本号来源规则修正。

### 涉及文件

- `src/jmcomic_shelf/__init__.py`
- `src/jmcomic_shelf/detail_service.py`
- `src/jmcomic_shelf/ui/detail_page.py`
- `tests/test_jmcomic/test_shelf_detail_service.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 发布前已按项目规则运行 `git ls-remote --tags origin`，确认当前 GitHub 远端最新 Release 基线为 `v0.1.0`。
- 本次包含用户可见的新功能：禁漫预览页在详情文字上方显示完整等比例封面图，并优先复用本地封面；缺失时缓存线上封面。因此按语义化版本从 `v0.1.0` 升级到 `v0.2.0`。
- 同步更新 `src/jmcomic_shelf/__init__.py` 的桌面端版本号为 `0.2.0`。未修改 `src/jmcomic/__init__.py` 的上游核心库版本号。
- 新增 `DetailResult` 和 `fetch_album_detail_result()`，保留 `fetch_album_detail()` 兼容旧调用。
- 修正并固化 release 版本号来源规则：以后发版必须以 `origin` 远端 tag 或 GitHub Releases 为准，禁止使用本地上游历史 tag 推断项目版本。

### 验证情况

- 已运行 `git ls-remote --tags origin`，确认远端当前仅返回 `v0.1.0`。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_detail_service -v`，6 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，48 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\detail_page.py`，通过。
- 已运行 `git diff --check`，无空白错误，仅有 Windows 换行提示。
- 已确认 `pyappify.yml`、`.github/workflows/release.yml`、`icons/icon.png` 和 `icons/icon.ico` 均存在。
- 已确认 `jmcomic-option.yml` 仍被 `.gitignore` 忽略。

## 2026-06-20 03:50:00 +08:00

### 修改范围

- 修正 JMComic Shelf release 版本号来源规则。
- 参考 LaunchDock 的版本号、Release 和开发记录约定，补充本项目维护流程。

### 涉及文件

- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `TASKS.md`
- `development-log.md`

### 具体内容

- 复核 `origin` 远端 tag，确认当前 GitHub Release 基线只有 `v0.1.0`；本地 `git tag` 中的 `v2.x.x` 来源于上游历史标签，不能用于本项目发版。
- 参考 `https://github.com/Dylanliiiii/LaunchDock`：日常开发记录只写日期时间，不写版本号；只有正式发布、打包或上线更新时才使用 `## Version x.x.x - 时间` 标题并更新项目自身版本号。
- 在 `AGENTS.md` 和 `jmcomic-shelf-maintenance` 中新增硬性规则：正式 release 前必须通过 `git ls-remote --tags origin` 或 GitHub Releases 页面确认当前仓库远端最新版本；禁止用本地 `git tag`、`git describe --tags` 或上游 `src/jmcomic/__init__.py` 推断 JMComic Shelf 的最新 Release。
- 补充语义化版本递增规则：主版本号用于大改或不兼容变更，次版本号用于新功能，修订号用于 bug 修复或小型改进；不确定时先向用户确认。
- 本次为协作规则和项目专属 Skill 修正，未更新项目版本号，也未发布 Release。

### 验证情况

- 已运行 `git ls-remote --tags origin`，确认远端当前仅返回 `v0.1.0`。
- 已运行 `git ls-remote --tags https://github.com/Dylanliiiii/LaunchDock.git`，确认参考项目发布标签从 `v1.0.0` 递增到 `v1.1.4`。
- 已读取 LaunchDock 的 `AGENTS.md` 和 `development-log.md`，确认其日常开发记录与正式 `Version x.x.x` 发布记录的区分方式。
- 本次为文档和流程规则更新，未运行应用单元测试。

## 2026-06-20 03:45:00 +08:00

### 修改范围

- 禁漫预览页新增封面图展示。
- 详情查询服务新增封面缓存结果，优先使用本地封面，缺失时缓存线上封面。
- 同步 README、项目专属 Skill、桌面端 spec 和 plan。

### 涉及文件

- `src/jmcomic_shelf/detail_service.py`
- `src/jmcomic_shelf/ui/detail_page.py`
- `tests/test_jmcomic/test_shelf_detail_service.py`
- `README.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `TASKS.md`
- `development-log.md`

### 具体内容

- 新增 `DetailResult` 和 `fetch_album_detail_result()`，保留原 `fetch_album_detail()` 兼容旧调用。
- 预览页查询时会先同步索引并查找本地记录；如果本地已有封面，直接显示本地封面；否则调用上游 `download_album_cover()` 将线上封面缓存到应用数据目录 `covers/`。
- 禁漫预览页在详情文字上方新增封面显示区域，按完整等比例缩放，不裁剪、不截断。
- 保持查询中状态、按钮禁用和 Enter 查询行为。
- README、项目专属 Skill、桌面端 spec 和 plan 已同步新增的预览封面能力；`AGENTS.md` 的规则和工作流说明无需调整。
- 本次未写入真实账号、cookie、token、代理配置、用户本地下载内容、PDF、封面或本地 `catalog.md`。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_detail_service -v`，6 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，48 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\detail_page.py`，通过。
- 已运行 `git diff --check`，无空白错误，仅有 Windows 换行提示。
- 已确认 `jmcomic-option.yml` 仍被 `.gitignore` 忽略。

## 2026-06-20 03:35:00 +08:00

### 修改范围

- 整理本机 `D:\Others\JMComic` 现有书库到新的 PDF-only 作者目录结构。
- 复查并确认源码启动脚本是否仍需保留。
- 更新本次任务台账和开发记录。

### 涉及文件

- `TASKS.md`
- `development-log.md`

本次还修改了用户本地下载目录 `D:\Others\JMComic` 中的 PDF、封面缓存、`catalog.md` 和桌面端 SQLite 索引；这些属于用户本地内容，不进入 Git 提交。

### 具体内容

- 整理前扫描确认本地书库共有 90 部作品、90 个旧作品图片目录、90 个 PDF，且每部作品均能找到第一张图片作为封面候选。
- 在 `D:\Others\JMComic\Cover` 创建/使用封面缓存目录，复制 90 张封面。
- 将 90 个 PDF 移动到 `下载根目录 / 作者 / JM号-作品名.pdf`，并删除 90 个旧 `JM号-作品名 / 第1章 / 图片` 作品目录。
- 文件系统层面未发现同一 JM ID 分布在多个作者目录下的情况；本次本地整理无需额外选择重复作品保留作者。
- 检查 `catalog.md` 时发现 2 个 JM ID 仍有重复作者条目，已按本次本地整理规则保留第一次出现的作者分组，并补回整理过程中缺失的 4 个 catalog 条目。
- 复查后确认本地文件系统剩余旧作品目录数为 0，PDF 数为 90，`Cover/` 封面数为 90；`catalog.md` 中 90 个 JM ID 与 PDF 完全对齐且无重复作者登记。
- 已调用当前 `rebuild_index_from_download_dir()` 重建桌面端 SQLite 索引，确认 90 条记录的 PDF 和封面路径均可访问，且不再指向旧 `JM...` 图片目录。
- 检查 `start-jmcomic-shelf.bat` 后确认它仍是源码仓库双击启动入口，并且 README、AGENTS 和项目 Skill 都把它作为保留脚本；本次不删除。

### 验证情况

- 已复查 `D:\Others\JMComic`：旧作品图片目录 0 个，PDF 90 个，`Cover/` 封面 90 个。
- 已复查 `catalog.md`：PDF JM ID 90 个，catalog JM ID 90 个，缺失 0 个，额外 0 个，重复 0 个。
- 已重建桌面端 SQLite：`rebuilt=90`；数据库中 90 条记录，缺失 PDF 0 个，缺失封面 0 个，旧作品目录路径 0 个。
- README、`AGENTS.md`、项目专属 Skill、spec 和 plan 已在上一轮同步新的工作流；本次没有改变项目代码逻辑或用户入口，无需继续修改。

## 2026-06-20 02:55:00 +08:00

### 修改范围

- 调整桌面端下载后的本地文件结构：作者目录下只保留 PDF，图片目录作为中间产物不再保留。
- 新增下载根目录 `Cover/` 封面缓存逻辑，保存每本漫画第一面图片供书库读取。
- 修复多作者作品在 `catalog.md` 和桌面端书库中按多个作者重复出现的问题，统一只保留第一作者。
- 改进禁漫预览页交互，查询期间显示搜索中状态，并支持输入框按 Enter 查询。
- 新增根目录 `TASKS.md` 作为跨会话任务台账，并同步项目协作规则、项目专属 Skill、README、规格和计划文档。

### 涉及文件

- `TASKS.md`
- `AGENTS.md`
- `README.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `src/jmcomic/jm_plugin.py`
- `src/jmcomic_shelf/download_service.py`
- `src/jmcomic_shelf/index_service.py`
- `src/jmcomic_shelf/detail_service.py`
- `src/jmcomic_shelf/ui/detail_page.py`
- `tests/test_jmcomic/test_jm_plugin.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `tests/test_jmcomic/test_shelf_detail_service.py`
- `development-log.md`

### 具体内容

- 下载服务在上游插件生成 PDF 后，会把最终 PDF 移动到 `下载根目录 / 第一作者 / JM号-作品名.pdf`。
- 下载服务会从作品图片目录中复制第一张图片到 `下载根目录 / Cover / JM号-作品名.扩展名`，再删除下载阶段产生的作品图片目录。
- 书库扫描跳过根目录 `Cover/`，支持新结构的作者目录 PDF、根目录封面缓存、旧版作品图片目录和下载根目录或子目录中的 PDF。
- 桌面端索引、书库作者分组和 catalog 合并逻辑均按第一作者保存；旧 catalog 中同一 JM ID 在多个作者下重复登记时，扫描和更新会只保留第一作者语义。
- `CatalogPlugin` 生成 Markdown 总目录时只登记第一作者，并在更新同一作品时移除其他作者分组下的重复条目。
- 禁漫预览页输入框绑定 Enter 查询；查询期间显示 `正在搜索中` 状态，并暂时禁用输入框和按钮，完成或失败后恢复。
- 新增 `TASKS.md` 规则：开工时登记任务，完成一点标记一点，全部验证通过后清空当前任务，方便上下文压缩或新开对话续做。
- README、`AGENTS.md`、项目专属 Skill、桌面端 spec 和 plan 已同步新的 PDF-only 作者目录、根目录 `Cover/`、第一作者去重和预览交互规则。
- 本次未写入真实账号、cookie、token、代理配置、用户本地下载内容、PDF、封面或本地 `catalog.md`。

### 验证情况

- 已先按 TDD 增加/更新测试，并确认新测试在旧实现下失败。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，45 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v`，5 项通过。
- 直接运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic\jm_plugin.py` 时仍因仓库内 `__pycache__` 权限/占用报 `Permission denied`；已改用 `$env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache')` 后通过。
- 已检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/`，本次改变用户可见文件结构与交互行为，相关文档均已同步。

## 2026-06-20 01:11:56 +08:00

### 修改范围

- 补齐本地下载目录中缺失的合并 PDF。
- 修复 Windows 长路径导致 `img2pdf` 生成、书库扫描和打开 PDF 误判失败的问题。
- 修复桌面端下载任务在 PDF 未生成时仍显示成功的问题。

### 涉及文件

- `src/jmcomic/jm_plugin.py`
- `src/jmcomic_shelf/path_utils.py`
- `src/jmcomic_shelf/download_service.py`
- `src/jmcomic_shelf/index_service.py`
- `src/jmcomic_shelf/file_actions.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `tests/test_jmcomic/test_jm_plugin.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `tests/test_jmcomic/test_shelf_file_actions.py`
- `tests/test_jmcomic/test_shelf_path_utils.py`
- `development-log.md`

### 具体内容

- 扫描当前下载目录后确认共有 90 个带图片的作品目录，其中 29 个缺失对应合并 PDF；使用项目当前 `img2pdf` 方案和 `JM{Aid}-{Atitle}.pdf` 命名规则补齐全部 29 个 PDF。
- 首轮补齐 27 个 PDF，剩余 2 个因 Windows 总路径超过普通 API 限制而写入失败；使用 Windows 长路径前缀补齐后，90 个 PDF 文件头均可读到 `%PDF-`。
- 新增 `jmcomic_shelf.path_utils`，统一处理 Windows `\\?\` 长路径、长路径存在性判断和长路径递归扫描。
- `Img2pdfPlugin` 写入 PDF 和创建输出目录时使用长路径兼容路径，避免长标题作品在插件阶段失败。
- 下载服务在任务完成后必须找到生成的 PDF 才标记成功；若插件未产出 PDF，会把任务标记为失败并提示缺少 PDF。
- 下载服务、书库索引和封面卡片右键菜单改用长路径兼容判断，避免超长路径 PDF 已存在但 UI 误判为缺失。
- 已重建桌面端 SQLite 索引，确认当前书库 90 条记录均关联到可访问 PDF。
- 开工前读取本地 `AGENTS.md` 和项目专属 Skill 时，PowerShell 输出仍呈现 mojibake；本次继续以用户消息中提供的正常中文规则为准，并未扩大为协作文件编码修复。
- 已检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/`：本次修复的是既有“下载后生成 PDF / 书库打开 PDF”规则的实现缺陷，不新增用户入口、不改变推荐目录规则，无需同步正文。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，40 项通过；仍有既有 QFluentWidgets Pro 提示、`zhconv`/Qt 退出阶段 `ResourceWarning`，不影响测试结果。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_jm_plugin.Test_CatalogPlugin tests.test_jmcomic.test_jm_plugin.Test_ShelfIndexPlugin tests.test_jmcomic.test_jm_plugin.TestPluginPathUtils -v`，7 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile src\jmcomic\jm_plugin.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\file_actions.py src\jmcomic_shelf\path_utils.py src\jmcomic_shelf\ui\library_page.py`，通过。
- 已用长路径兼容检查确认当前下载目录中 90 个带图作品目录均有 PDF，缺失数为 0。
- 已重建桌面端 SQLite 索引并查询确认 90 条记录均有关联 PDF，缺失数为 0。
- 首次直接运行 `py_compile` 时因仓库 `__pycache__` 写入权限/占用报 `Permission denied`，已改用临时 `PYTHONPYCACHEPREFIX` 后通过。

## 2026-06-18 12:58:10 +08:00

### 修改范围

- 修复 `v0.1.0` 首次 Release workflow 中 PyAppify 构建失败的问题。

### 涉及文件

- `pyappify.yml`
- `development-log.md`

### 具体内容

- GitHub Actions 日志显示 PyAppify Action 会把 `pyappify.yml` 的 `name` 写入 Tauri/Cargo package name。
- Cargo package name 不允许空格，原配置 `JMComic Shelf` 导致 `cargo metadata` 失败。
- 将 `pyappify.yml` 的 `name` 改为 `JMComic-Shelf`；应用自身窗口标题和 README 展示名仍保持 `JMComic Shelf`。

### 验证

- 已重新解析 `pyappify.yml` 和 `.github/workflows/release.yml`，结果为 `yaml ok`。
- 已运行 `git diff --check`，无空白错误，仅有 Windows 换行提示。
- 下一步提交修复后重新触发 Release workflow。

## 2026-06-18 12:52:38 +08:00

### 修改范围

- 修复设置页外观主题选择后下次启动不生效的问题。
- 修复本地书库分类标签点击时整块标签面板闪烁的问题。
- 清理早期下载和查看详情脚本，改为桌面端优先入口。
- 补充 PyAppify 打包与 GitHub Release 工作流，预留并接入软件图标。
- 同步 README、英文 README、AGENTS、项目专属 Skill、桌面端规格和计划文档中的发布维护规则。

### 涉及文件

- `src/jmcomic_shelf/app.py`
- `src/jmcomic_shelf/paths.py`
- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/settings_page.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `src/jmcomic_shelf/assets/icon.png`
- `assets/icon.png`
- `icons/icon.png`
- `icons/icon.ico`
- `icons/README.md`
- `pyappify.yml`
- `.github/workflows/release.yml`
- `pyproject.toml`
- `setup.py`
- `README.md`
- `assets/readme/README-en.md`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `tests/test_jmcomic/test_shelf_settings.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- 删除 `download-jmcomic.bat`
- 删除 `view-jmcomic.bat`

### 具体内容

- 设置页主题下拉框改为选择后立即写入 `settings.json`，主程序在创建主窗口前先读取并应用保存的主题，避免每次启动回到深色模式。
- 本地书库分类标签面板保留已有按钮对象，只在标签集合或列数变化时重建；普通筛选点击只更新按钮状态，避免标签区域整体刷新闪烁。
- 新增回归测试覆盖主题即时保存和标签筛选不重建按钮。
- 删除早期命令行下载、查看详情入口脚本，README 改为推荐 `start-jmcomic-shelf.bat`、源码运行和 GitHub Release 桌面端安装包。
- 新增 `pyappify.yml` 和 `.github/workflows/release.yml`，约定推送 `v*` tag 时由 PyAppify Action 构建 Windows 桌面发布包并上传到 GitHub Release。
- 新增 `icons/` 发布图标目录，并把当前软件图标同步到包内资源，确保源码运行、安装包和 README 都能引用同一图标资产。
- 文档中补充版本号规则：只在用户明确要求发版时使用 `vMAJOR.MINOR.PATCH`；当前不增加 CNB 镜像和同步 Action。

### 验证

- 已运行主题回归测试并先观察到修复前失败，再修复为通过。
- 已运行分类标签回归测试并先观察到修复前缺少稳定按钮缓存，再修复为通过。
- 已运行：

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v
```

- 结果：35 个 `test_shelf_*.py` 测试通过；运行过程中仍有 Qt/zhconv 的既有 `ResourceWarning`，不影响测试结果。
- 已运行桌面端相关模块 `py_compile`，通过。
- 已解析 `pyappify.yml` 和 `.github/workflows/release.yml`，通过。
- 已检查 `assets/icon.png`、`icons/icon.png`、`icons/icon.ico`、`src/jmcomic_shelf/assets/icon.png` 能由 Pillow 打开。
- 已运行 offscreen 桌面端冒烟测试，窗口标题为 `JMComic Shelf`，图标路径存在。

### 同步检查

- README / 英文 README：已同步桌面端入口、图标、PyAppify 与 Release 说明。
- `AGENTS.md`：已同步脚本清理、版本号和 Release 维护规则。
- 项目专属 Skill：已同步桌面端入口、图标、PyAppify 和 Release 规则。
- `docs/superpowers/specs/` 与 `docs/superpowers/plans/`：已同步移除旧脚本入口、主题持久化、标签面板稳定渲染和 PyAppify 发版路径。
- `jmcomic-option.yml`：仍应保持 ignored，不进入提交。

## 2026-06-18 12:31:24 +08:00

### 修改范围

- 桌面应用窗口图标接入。
- 应用资源路径辅助函数。

### 涉及文件

- `assets/icon.png`
- `src/jmcomic_shelf/app.py`
- `src/jmcomic_shelf/paths.py`
- `src/jmcomic_shelf/ui/main_window.py`
- `development-log.md`

### 具体内容

- 使用 `assets/icon.png` 作为 JMComic Shelf 桌面端软件图标。
- 新增 `get_app_icon_path()`，统一返回应用图标路径，并兼容后续打包时的 `_MEIPASS` 资源根目录。
- 在 `QApplication` 和 `MainWindow` 上设置同一个 `QIcon`，用于窗口标题栏、任务栏和应用级默认窗口图标。
- 开工前读取 `AGENTS.md`、项目专属 Skill、相关桌面端 spec/plan 和近期开发记录时，PowerShell 终端输出出现中文 mojibake；结合本次用户提供的正常中文规则内容，判断为终端输出编码显示问题，本次不扩大为文档清理任务。
- 已检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/`：本次仅接入现有图标资源，不改变使用流程和设计规则，无需同步更新。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，33 个测试通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，结果通过。
- 已检查 diff 中不包含账号、密码、cookie、token、代理凭据或用户下载内容。

## 2026-06-18 08:10:04 +08:00

### 修改范围

- 本地书库搜索输入体验优化。
- 本地书库“全部 / 分类”筛选按钮视觉状态统一。
- 分类标签面板滚动与多选筛选。
- 相关文档、项目规则和开发记录同步。

### 涉及文件

- `src/jmcomic_shelf/database.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `tests/test_jmcomic/test_shelf_database.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 排查确认搜索框卡顿根因是 `textChanged` 立即调用 `reload()`，而 `reload()` 会查库并重绘封面网格，输入法组合文字期间会被频繁刷新打断；改为 260ms 防抖后再轻量查询，不在每个字符输入时立即刷新。
- 将“全部”和“分类”改为同一种筛选按钮样式，统一字体、尺寸、下划线和选中亮度；分类展开或存在已选标签时，“分类”保持选中状态。
- 分类标签面板改为最多展示五行，超出后在面板内部滚动，避免标签过多时占满页面。
- 新增多标签筛选：可同时选择多个标签，数据库按“满足任一选中标签”查询并显示作品；点击“全部”清空搜索和标签筛选。
- 将 `src/jmcomic_shelf/ui/library_page.py` 和 `tests/test_jmcomic/test_shelf_library_page.py` 中本次触及的历史 mojibake 文案恢复为正常 UTF-8 中文。
- README、`AGENTS.md`、项目专属 Skill、spec 和 plan 已同步记录搜索防抖、分类面板五行滚动、多标签任一匹配筛选规则；维护 Skill 仍是通用收尾流程，无需修改。
- 开工前读取本地 `AGENTS.md` 与两个项目专属 Skill 时，终端输出仍存在 mojibake 乱码；本次按用户消息中贴出的正常 UTF-8 规则以及既有开发记录继续执行，并在触及的 UI/测试文件中清理乱码。

### 验证情况

- 已按 TDD 新增失败测试 `test_query_albums_by_tags_matches_any_selected_tag`，确认旧数据库缺少多标签查询接口；修复后通过。
- 已按 TDD 更新/新增书库页测试，覆盖搜索防抖、多标签选择、分类面板五行滚动、筛选按钮同尺寸和选中下划线状态；修复后相关测试通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，33 项通过；`zhconv` 和 Qt 退出阶段仍有既有 `ResourceWarning` 提示，但测试结果通过。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile ...`，通过。
- 已运行 offscreen 书库页烟测，确认搜索防抖间隔为 `260ms`，分类面板最大高度为 `208px`，多标签选择可同时保留“后宫”和“巨乳”。

## 2026-06-18 07:53:26 +08:00

### 修改范围

- 本地书库分类标签展开修复。
- 下载目录重建索引时合并 `catalog.md` 标签。
- 本地书库筛选按钮尺寸统一。

### 涉及文件

- `src/jmcomic_shelf/index_service.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- `development-log.md`

### 具体内容

- 排查确认“分类”展开后只显示“暂无标签”的根因是书库页会从下载目录重建 SQLite 索引，但扫描现有作者目录、作品目录和 PDF 时没有读取下载根目录下的 `catalog.md`，导致已有漫画记录没有标签关系。
- 在 `rebuild_index_from_download_dir()` 的扫描结果中按 JM ID 合并 `catalog.md` 里的作者、标签、链接和章节信息；标签仍通过 `CatalogPlugin.read_catalog()` 和数据库写入流程统一转换为中文简体，标题和作者保留来源文本。
- 将“分类”按钮高度固定为与左侧“全部”筛选块一致，避免截图中两个按钮大小不统一。
- 已检查 README、`AGENTS.md`、项目专属 Skill、spec 和 plan：上次已同步记录标签简体化和分类筛选规则，本次是修复既有规则落地问题，无需再改文档正文。
- 开工前读取本地 `AGENTS.md` 与两个项目专属 Skill 时，终端输出存在 mojibake 乱码；本次按用户消息中贴出的正常 UTF-8 规则以及已有开发记录继续执行，未在本次一并修复协作文件编码。

### 验证情况

- 已按 TDD 新增失败测试 `test_rebuild_index_from_download_dir_merges_tags_from_catalog`，确认旧行为会在重建索引后丢失 `catalog.md` 中的标签；修复后通过。
- 已按 TDD 新增失败测试 `test_category_button_uses_same_height_as_all_filter`，确认旧行为中“分类”按钮高度与“全部”筛选块不一致；修复后通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_library_page -v`，6 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_index_service -v`，4 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，30 项通过；`zhconv` 和 Qt 退出阶段仍有既有 `ResourceWarning` 提示，但测试结果通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v`，5 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile ...`，通过。
- 已运行 offscreen 书库页烟测，确认“分类”按钮和“全部”筛选块高度均为 `48`，分类面板默认收起。

## 2026-06-18 07:29:25 +08:00

### 修改范围

- `catalog.md` 标签繁简统一规则。
- 桌面端 SQLite 标签存储与分类筛选。
- 本地书库标签分类 UI。
- README、AGENTS、项目专属 Skill、桌面应用设计文档和实施计划同步。

### 涉及文件

- `src/jmcomic/jm_plugin.py`
- `src/jmcomic_shelf/database.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `tests/test_jmcomic/test_jm_plugin.py`
- `tests/test_jmcomic/test_shelf_database.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- `README.md`
- `assets/readme/README-en.md`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `setup.py`
- `development-log.md`

### 具体内容

- 调整 `CatalogPlugin`：标题、作者、章节和封面保持来源文本；标签在写入 `catalog.md` 前统一转换为中文简体。
- 新增 `CatalogPlugin.normalize_catalog_tags(filepath)`，用于只重写已有 `catalog.md` 中“标签：”后面的标签文本，不改标题、作者、章节和封面。
- 已对当前桌面端设置下载目录下的本地 `catalog.md` 执行一次标签简体化处理；该文件属于用户下载目录，不进入 git diff。
- `ShelfDatabase` 写入标签时统一转为简体，并新增 `list_tags()` 和 `query_albums_by_tag()`，用于列出所有已出现标签和按单个标签精确筛选漫画。
- 本地书库页在“全部”旁新增“分类”按钮；点击后展开当前书库里出现过的标签按钮，点击标签后按该标签筛选作品，点击“全部”返回完整列表。
- 将 `zhconv` 加入运行依赖，避免标签简体化在非开发环境中因缺少依赖而退回原文本。
- README、英文 README、`AGENTS.md`、项目专属 Skill、spec 和 plan 已同步记录“只统一标签，不改标题/作者”的规则，以及本地书库分类筛选能力。
- 维护 Skill 仅描述通用收尾流程，本次规则变化不需要修改。

### 验证情况

- 已按 TDD 先新增失败测试，确认旧行为会保留繁体标签、数据库缺少标签列表/精确筛选接口、书库页缺少分类展开与标签筛选入口。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v`，5 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，28 项通过；`zhconv` 和 Qt 退出阶段有 `ResourceWarning` 提示，但测试结果通过。
- 已运行 `$env:PYTHONPATH='src;tests'; $env:PYTHONPYCACHEPREFIX=(Join-Path $env:TEMP 'codex_jmcomic_pycache'); python -m py_compile ...`，通过。第一次直接运行 `py_compile` 时因源码目录已有 `__pycache__` 写入权限失败，改用临时字节码目录后通过。
- 已运行 offscreen `MainWindow` 初始化烟测，窗口标题输出为 `JMComic Shelf`。
- 已确认 `jmcomic-option.yml` 仍由 `.gitignore` 忽略，git diff 中没有账号密码、cookie、token、代理凭据、下载内容、PDF、封面或用户本地 `catalog.md`。

## 2026-06-18 07:08:52 +08:00

### 修改范围

- 禁漫下载页顶部排版微调。
- 桌面端下载页布局回归测试。

### 涉及文件

- `src/jmcomic_shelf/ui/download_page.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `development-log.md`

### 具体内容

- 将禁漫下载页标题从标题和按钮同一行调整为独立一行。
- 将说明文字与“开始下载”按钮放到标题下方同一行，说明文字在左，按钮在右。
- 新增下载页布局测试，约束标题独立成行，开始按钮位于第二行右侧。
- 本次只调整已有下载页局部排版，不改变功能、文件结构或用户工作流；已检查 README、`AGENTS.md`、项目专属 Skill、spec 和 plan，无需同步更新。

### 验证情况

- 已按 TDD 先新增失败测试 `test_download_page_title_uses_separate_row_from_start_button`，确认当前标题和按钮同一行时失败。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_download_service.TestShelfDownloadService.test_download_page_title_uses_separate_row_from_start_button -v`，通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，26 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py`，通过。
- 已运行 offscreen `MainWindow` 初始化烟测，确认窗口可创建。

## 2026-06-18 06:47:04 +08:00

### 修改范围

- 本地书库页面切换性能优化。
- 本地书库后台索引同步。
- README、桌面应用设计文档和实施计划同步。

### 涉及文件

- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- `README.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 排查确认从其他页面切回本地书库时，`MainWindow.reload_current_page()` 会直接调用 `LibraryPage.reload()`，而 `reload()` 会同步递归扫描下载目录并重建 SQLite 索引，下载目录稍大时会阻塞页面切换。
- 为本地书库新增 `reload_for_activation()`：页面激活时先跳过下载目录扫描，只读取现有 SQLite 索引并立即渲染。
- 新增 `IndexSyncWorker` 后台线程；页面切回本地书库后会在后台扫描下载目录，扫描完成后再轻量刷新列表，保留“切回书库可发现新下载或手动放入作品”的能力。
- 主窗口页面切换优先调用页面的 `reload_for_activation()`，没有该接口时才回退到普通 `reload()`。
- README、spec 和 plan 已同步记录切回本地书库时的后台索引刷新行为；`AGENTS.md` 和两个项目专属 Skill 只需沿用既有同步规则，无需改动。

### 验证情况

- 已按 TDD 先新增失败测试，覆盖页面激活刷新不直接调用下载目录扫描，以及主窗口切回本地书库时优先调用轻量激活刷新。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest tests.test_jmcomic.test_shelf_library_page -v`，4 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，25 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py`，通过。
- 已运行 offscreen `MainWindow` 初始化烟测，确认窗口可创建。

## 2026-06-18 06:29:06 +08:00

### 修改范围

- 桌面端本地书库、禁漫下载、禁漫预览页面细节优化。
- 下载任务输入和进度条状态行为。
- 本地书库封面网格重排性能优化。
- README、桌面应用设计文档和实施计划同步。

### 涉及文件

- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `src/jmcomic_shelf/ui/download_page.py`
- `src/jmcomic_shelf/ui/detail_page.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `tests/test_jmcomic/test_shelf_library_page.py`
- `README.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 左侧导航和页面标题改为“本地书库”“禁漫下载”“禁漫预览”，保留“设置”不变。
- 禁漫下载页开始下载后会先把输入的 JM 号写入任务表格，然后立即清空输入框，方便下一次输入。
- 下载任务全部结束后，进度条归零；成功时显示“全部已完成。”，失败时继续显示失败数量，表格保留成功和失败记录。
- 禁漫预览页标题单独成行，JM 号输入框和查看按钮移动到标题下方。
- 本地书库页的“全部 · N 本”筛选器增加轻量背景框，同时保留青色下划线。
- 本地书库页在左侧导航反复展开或收起时，不再立即频繁重排封面网格，而是通过短延迟合并宽度变化，降低明显卡顿。
- README、spec 和 plan 已同步记录本次用户可见功能与行为变化；`AGENTS.md` 和两个项目专属 Skill 只需沿用既有同步规则，无需改动。

### 验证情况

- 已按 TDD 先新增失败测试，覆盖下载开始后清空输入框、下载全部完成后进度归零，以及书库页宽度变化时延迟重排封面网格。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，23 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py`，通过。
- 已运行 offscreen `MainWindow` 初始化烟测，确认窗口可创建。

## 2026-06-18 03:48:42 +08:00

### 修改范围

- 桌面端书库批量管理。
- 本地漫画文件删除服务。
- 桌面端 SQLite 索引字段与删除能力。
- README、桌面应用设计文档和实施计划。

### 涉及文件

- `src/jmcomic_shelf/models.py`
- `src/jmcomic_shelf/database.py`
- `src/jmcomic_shelf/index_service.py`
- `src/jmcomic_shelf/delete_service.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `tests/test_jmcomic/test_shelf_database.py`
- `tests/test_jmcomic/test_shelf_delete_service.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `README.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 书库页新增“批量管理”模式；进入后封面卡片左上角显示选择框，点击选择框或整张卡片都可切换选中状态。
- 批量工具栏提供“全选”“反选”“取消全选”“删除选中”和“退出批量管理”，并显示当前选中数量。
- 删除选中前弹出确认框，明确提示会删除所选漫画的本地文件和桌面端数据库索引。
- 新增 `delete_service.py`，删除时只处理当前下载目录内的漫画目录和 PDF 文件，外部路径和下载根目录本身会跳过，避免误删。
- SQLite `albums` 表新增 `album_dir` 字段，并在打开旧数据库时自动迁移；下载目录扫描会写入本地漫画目录路径，供批量删除使用。
- `ShelfDatabase` 新增 `delete_albums()`，删除选中作品的索引记录，并依赖外键级联清理作者、标签、章节关联。
- README、spec 和 plan 已同步记录批量管理、二次确认和本地文件删除行为；`AGENTS.md` 与项目专属 Skill 的规则未变化，无需同步。

### 验证情况

- 已按 TDD 先新增失败测试：`test_delete_albums_removes_selected_records` 和 `test_delete_album_files_removes_download_dir_album_assets_only`，确认分别因缺少数据库删除方法和删除服务模块而失败。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，20 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\database.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\delete_service.py src\jmcomic_shelf\models.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\styles.py src\jmcomic_shelf\ui\theme.py`，通过。
- 已运行 offscreen `MainWindow` 批量模式烟测，确认可进入批量模式并执行全选、反选、取消全选。

## 2026-06-18 03:38:12 +08:00

### 修改范围

- 桌面端设置页外观主题布局微调。

### 涉及文件

- `src/jmcomic_shelf/ui/settings_page.py`
- `development-log.md`

### 具体内容

- 将设置页“外观主题”卡片中的主题下拉选择框移动到卡片右侧，左侧保留标题和说明文字。
- 下拉框固定宽度为 `140`，整体使用横向布局，更接近 Windows 设置项的左右分栏表达。
- 本次只调整已有功能的局部排布，不改变功能、配置结构或用户工作流；已检查 README、`AGENTS.md`、项目专属 Skill、spec 和 plan，无需同步更新。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，18 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\styles.py src\jmcomic_shelf\ui\theme.py`，通过。

## 2026-06-18 03:20:06 +08:00

### 修改范围

- 桌面端书库页布局与筛选展示。
- 桌面端下载页任务进度展示。
- 桌面端主题设置。
- 项目协作规则与说明文档同步要求。
- README、桌面应用设计文档和实施计划。

### 涉及文件

- `src/jmcomic_shelf/settings.py`
- `src/jmcomic_shelf/ui/theme.py`
- `src/jmcomic_shelf/ui/styles.py`
- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `src/jmcomic_shelf/ui/download_page.py`
- `src/jmcomic_shelf/ui/settings_page.py`
- `tests/test_jmcomic/test_shelf_settings.py`
- `README.md`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 具体内容

- 书库页将“全部”筛选左对齐，并显示当前结果总数，例如 `全部 · 12 本`。
- 书库页封面卡片网格不再固定每行 5 本，而是根据窗口宽度动态计算列数；拖动窗口时只重排当前记录，不触发重新扫描下载目录。
- 下载页新增任务级总进度条；开始下载后，输入的 JM 号会先进入任务列表，状态按“等待中”“下载中”“已完成”“失败”更新。
- 下载任务改为后台 `QThread` 顺序执行，避免下载过程长期阻塞 UI；第一版只显示任务级进度，不伪造上游下载器未提供的图片级百分比。
- 设置页新增“外观主题”，支持跟随系统、浅色和深色；选择后立即预览，保存后写入 `settings.json`。
- 新增 `ui/theme.py` 统一 QFluentWidgets 主题映射和青色强调色；页面自定义样式会根据当前主题切换深浅色。
- 根据用户补充要求，把“不能只更新开发记录，新增功能/结构/工作流/用户可见行为变化时必须同步检查 README、AGENTS、项目专属 Skill、spec 和 plan”的规则写入 `AGENTS.md` 和两个项目专属 Skill。
- README、桌面应用设计文档和实施计划已同步记录本次新增的响应式书库、下载进度和主题设置。
- 读取最近开发记录时发现旧条目存在 mojibake 乱码；本次未大面积改写旧历史内容，新增记录保持正常 UTF-8，并将该问题作为后续文档清理风险保留。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，18 项通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py src\jmcomic_shelf\ui\theme.py`，通过。
- 已运行 offscreen `MainWindow` 初始化烟测，窗口标题正常输出为 `JMComic Shelf`。

## 2026-06-18 02:32:47 +08:00

### 修改范围

- 桌面端 Fluent UI 背景框与布局修复
- 下载结果表格样式修复
- 书库封面网格左对齐修复
- 项目术语修正
- 开发记录

### 涉及文件

- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/styles.py`
- `src/jmcomic_shelf/ui/download_page.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `development-log.md`

### 具体内容

- 根据用户反馈，把相关术语修正为“技术栈与限制”，避免后续对项目规则和 spec 的理解跑偏。
- 为 `FluentWindow` 右侧 `stackedWidget` 增加深色 Fluent 面板背景、边框、圆角和内边距，让主内容区形成类似参考项目 LaunchDock 的背景框，而不是漂在纯色背景上。
- 调整下载页结果表格：隐藏异常突兀的左侧行头，开启网格线，为表头和单元格增加竖向分隔线，并固定 `JM号` 与 `状态` 列宽，避免两列贴得太近。
- 调整书库页封面网格：封面卡片固定宽度、网格左上对齐、使用固定横向间距，并在右侧加入伸展占位，让多余空间留在右边，不再根据书本数量平均分散整行。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，17 个桌面端相关测试全部通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，结果通过。
- 本次没有触发真实下载；没有提交账号密码、cookie、token、代理凭据、下载内容、PDF、封面缓存或本地 `catalog.md`。
## 2026-06-18 02:02:07 +08:00

### 修改范围

- 桌面端 Fluent UI 风格修复
- 书库下载目录递归扫描与索引重建
- 项目协作规则、桌面端设计文档和实施计划修复
- 项目专属 Skill 更新
- 开发记录

### 涉及文件

- `src/jmcomic_shelf/index_service.py`
- `src/jmcomic_shelf/download_service.py`
- `src/jmcomic_shelf/detail_service.py`
- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/library_page.py`
- `src/jmcomic_shelf/ui/download_page.py`
- `src/jmcomic_shelf/ui/detail_page.py`
- `src/jmcomic_shelf/ui/settings_page.py`
- `src/jmcomic_shelf/ui/styles.py`
- `tests/test_jmcomic/test_shelf_index_service.py`
- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `.gitignore`
- `development-log.md`

### 具体内容

- 根据用户截图反馈，确认此前 UI 根因是硬编码全局 `QWidget` 背景与 QFluentWidgets 暗色主题混用，导致主区域出现白色大画布、黑色文字块和突兀黑色内容区。
- 重新整理桌面端样式：主窗口保留 `FluentWindow`、左侧图标文字导航、Mica 和 QFluentWidgets 主题；移除全局白底覆盖，页面背景改为透明，强调色设为 `#00c8d7`。
- 重写书库、下载、查看详情、设置页中的用户可见中文文案，修复本次涉及文件里的 mojibake 乱码。
- 书库页改为每次 reload 时先读取设置中的下载目录并递归扫描，支持识别 `作者/JM号-标题/第n章/图片` 与 `JM号-标题.pdf`，再写入 SQLite 后显示。
- 设置页的“重建索引”按钮改为真实调用下载目录扫描逻辑，并显示扫描到的本地漫画数量。
- 查看详情页查询前也会同步扫描下载目录，以便识别刚下载或手动放入的本地 PDF。
- 修复下载服务 JM 号解析中的中文逗号分隔符，避免编码损坏后的正则影响输入解析。
- 参考用户提供的 `https://github.com/Dylanliiiii/LaunchDock`，读取其 `AGENTS.md`、项目专属 Skill 和 QFluentWidgets UI 结构，把“深色 Fluent、左侧导航、右侧卡片、青色强调、禁止突兀大黑块、开工前先读完整项目规则和 spec”写入本项目 `AGENTS.md`、项目 Skill、桌面端设计文档和实施计划。
- 将临时浅克隆参考目录 `.tmp_launchdock_ref/` 加入 `.gitignore`，避免参考项目文件进入提交。

### 验证情况

- 已运行 `$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v`，17 个桌面端相关测试全部通过。
- 已运行 `$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`，结果通过。
- 本次没有触发真实下载；没有提交账号密码、cookie、token、代理凭据、下载内容、PDF、封面缓存或本地 `catalog.md`。

## 2026-06-18 01:41:17 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤 Fluent UI 澹虫仮澶?- 涔﹀簱绱㈠紩鍐欏叆娴佺▼淇
- 娴呰壊/娣辫壊鑳屾櫙閫傞厤
- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `src/jmcomic_shelf/download_service.py`
- `src/jmcomic_shelf/ui/main_window.py`
- `src/jmcomic_shelf/ui/styles.py`
- `src/jmcomic_shelf/ui/download_page.py`
- `tests/test_jmcomic/test_shelf_download_service.py`
- `development-log.md`

### 鍏蜂綋鍐呭

- 鐢ㄦ埛鍙嶉涓婁竴娆′慨澶嶆妸 QFluentWidgets/Windows Fluent 椋庢牸鏀瑰亸浜嗭紱鏈灏嗕富绐楀彛鎭㈠涓?`FluentWindow`銆乣NavigationInterface`銆乣FluentIcon` 鐨?QFluentWidgets 妗嗘灦锛屼笉鍐嶇敤鏅€?`QListWidget` 鏇夸唬渚ц竟瀵艰埅銆?- 淇濈暀渚ц竟鏍忛粯璁ゅ睍寮€锛屽搴︽敹鏁涘埌 `180`锛屽苟缁х画浣跨敤 QFluentWidgets 鑷甫瀵艰埅椋庢牸銆?- 绂佺敤 `Mica` 鏁堟灉骞剁粰瀵艰埅鍜岀獥鍙ｈˉ娴呰壊鑳屾櫙锛岄伩鍏嶆祬鑹叉ā寮忔垨 offscreen 鐜涓嬪乏渚у尯鍩熸覆鏌撴垚澶ч潰绉粦搴曪紱椤甸潰鍐呴儴鏍峰紡鏀逛负鎸夊綋鍓?QFluentWidgets 涓婚閫夋嫨娴呰壊鎴栨繁鑹茶儗鏅€?- 涔﹀簱涓嶆樉绀轰笅杞藉唴瀹圭殑鏍瑰洜鏄闈笅杞芥湇鍔′笅杞芥垚鍔熷悗娌℃湁鍐欏叆妗岄潰绔?SQLite 绱㈠紩锛涙湰娆¤ `DownloadService.run_task()` 鍦ㄤ笅杞芥垚鍔熷悗涓诲姩鎶?album 鍏冩暟鎹啓鍏?`%APPDATA%/JMComic Shelf/shelf.db`銆?- 涓嬭浇鏈嶅姟浼氬湪璁剧疆鐨勪笅杞界洰褰曚腑鏌ユ壘 `JM{jm_id}-*.pdf`锛屾壘鍒板悗鎶?PDF 璺緞鍐欏叆绱㈠紩锛屼究浜庝功搴撻〉鐐瑰嚮灏侀潰鎵撳紑 PDF銆?- 涓荤獥鍙ｅ垏鎹㈠埌涔﹀簱椤垫椂浼氳皟鐢ㄩ〉闈?`reload()`锛屼笅杞藉畬鎴愬悗鍥炲埌涔﹀簱鍗冲彲閲嶆柊璇诲彇绱㈠紩銆?- 璁板綍鐢ㄦ埛鎻愪緵鐨?UI 鍙傝€冮」鐩畬鏁撮摼鎺ワ細`https://github.com/Dylanliiiii/LaunchDock`锛屽悗缁闈?UI 杩唬搴斿弬鑰冨叾 QFluentWidgets 椋庢牸鎺掔増锛岃€屼笉鏄敼鎴愭櫘閫?Qt 渚ц竟鏍忋€?
### 楠岃瘉鎯呭喌

- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_download_service tests.test_jmcomic.test_shelf_settings tests.test_jmcomic.test_shelf_library_page -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\styles.py src\jmcomic_shelf\ui\download_page.py`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?offscreen 涓荤獥鍙ｆ埅鍥炬鏌ワ紝纭宸叉仮澶?QFluentWidgets 瀵艰埅澹筹紝鍐呭鍖哄拰宸︿晶鏍忎笉鍐嶅嚭鐜板ぇ闈㈢Н榛戝簳锛沷ffscreen 鎴浘涓殑涓枃鏂瑰潡涓虹灞忓瓧浣撴覆鏌撻棶棰橈紝鐢ㄦ埛鏈満姝ｅ父绐楀彛鎴浘涓枃鍙樉绀恒€?- 鏈鏈疄闄呰Е鍙戠湡瀹炰笅杞斤紝涓嶆秹鍙婅处鍙峰瘑鐮併€乧ookie銆乼oken銆佷唬鐞嗗嚟鎹€佷笅杞藉唴瀹广€丳DF銆佸皝闈㈢紦瀛樻垨鏈湴 `catalog.md`銆?
## 2026-06-18 01:26:23 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤 UI 鍙敤鎬т慨澶?- 涓嬭浇涓庢煡鐪嬭鎯呴敊璇彁绀?- 璁剧疆椤佃矾寰勮鏄庝笌閰嶇疆鍚屾
- 婧愮爜鍚姩榛樿閰嶇疆璺緞
- 寮€鍙戣褰?
### 娑夊強鏂囦欢

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

### 鍏蜂綋鍐呭

- 鏍规嵁鐢ㄦ埛瀹為檯璇曠敤鍙嶉锛岀Щ闄ゆ闈㈤〉闈腑鐢?QScrollArea/QTableWidget/FluentWindow 榛樿鏍峰紡鏆撮湶鍑虹殑娣辫壊澶у潡鑳屾櫙锛屾敼涓烘祬鑹?Windows 椋庢牸宸ヤ綔鍖恒€?- 灏嗕富绐楀彛浠?`FluentWindow` 榛樿瀵艰埅鏀逛负椤圭洰鍙帶鐨勬祬鑹插乏渚ф爮锛岄粯璁ゅ睍寮€锛屽搴︽敹鏁涘埌閫傞厤瀵艰埅鏂囧瓧锛涘鑸」鍖呭惈涓绘爣棰樺拰涓€鍙ュ皬瀛楄鏄庛€?- 涔﹀簱銆佷笅杞姐€佹煡鐪嬭鎯呫€佽缃〉鍧囪ˉ鍏呬竴鍙ョ畝鐭搷浣滆鏄庯紝閬垮厤鍙湁鏍囬鍜岃緭鍏ユ銆?- 涓嬭浇鏈嶅姟鍦?`jmcomic-option.yml` 鏈€夋嫨鎴栬矾寰勪笉瀛樺湪鏃讹紝鐩存帴杩斿洖涓枃鍙閿欒锛屼笉鍐嶆妸绌鸿矾寰勪紶缁欎笂娓稿鑷?`unknown mode: '', acceptable modes=['yml', 'json', 'pickle']`銆?- 鏌ョ湅璇︽儏鏈嶅姟鍚屾牱鏍￠獙閰嶇疆鏂囦欢璺緞锛岃鎯呴〉鎹曡幏寮傚父骞舵樉绀哄湪椤甸潰涓紝閬垮厤鐢ㄦ埛鐐瑰嚮鍚庢棤鍙嶅簲銆?- 璁剧疆椤垫敼涓哄垎鍧楄鏄庯細涓嬭浇鐩綍鐢ㄤ簬淇濆瓨婕敾鍥剧墖銆丳DF 鍜?`catalog.md`锛涢厤缃枃浠舵槸 `jmcomic-option.yml`锛涘簲鐢ㄦ暟鎹洰褰曠敤浜?`settings.json`銆乣shelf.db` 鍜屽皝闈㈢缉鐣ュ浘缂撳瓨銆?- 淇濆瓨璁剧疆鏃讹紝濡傛灉閫夋嫨浜?`jmcomic-option.yml` 鍜屼笅杞界洰褰曪紝浼氬悓姝ユ洿鏂伴厤缃枃浠朵腑鐨?`dir_rule.base_dir`锛岃 UI 閲岃缃殑涓嬭浇鐩綍鐪熸浣滅敤浜庝笅杞芥祦绋嬨€?- 婧愮爜鍚姩鑴氭湰 `start-jmcomic-shelf.bat` 鏂板 `JMCOMIC_SHELF_PROJECT_DIR` 鐜鍙橀噺锛涙闈㈢榛樿閰嶇疆鏂囦欢璺緞浼氳嚜鍔ㄦ寚鍚戞簮鐮佹牴鐩綍涓嬬殑 `jmcomic-option.yml`锛屽噺灏戦娆′娇鐢ㄧ殑鐚滄祴鎴愭湰銆?
### 楠岃瘉鎯呭喌

- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_settings tests.test_jmcomic.test_shelf_download_service tests.test_jmcomic.test_shelf_detail_service tests.test_jmcomic.test_shelf_option_service -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_library_page -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\settings.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\option_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py`锛岀粨鏋滈€氳繃銆?- 宸茬敤 offscreen 涓荤獥鍙ｆ埅鍥炬鏌ユ繁鑹插儚绱犳瘮渚嬶紝娣辫壊鍖哄煙绾?`0.0046`锛岀敤浜庣‘璁や笉鍐嶅嚭鐜板ぇ闈㈢Н榛戣壊鑳屾櫙銆?- 鏈鏈疄闄呰Е鍙戜笅杞斤紝涓嶆秹鍙婅处鍙峰瘑鐮併€乧ookie銆乼oken銆佷唬鐞嗗嚟鎹€佷笅杞藉唴瀹广€丳DF銆佸皝闈㈢紦瀛樻垨鏈湴 `catalog.md`銆?
## 2026-06-18 01:05:32 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤婧愮爜鍚姩鑴氭湰
- README 妗岄潰绔惎鍔ㄨ鏄?- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `start-jmcomic-shelf.bat`
- `README.md`
- `assets/readme/README-en.md`
- `development-log.md`

### 鍏蜂綋鍐呭

- 鐢ㄦ埛鐩存帴鍦ㄩ」鐩牴鐩綍杩愯 `python -m jmcomic_shelf.app` 鏃讹紝褰撳墠 Python 鐜鎵句笉鍒?`src/jmcomic_shelf`锛屾姤閿?`ModuleNotFoundError: No module named 'jmcomic_shelf'`銆?- 鏍瑰洜鏄闈㈢浠ｇ爜褰撳墠浠嶄互婧愮爜褰㈠紡鏀惧湪 `src/` 涓嬶紝灏氭湭閫氳繃 `pip install -e .` 鎴栨寮忔墦鍖呭畨瑁呭埌 Python 鐜锛涚洿鎺?`python -m ...` 涓嶄細鑷姩鎶?`src` 鍔犲叆妯″潡鎼滅储璺緞銆?- 鏂板 `start-jmcomic-shelf.bat`锛屽弻鍑绘椂鑷姩璁剧疆 `PYTHONPATH=%~dp0src`锛屽啀杩愯 `python -m jmcomic_shelf.app`锛岃婧愮爜浠撳簱闃舵涔熻兘鐩存帴鍚姩妗岄潰搴旂敤銆?- README 鍜岃嫳鏂?README 琛ュ厖璇存槑锛氭簮鐮佷粨搴撻樁娈典紭鍏堝弻鍑?`start-jmcomic-shelf.bat`锛涘畨瑁呭寘鎴?editable install 鍚庢墠浣跨敤 `jmcomic-shelf` 鍛戒护銆?
### 楠岃瘉鎯呭喌

- 宸茶繍琛?`$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; python -c "from PySide6.QtWidgets import QApplication; from jmcomic_shelf.ui.main_window import MainWindow; app=QApplication([]); window=MainWindow(); print(window.windowTitle())"`锛岀粨鏋滆緭鍑?`JMComic Shelf`銆?- 鏈鏈疄闄呰Е鍙戜笅杞斤紝涓嶆秹鍙婅处鍙峰瘑鐮併€乧ookie銆乼oken銆佷唬鐞嗗嚟鎹€佷笅杞藉唴瀹广€丳DF銆佸皝闈㈢紦瀛樻垨鏈湴 `catalog.md`銆?
## 2026-06-18 00:45:23 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤 v1 鍩虹瀹炵幇
- 妗岄潰涔﹀簱 SQLite 绱㈠紩
- 闈炶鍓皝闈㈢缉鐣ュ浘缂撳瓨
- 涓嬭浇銆佽鎯呫€佹枃浠舵搷浣滄湇鍔?- PySide6 + QFluentWidgets 妗岄潰鍏ュ彛鍜岄〉闈?- README 妗岄潰绔鏄?- 寮€鍙戣褰?
### 娑夊強鏂囦欢

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

### 鍏蜂綋鍐呭

- 鏂板 `jmcomic_shelf` 妗岄潰绔寘锛屾彁渚?Windows 鐢ㄦ埛鏁版嵁鐩綍銆乣settings.json`銆乣shelf.db` 鍜屽皝闈㈢紦瀛樼洰褰曠殑缁熶竴璺緞鍏ュ彛銆?- 鏂板 `ShelfSettings`锛屼繚瀛樺綋鍓嶄笅杞界洰褰曘€乣jmcomic-option.yml` 璺緞鍜屽簲鐢ㄦ暟鎹洰褰曪紱妗岄潰绔涓€鐗堜粛鍙鐞嗗綋鍓嶈缃噷鐨勪竴涓笅杞界洰褰曘€?- 鏂板 `ShelfDatabase` SQLite 绱㈠紩锛屼繚瀛樹綔鍝併€佷綔鑰呫€佹爣绛俱€佺珷鑺傘€丳DF 璺緞鍜屽皝闈㈢缉鐣ュ浘璺緞锛涚┖鏌ヨ瀵瑰簲 UI 鐨?`鍏ㄩ儴`锛屼笉鎶?`鍏ㄩ儴` 鍐欐垚鐪熷疄鏍囩銆?- 鏂板 `CoverCache`锛屽彧鐢熸垚妗岄潰绔娇鐢ㄧ殑 JPEG 缂╃暐鍥撅紝鎸夊搴︾瓑姣斾緥缂╁皬鍜屽帇缂╃敾璐紝涓嶈鍓€佷笉鎴柇銆佷笉淇濆瓨鍘熷浘鍓湰銆?- 鏂板 `record_from_album` 鍜?`group_by_author`锛屽鐢ㄧ幇鏈?`CatalogPlugin.build_album_info()`锛岃 Markdown 鎬荤洰褰曞拰妗岄潰 SQLite 绱㈠紩鍏变韩鍚屼竴濂椾綔鑰呫€佹爣绛惧拰绔犺妭鎻愬彇閫昏緫銆?- 鍦?`src/jmcomic/jm_plugin.py` 涓柊澧?`shelf_index` 鎻掍欢锛岀敤浜庝笅杞藉悗鍐欏叆妗岄潰绔?SQLite 绱㈠紩锛涘師 `catalog` 鎻掍欢缁х画缁存姢涓嬭浇鐩綍涓嬬殑 `catalog.md`銆?- 鏂板涓嬭浇鏈嶅姟锛屾敮鎸佺┖鏍笺€侀€楀彿鍜屾崲琛岃緭鍏ュ涓?JM 鍙凤紝淇濈暀澶辫触浠诲姟閲嶈瘯鐘舵€併€?- 鏂板璇︽儏鏈嶅姟鍜屾枃浠舵搷浣滄湇鍔★紝鐢ㄤ簬鑾峰彇鍗曚釜 JM 鍙疯鎯呫€佹墦寮€ PDF銆佸湪鏂囦欢璧勬簮绠＄悊鍣ㄤ腑瀹氫綅 PDF銆?- 鏂板 `jmcomic-shelf` 鍛戒护鍜?PySide6 + QFluentWidgets 渚濊禆锛屽缓绔嬪乏渚у浘鏍囨枃瀛楀鑸細`涔﹀簱`銆乣涓嬭浇`銆乣鏌ョ湅璇︽儏`銆乣璁剧疆`銆?- 涔﹀簱椤靛疄鐜?`鍏ㄩ儴`銆丣M 鍙?浣滆€?鏍囩鎼滅储銆佷綔鑰呭垎缁勩€佸皝闈㈠崱鐗囥€佺偣鍑绘墦寮€ PDF 鍜屽彸閿祫婧愮鐞嗗櫒瀹氫綅锛涘綋 `%APPDATA%/JMComic Shelf/` 鏆備笉鍙啓鎴栫储寮曚笉鍙鏃讹紝椤甸潰鏄剧ず绌虹姸鎬佽€屼笉鏄鑷村簲鐢ㄥ惎鍔ㄥけ璐ャ€?- 涓嬭浇椤靛疄鐜板 JM 鍙疯緭鍏ャ€佷换鍔¤〃鏍煎拰澶辫触閲嶈瘯鎸夐挳銆?- 鏌ョ湅璇︽儏椤靛疄鐜板崟 JM 鍙锋煡璇紝涓嶄繚瀛樻煡璇㈠巻鍙诧紱鏈湴绱㈠紩鏈?PDF 鏃跺彲鎵撳紑鎴栧畾浣嶃€?- 璁剧疆椤靛疄鐜颁笅杞界洰褰曘€侀厤缃枃浠躲€佸簲鐢ㄦ暟鎹洰褰曞睍绀哄拰灏侀潰缂撳瓨娓呯悊锛涢噸寤虹储寮曟寜閽厛浣滀负鍚庣画鎵弿鏈嶅姟鍏ュ彛棰勭暀銆?- README 鍜岃嫳鏂?README 琛ュ厖妗岄潰绔懡浠ゃ€佹暟鎹綅缃€佷笅杞藉唴瀹逛笌 `catalog.md` 鐨勪繚鐣欒鍒欙紝骞惰褰曞畬鏁村弬鑰冮摼鎺ワ細`https://github.com/ok-oldking/ok-script`銆乣https://github.com/ok-oldking/pyappify`銆?
### 楠岃瘉鎯呭喌

- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_settings -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_database -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_cover_cache -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_index_service -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_download_service -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest tests.test_jmcomic.test_shelf_library_page -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest discover -s tests -p test_jm_plugin.py -k shelf_index -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛?`python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py`锛岀粨鏋滈€氳繃銆?- 宸茶繍琛屼富绐楀彛 offscreen 鏋勯€犳鏌ワ紝鑳芥垚鍔熷疄渚嬪寲骞惰緭鍑?`JMComic Shelf`銆?- 鏈鏈彁浜?`jmcomic-option.yml`銆佽处鍙峰瘑鐮併€乧ookie銆乼oken銆佷唬鐞嗗嚟鎹€佷笅杞藉唴瀹广€丳DF銆佸皝闈㈢紦瀛樻垨鏈湴 `catalog.md`銆?
## 2026-06-18 00:03:12 +08:00

### 淇敼鑼冨洿

- 澶栭儴鍙傝€冮摼鎺ヨ褰曡鍒?- 妗岄潰搴旂敤璁捐鏂囨。纭椤规敹鏉?- 妗岄潰搴旂敤 v1 瀹炵幇璁″垝
- 椤圭洰鍗忎綔璇存槑
- 椤圭洰涓撳睘 Skill
- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`
- `development-log.md`

### 鍏蜂綋鍐呭

- 鐢ㄦ埛纭璁捐鏂囨。涓殑涓変釜榛樿寤鸿锛氫笅杞介〉绗竴鐗堟敮鎸佸け璐ラ噸璇曟寜閽紱鏌ョ湅璇︽儏椤电涓€鐗堜笉淇濆瓨鏌ヨ鍘嗗彶锛涜缃〉绗竴鐗堝彧鏄剧ず搴旂敤鏁版嵁鐩綍鍜屾竻鐞嗙紦瀛橈紝涓嶅仛搴旂敤鏁版嵁鐩綍杩佺Щ銆?- 灏嗚璁℃枃妗ｄ腑鐨勨€滃緟鐢ㄦ埛纭鈥濇敼涓衡€滃凡纭鍐崇瓥鈥濓紝閬垮厤鍚庣画瀹炵幇璁″垝瀛樺湪鎮┖椤广€?- 鍦ㄨ璁℃枃妗ｄ腑琛ュ厖瀹屾暣鍙傝€冮摼鎺ワ細`ok-oldking/ok-script` 浣跨敤 `https://github.com/ok-oldking/ok-script`锛宍ok-oldking/pyappify` 浣跨敤 `https://github.com/ok-oldking/pyappify`銆?- 鐢ㄦ埛瑕佹眰鍚庣画鏂囨。鎴栧紑鍙戣褰曞紩鐢ㄥ弬鑰冮」鐩€佹暀绋嬨€佸伐鍏锋垨澶栭儴璧勬枡鏃讹紝搴斿敖閲忎繚鐣欏畬鏁?URL锛屼笉鑳藉彧鍐欓」鐩悕锛涘凡鍚屾鍐欏叆 `AGENTS.md` 鍜岄」鐩笓灞?Skill锛屾柟渚挎柊瀵硅瘽鎴栧叾浠栨櫤鑳戒綋杩芥函鏉ユ簮銆?- 鏂板妗岄潰搴旂敤 v1 瀹炵幇璁″垝锛屾媶鍒嗕负璁剧疆璺緞銆丼QLite銆佸皝闈㈢紦瀛樸€佺储寮曟湇鍔°€佺储寮曟彃浠躲€佷笅杞芥湇鍔°€佹枃浠舵搷浣溿€佹闈㈠叆鍙ｃ€乁I 椤甸潰銆丷EADME 鍜屾渶缁堥獙璇佺瓑浠诲姟銆?
### 楠岃瘉鎯呭喌

- 鏈涓哄崗浣滆鍒欍€佽璁℃枃妗ｅ拰瀹炵幇璁″垝鏇存柊锛屾湭杩愯浠ｇ爜鍗曞厓娴嬭瘯銆?- 宸叉鏌ユ枃妗ｅ唴瀹规湭璁板綍璐﹀彿銆佸瘑鐮併€乧ookie銆乼oken銆佺湡瀹炴湰鍦颁笅杞界洰褰曘€丳DF 鎴?`catalog.md` 鍐呭銆?
## 2026-06-17 23:57:24 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤 v1 璁捐鏂囨。
- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `docs/superpowers/specs/2026-06-17-desktop-app-design.md`
- `development-log.md`

### 鍏蜂綋鍐呭

- 鏂板妗岄潰搴旂敤 v1 璁捐鏂囨。锛屾敹鏉熺洰鍓嶅凡纭鐨?PySide6 + QFluentWidgets 鎶€鏈柟鍚戙€佹柟妗?A 宸︿晶瀵艰埅宸ヤ綔鍙般€佷功搴撻〉銆佷笅杞介〉銆佹煡鐪嬭鎯呴〉銆佽缃〉銆丼QLite 鏁版嵁瀛樺偍銆丮arkdown 鎬荤洰褰曚繚鐣欍€佸皝闈㈢紦瀛樿鍒欍€佹暟鎹祦銆侀敊璇鐞嗐€佹祴璇曠瓥鐣ュ拰闈炵洰鏍囥€?- 璁捐鏂囨。鏄庣‘绗竴鐗堝彧绠＄悊褰撳墠璁剧疆閲岀殑涓€涓笅杞界洰褰曪紝SQLite 浣滀负妗岄潰绔富绱㈠紩锛宍catalog.md` 缁х画浣滀负鐢ㄦ埛鍙洿鎺ユ墦寮€鏌ョ湅鐨勬€荤洰褰曘€?- 璁捐鏂囨。鏄庣‘灏侀潰缂╃暐鍥惧彧鑳界瓑姣斾緥缂╁皬鍜屽帇缂╃敾璐紝涓嶅厑璁歌鍓€佹埅鏂垨鍙栧眬閮ㄧ敾闈€?- 涓嬩竴姝ラ渶瑕佺敤鎴峰闃呰璁℃枃妗ｄ腑鐨勫緟纭椤癸紝鍐嶈繘鍏ュ疄鐜拌鍒掗樁娈点€?
### 楠岃瘉鎯呭喌

- 鏈涓鸿璁℃枃妗ｆ洿鏂帮紝鏈繍琛屼唬鐮佸崟鍏冩祴璇曘€?- 宸叉鏌ユ枃妗ｅ唴瀹规湭璁板綍璐﹀彿銆佸瘑鐮併€乧ookie銆乼oken銆佺湡瀹炴湰鍦颁笅杞界洰褰曘€丳DF 鎴?`catalog.md` 鍐呭銆?
## 2026-06-17 23:48:32 +08:00

### 淇敼鑼冨洿

- 妗岄潰涔﹀簱鏁版嵁鏋舵瀯瑙勫垝
- 涓嬭浇鐩綍涓庣敤鎴锋暟鎹綅缃鍒?- 灏侀潰缂撳瓨瑙勫垯纭
- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `development-log.md`

### 鍏蜂綋鍐呭

- 鐢ㄦ埛纭绗竴鐗堟闈功搴撳彧绠＄悊褰撳墠璁剧疆閲岀殑涓€涓笅杞界洰褰曪紝涔熷彧鏇存柊杩欎竴涓笅杞界洰褰曘€?- 妗岄潰绔富鏁版嵁婧愰噰鐢ㄧ嫭绔嬬粨鏋勫寲绱㈠紩锛屼紭鍏堣璁′负 SQLite 鏁版嵁搴擄紱鍘熸湁 `catalog.md` 缁х画淇濈暀锛屼綔涓虹敤鎴峰彲鐩存帴鎵撳紑鏌ョ湅鐨?Markdown 鎬荤洰褰曪紝涓嶄綔涓烘闈㈢涓荤储寮曘€?- 涓嬭浇鐩綍浠嶇敱鐢ㄦ埛鑷畾涔夛紝涓嬭浇鍚庣殑鍥剧墖銆丳DF 鍜?`catalog.md` 淇濇寔鍦ㄧ敤鎴烽€夋嫨鐨勪笅杞芥牴鐩綍涓嬶紝鐩綍缁撴瀯缁х画鎺ヨ繎褰撳墠 `浣滆€?/ JM鍙?浣滃搧鍚?/ 绗琋绔燻 鐨勮鍒欍€?- 妗岄潰搴旂敤鐢ㄦ埛鏁版嵁榛樿鏀惧湪 Windows 鐢ㄦ埛鏁版嵁鐩綍锛屼緥濡?`%APPDATA%/JMComic Shelf/`锛岀敤浜庝繚瀛?`shelf.db`銆乣settings.json` 鍜屽皝闈㈢紦瀛橈紱绋嬪簭瀹夎鐩綍鍙斁搴旂敤浠ｇ爜锛岄伩鍏嶅悗缁嚜鍔ㄦ洿鏂拌鐩栫敤鎴锋暟鎹€?- 鐢ㄦ埛鎷呭績鏁版嵁搴撴斁鍦?C 鐩樺彲鑳藉彉澶э紱褰撳墠鍒ゆ柇鏄?SQLite 鏂囨湰绱㈠紩鏈韩浣撶Н寰堝皬锛屼富瑕佺┖闂存潵鑷皝闈㈢紦瀛樸€傝璁′笂灏侀潰缂撳瓨搴斿彲娓呯悊銆佸彲閲嶅缓锛屽悗缁彲棰勭暀楂樼骇璁剧疆杩佺Щ搴旂敤鏁版嵁鐩綍銆?- 灏侀潰缂撳瓨鍙繚瀛樻闈㈢浣跨敤鐨勭缉鐣ュ浘锛屼笉淇濆瓨鍘熷浘锛涚缉鐣ュ浘蹇呴』瀹屾暣淇濈暀灏侀潰鍐呭锛屽彧鍏佽绛夋瘮渚嬬缉灏忓拰閫傚害鍘嬬缉鐢昏川锛屼笉鍏佽瑁佸壀銆佹埅鏂垨鍙彇灞€閮ㄧ敾闈€?- 鈥滃叏閮ㄢ€濅綔涓烘闈㈢鍐呯疆绛涢€夊櫒瀹炵幇锛屼笉鍐欐垚姣忔湰浣滃搧鐨勭湡瀹炴爣绛撅紱榛樿灞曠ず鍏ㄩ儴宸蹭笅杞戒綔鍝併€?
### 楠岃瘉鎯呭喌

- 鏈涓鸿鍒掕褰曟洿鏂帮紝鏈繍琛屼唬鐮佸崟鍏冩祴璇曘€?- 宸茬‘璁ゆ湭璁板綍璐﹀彿銆佸瘑鐮併€乧ookie銆乼oken銆佺湡瀹炴湰鍦颁笅杞界洰褰曘€丳DF 鎴?`catalog.md` 鍐呭銆?
## 2026-06-17 23:26:41 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤甯冨眬鏂规纭
- 涔﹀簱绛涢€夎鍒欒鍒?- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `development-log.md`

### 鍏蜂綋鍐呭

- 鐢ㄦ埛纭閲囩敤妗岄潰搴旂敤甯冨眬鏂规 A锛氬乏渚у鑸伐浣滃彴浣滀负涓绘鏋躲€?- 宸︿晶瀵艰埅鍚庣画瀹炵幇鏃跺簲浣跨敤鈥滃浘鏍?+ 鏂囧瓧鈥濈殑鍔熻兘鍏ュ彛锛屼笉浣跨敤鍙湁鍥炬爣鐨勭獎瀵艰埅锛涘叆鍙ｈ嚦灏戝寘鍚功搴撱€佷笅杞姐€佹煡鐪嬭鎯呭拰璁剧疆銆?- 涔﹀簱绛涢€夋暟鎹腑闇€瑕佷繚鐣欌€滃叏閮ㄢ€濆叆鍙ｏ紱榛樿鐘舵€佸睍绀哄凡缁忎笅杞界殑鍏ㄩ儴鍐呭锛屽啀鏍规嵁 JM 鍙枫€佷綔鑰呭悕鎴栨爣绛捐繘琛岀瓫閫夈€?- 鏈湴鍙鍖栬崏鍥?`.superpowers/brainstorm/desktop-app/layout-preview.html` 宸插悓姝ユ洿鏂颁负鏂规 A 鐨勨€滃浘鏍?+ 鏂囧瓧鈥濆鑸笌鈥滃叏閮ㄢ€濈瓫閫夊睍绀猴紱璇ョ洰褰曞凡琚?`.gitignore` 蹇界暐锛屼笉浣滀负姝ｅ紡椤圭洰鏂囦欢鎻愪氦銆?- 涓嬩竴姝ラ渶瑕佺户缁‘璁や功搴撶储寮曠殑鏁版嵁鏉ユ簮锛氱洿鎺ヨВ鏋愮幇鏈?`catalog.md`锛岃繕鏄湪涓嬭浇鍚庡悓姝ョ淮鎶や竴涓洿閫傚悎妗岄潰绔鍙栫殑缁撴瀯鍖栫储寮曘€?
### 楠岃瘉鎯呭喌

- 鏈涓鸿鍒掕褰曟洿鏂帮紝鏈繍琛屼唬鐮佸崟鍏冩祴璇曘€?- 宸茬‘璁ゆ湭璁板綍璐﹀彿銆佸瘑鐮併€乧ookie銆乼oken銆佺湡瀹炴湰鍦颁笅杞界洰褰曘€丳DF 鎴?`catalog.md` 鍐呭銆?
## 2026-06-17 23:07:55 +08:00

### 淇敼鑼冨洿

- 妗岄潰搴旂敤鍓嶆湡瑙勫垝璁板綍
- 椤圭洰鍗忎綔璇存槑
- 椤圭洰涓撳睘 Skill
- 鍙鍖栬崏鍥炬枃浠跺拷鐣ヨ鍒?
### 娑夊強鏂囦欢

- `AGENTS.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `.gitignore`
- `development-log.md`

### 鍏蜂綋鍐呭

- 纭涓嬩竴闃舵鐩爣鏄妸褰撳墠鑴氭湰寮忓伐浣滄祦鏁寸悊涓?Windows 妗岄潰搴旂敤锛岃鍒掍互 PySide6 + QFluentWidgets 瀹炵幇锛屽苟鍙傝€?`ok-oldking/ok-script` 鐨勫師鐢?Windows 椋庢牸銆?- 鍒濇闇€姹傚寘鎷細涓嬭浇鍔熻兘銆佹煡鐪嬭鎯呭姛鑳姐€佹湰鍦颁功搴撴煡鎵惧姛鑳姐€佹寜 JM 鍙?浣滆€?鏍囩绛涢€夈€佹寜浣滆€呭垎缁勫睍绀哄懡涓綔鍝併€佸皝闈㈠崱鐗囧睍绀恒€佺偣鍑诲皝闈㈡墦寮€ PDF銆佸彸閿湪鏂囦欢璧勬簮绠＄悊鍣ㄤ腑鎵撳紑 PDF 鎵€鍦ㄤ綅缃€?- 鍚庣画鎵撳寘鏂瑰悜鍊惧悜鐮旂┒ `ok-oldking/pyappify`锛岄伩鍏嶉粯璁や娇鐢?PyInstaller锛屽苟棰勭暀鑷姩鏇存柊鑳藉姏銆?- 鐢ㄦ埛纭寮€鍙戣褰曚篃搴旇褰曞繀瑕佺殑鍓嶆湡鎬濊矾銆佽鍒掔粨璁哄拰闃舵杩涘害锛涘洜姝ゆ洿鏂?`AGENTS.md` 鍜岄」鐩笓灞?Skill锛屾妸杩欐潯浣滀负鍚庣画鍗忎綔瑙勫垯銆?- 鐢ㄦ埛纭鍙娇鐢?brainstorming 鍙鍖栦即闅忔潵灞曠ず UI 鑽夊浘锛涘皢 `.superpowers/` 鍔犲叆 `.gitignore`锛岄伩鍏嶆湰鍦拌崏鍥句細璇濇枃浠惰繘鍏ヤ粨搴撱€?
### 楠岃瘉鎯呭喌

- 鏈涓洪」鐩崗浣滆鍒欎笌瑙勫垝璁板綍鏇存柊锛屾湭杩愯浠ｇ爜鍗曞厓娴嬭瘯銆?- 宸叉鏌ユ湰娆¤褰曟湭鍖呭惈璐﹀彿銆佸瘑鐮併€乧ookie銆乼oken銆佺湡瀹炴湰鍦颁笅杞界洰褰曘€丳DF 鎴?`catalog.md` 鍐呭銆?
## 2026-06-17 21:32:32 +08:00

### 淇敼鑼冨洿

- 鏈湴椤圭洰鐩綍鍛藉悕
- 椤圭洰鏂囨。涓庡崗浣滆鏄庢鏌?
### 娑夊強鏂囦欢

- `development-log.md`

### 鍏蜂綋鍐呭

- 鍑嗗灏嗘湰鍦伴」鐩枃浠跺す浠?`JMComic-Crawler-Python` 閲嶅懡鍚嶄负 `JMComic-Shelf`锛屼笌 GitHub 浠撳簱鍚嶄繚鎸佷竴鑷淬€?- 妫€鏌?README銆佽嫳鏂?README銆乣AGENTS.md` 鍜岄」鐩笓灞?Skill 涓殑 `JMComic-Crawler-Python` 寮曠敤锛岀‘璁よ繖浜涘紩鐢ㄥ潎鎸囧悜涓婃父鍘熶綔鑰呴」鐩紝搴斾繚鐣欎綔涓烘潵婧愯鏄庯紝涓嶅簲璇敼涓哄綋鍓嶄粨搴撳悕銆?- 纭褰撳墠浠撳簱杩滅▼浠嶄负 `origin -> Dylanliiiii/JMComic-Shelf`锛宍upstream -> hect0x7/JMComic-Crawler-Python`銆?
### 楠岃瘉鎯呭喌

- 宸茶繍琛屾枃鏈绱紝纭娌℃湁闇€瑕佷慨鏀圭殑鏈湴鏃х洰褰曞悕寮曠敤銆?- 宸茬‘璁?`D:\Others\JMComic-Shelf` 褰撳墠涓嶅瓨鍦紝鍙互鐢ㄤ簬閲嶅懡鍚嶃€?
## 2026-06-17 21:31:00 +08:00

### 淇敼鑼冨洿

- 椤圭洰鍗忎綔璇存槑
- 椤圭洰涓撳睘 Skill
- 寮€鍙戣褰?
### 娑夊強鏂囦欢

- `AGENTS.md`
- `README.md`
- `assets/readme/README-en.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-project/agents/openai.yaml`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/agents/openai.yaml`
- `development-log.md`

### 鍏蜂綋鍐呭

- 鏂板 `AGENTS.md`锛岃褰曢」鐩畾浣嶃€佷笂娓稿叧绯汇€佹晱鎰熼厤缃€佷笅杞界洰褰曘€丳DF銆丮arkdown 鎬荤洰褰曘€乄indows 鑴氭湰銆佽川閲忚姹傚拰 GitHub 缁存姢瑙勫垯銆?- 鏂板 `jmcomic-shelf-project` 椤圭洰涓撳睘 Skill锛岀敤浜庡悗缁淮鎶や笅杞藉伐浣滄祦銆佺洰褰曟彃浠躲€丷EADME銆佽剼鏈拰妗岄潰搴旂敤瑙勫垝銆?- 鏂板 `jmcomic-shelf-maintenance` 椤圭洰涓撳睘 Skill锛岀敤浜庡悗缁瘡娆′慨鏀瑰悗鐨勫紑鍙戣褰曘€侀獙璇併€乧ommit 鍜?GitHub push銆?- 鏂板 `development-log.md`锛岀敤浜庤褰曢」鐩悗缁紨杩涖€?- 灏?README 涓殑鏈満缁濆璺緞绀轰緥鏀逛负鐩稿閰嶇疆鏂囦欢绀轰緥锛岄伩鍏嶅紑婧愭枃妗ｄ緷璧栫淮鎶よ€呯數鑴戣矾寰勩€?
### 楠岃瘉鎯呭喌

- 鏈涓洪」鐩崗浣滆鏄庛€丼kill 鍜?README 鏂囨。鏇存柊锛屾湭杩愯搴旂敤鍗曞厓娴嬭瘯銆?- 宸插弬鑰?LaunchDock 鐨?`AGENTS.md`銆侀」鐩笓灞?Skill 鍜?`development-log.md` 缁撴瀯銆?

