# JMComic Shelf 桌面应用 v1 实施计划

## 当前基线

桌面端已位于 `src/jmcomic_shelf/`，使用 PySide6 + QFluentWidgets。

已有模块：

- `settings.py`：保存下载目录、`jmcomic-option.yml`、应用数据目录和外观主题模式，主题支持跟随系统、浅色和深色。
- `database.py`：SQLite 书库索引。
- `cover_cache.py`：完整等比例封面缩略图。
- `index_service.py`：JM album 到 SQLite 的映射，以及从下载目录重建索引。
- `download_service.py`：解析多个 JM 号、执行下载、下载后将 PDF 归档到第一作者目录、缓存根目录 `Cover/` 封面并写入索引。
- `ui/theme.py`：集中处理 QFluentWidgets 主题映射和强调色。
- `detail_service.py`：查询单个 JM 号详情，并为预览页缓存可显示的封面图。
- `file_actions.py`：打开 PDF 和在资源管理器中定位。
- `repair_service.py`：扫描历史残留图片目录，补全缺失 PDF，成功后清理原图片目录，并复用重建索引同步 SQLite 和 `catalog.md`。
- `ui/`：本地书库、禁漫下载、禁漫预览、书库修复、禁漫官网、设置页面。
- `ui/official_site_page.py`：分组展示官方入口，并把点击交给系统默认浏览器。
- `pyappify.yml`：PyAppify 桌面版发布配置，`main_script` 指向 `run-jmcomic-shelf.py`。
- `run-jmcomic-shelf.py`：PyAppify 源码入口，优先加载当前 `working/src` 后启动桌面端。
- `.github/workflows/release.yml`：`v*` tag 触发的 GitHub Release 打包流程。

## 必须保持的 UI 方向

- `MainWindow` 使用 `FluentWindow`。
- 左侧导航使用 QFluentWidgets 导航接口，图标 + 中文文字。
- 主区域背景透明，交给 QFluentWidgets 主题处理。
- 不再使用全局 `QWidget { background: ... }` 覆盖主题。
- 主要页面使用 `CardWidget`、`SmoothScrollArea`、`TitleLabel`、`SubtitleLabel`、`CaptionLabel`。
- 视觉参考 `https://github.com/Dylanliiiii/LaunchDock` 的深色 Fluent 工具应用组织方式。
- 禁止回到白色大画布、黑色说明条、黑色大矩形内容区。

## 后续任务

### 1. 书库索引稳定化

- 保留 `rebuild_index_from_download_dir()`。
- 扩展扫描规则以兼容第一作者目录下的 PDF、根目录 `Cover/` 封面缓存、更多 PDF 位置和旧章节目录形态。
- 为无 PDF 但有图片目录的作品显示卡片，并禁用打开 PDF。
- 书库记录保存本地漫画目录路径，供批量删除本地文件时使用。
- 书库页提供批量管理模式，支持选择、多选、全选、反选、取消全选和删除选中；删除前必须二次确认。
- 本地书库页的 `全部` 筛选器保留总数、青色下划线和轻量背景框；侧边栏展开/收起触发布局变化时，应延迟重排封面网格，降低反复切换时的卡顿。
- 本地书库页在 `全部` 旁提供 `分类` 按钮，展开当前书库出现过的全部标签；标签面板最多展示五行并支持滚动；可同时选择多个标签，满足任一选中标签的作品都会显示；搜索输入需要防抖，避免输入法组合文字时频繁重绘；点击标签筛选时应复用已有标签按钮，只更新选中样式和作品区，避免分类面板整块闪烁。
- `catalog.md` 和 SQLite 中的标签统一转换为中文简体；标题、作者和章节标题保持来源文本；多作者作品只保留第一作者用于分组和去重。
- 重建索引时用本次扫描结果替换 SQLite 旧记录，并同步清理 `catalog.md` 中已经没有本地 PDF 或图片目录的旧条目，确保设置页扫描数、本地书库“全部”和总目录数量一致。
- 从其他页面切回本地书库时，页面切换只做轻量 SQLite 查询；下载目录重建索引放到后台线程，完成后再刷新列表。
- 后续下载目录较大时，将同步扫描改为后台线程。

### 2. UI 视觉打磨

