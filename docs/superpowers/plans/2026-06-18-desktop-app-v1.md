# JMComic Shelf 桌面应用 v1 实施计划

## 当前基线

桌面端已位于 `src/jmcomic_shelf/`，使用 PySide6 + QFluentWidgets。

已有模块：

- `settings.py`：保存下载目录、`jmcomic-option.yml`、应用数据目录和外观主题模式，主题支持跟随系统、浅色和深色。
- `database.py`：SQLite 书库索引。
- `cover_cache.py`：完整等比例封面缩略图。
- `index_service.py`：JM album 到 SQLite 的映射，以及从下载目录重建索引。
- `download_service.py`：解析多个 JM 号、执行下载、下载后写入索引。
- `ui/theme.py`：集中处理 QFluentWidgets 主题映射和强调色。
- `detail_service.py`：查询单个 JM 号详情。
- `file_actions.py`：打开 PDF 和在资源管理器中定位。
- `ui/`：本地书库、禁漫下载、禁漫预览、设置页面。

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
- 扩展扫描规则以兼容更多 PDF 位置和章节目录形态。
- 为无 PDF 但有图片目录的作品显示卡片，并禁用打开 PDF。
- 书库记录保存本地漫画目录路径，供批量删除本地文件时使用。
- 书库页提供批量管理模式，支持选择、多选、全选、反选、取消全选和删除选中；删除前必须二次确认。
- 本地书库页的 `全部` 筛选器保留总数、青色下划线和轻量背景框；侧边栏展开/收起触发布局变化时，应延迟重排封面网格，降低反复切换时的卡顿。
- 从其他页面切回本地书库时，页面切换只做轻量 SQLite 查询；下载目录重建索引放到后台线程，完成后再刷新列表。
- 后续下载目录较大时，将同步扫描改为后台线程。

### 2. UI 视觉打磨

- 检查深色和浅色主题下的本地书库、禁漫下载、禁漫预览、设置页。
- 设置页提供跟随系统、浅色、深色主题切换；选择后立即预览，保存后持久化。
- 用 QFluentWidgets 控件替换剩余普通 Qt 控件中影响观感的部分。
- 为书库空状态、错误状态和扫描状态增加 Fluent 卡片提示。
- 避免硬编码单主题颜色。

### 3. 下载流程完善

- 下载任务执行不应长期阻塞 UI 线程；UI 至少显示任务级进度、当前 JM 号和每个任务状态。
- 开始下载后应清空输入框；所有任务结束后进度条归零，表格继续保留成功和失败记录。
- 下载完成后应触发书库页刷新。
- 失败任务应保留可读错误摘要。

### 4. 文档和编码清理

- 每次修改到乱码文件时，把该文件恢复为正常 UTF-8 中文。
- 优先清理 `README.md`、`assets/readme/README-en.md` 和测试文件中的 mojibake。
- 开发记录新增内容必须保持正常中文。

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