- 检查深色和浅色主题下的本地书库、禁漫下载、禁漫预览、设置页。
- 设置页提供跟随系统、浅色、深色主题切换；选择后立即预览并持久化，下次启动继续使用。
- 用 QFluentWidgets 控件替换剩余普通 Qt 控件中影响观感的部分。
- 为书库空状态、错误状态和扫描状态增加 Fluent 卡片提示。
- 避免硬编码单主题颜色。

### 3. 下载流程完善

- 下载任务执行不应长期阻塞 UI 线程；UI 至少显示任务级进度、当前 JM 号和每个任务状态。
- 开始下载后应清空输入框；所有任务结束后进度条归零，表格继续保留成功和失败记录。
- 下载生成 PDF 后应整理为 `下载根目录 / 第一作者 / JM号-作品名.pdf`，并把第一面图片复制到根目录 `Cover/`。
- 整理完成后不再保留作品图片目录，减少 Windows 长路径风险。
- 下载完成后应触发书库页刷新。
- 失败任务应保留可读错误摘要。
- 批量删除只能删除匹配当前 JM 号的作品目录和对应 PDF；如果旧索引把 `album_dir` 记录成作者目录，应跳过该目录，避免误删同作者其他作品。

### 4. 预览交互完善

- 禁漫预览页查询期间显示搜索中状态，并暂时禁用输入框和按钮。
- JM 号输入框按 Enter 应触发与“查看详情”按钮相同的查询逻辑。
- 禁漫预览页在文字详情上方显示完整等比例封面图，优先复用本地封面，缺失时缓存线上封面。

### 5. 书库修复页

- 左侧导航在“禁漫预览”和底部“设置”之间新增“书库修复”，使用 `FluentWindow.addSubInterface()` 和 QFluentWidgets 内置图标，保持与现有导航项一致。
- 页面主按钮使用放大后的 `PrimaryPushButton`，颜色跟随统一青色强调色。
- 扫描历史残留的 `作者 / JM{Aid}-{Atitle} / 第{Pindex}章 / 图片` 目录，缺失 PDF 时用本地图片补全 `作者 / JM号-作品名.pdf`。
- PDF 生成成功后复制封面到根目录 `Cover/` 并删除原图片目录；失败时保留原目录并显示日志。
- 修复结束后调用重建索引，同步 SQLite 与 `catalog.md`。

### 6. 禁漫官网页

- 左侧导航位于“书库修复”和底部“设置”之间，使用 `FluentIcon.GLOBE` 和 `addSubInterface()`。
- 使用 Fluent 滚动卡片按发布页、国际域名、东南亚路线、大陆分流、APP 下载和联系方式分组。
- 裸域名保持原始文本，通过 `QUrl.fromUserInput()` 解析后交给 `QDesktopServices.openUrl()`。
- 不引入 WebEngine，不在页面加载时主动探测网络。

### 7. 文档和编码清理

- 每次修改到乱码文件时，把该文件恢复为正常 UTF-8 中文。
- 优先清理 `README.md`、`assets/readme/README-en.md` 和测试文件中的 mojibake。
- 开发记录新增内容必须保持正常中文。

### 8. 发布与仓库清理

- 旧的 `download-jmcomic.bat` 和 `view-jmcomic.bat` 已由桌面端入口替代，不再保留。
- 保留 `start-jmcomic-shelf.bat` 作为源码仓库启动入口。
- `assets/icon.png` 是桌面端软件图标；`icons/icon.png` 和 `icons/icon.ico` 供 PyAppify 打包使用。
- PyAppify 入口保持为 `run-jmcomic-shelf.py`，不要改回 `jmcomic-shelf` console script，避免自动更新后继续使用旧安装包代码。
- 正式 release 使用 `vMAJOR.MINOR.PATCH`，例如 `v0.1.0`。
- 推送 `v*` tag 后由 GitHub Actions 调用 `ok-oldking/pyappify-action` 构建 Windows 包并上传到 GitHub Release。
- 暂不配置 CNB 镜像或同步 Action。

## 验证命令

桌面端改动后至少运行：

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v
$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\detail_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\styles.py
```

涉及 `CatalogPlugin` 时额外运行：

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v
$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic\jm_plugin.py
```

## 安全检查

提交前确认：

- `jmcomic-option.yml` 仍被 `.gitignore` 忽略。
- diff 中没有账号、密码、cookie、token、代理凭据。
- diff 中没有用户下载目录里的漫画、PDF、封面、`catalog.md`。
- 临时参考目录 `.tmp_launchdock_ref/` 不进入提交。
