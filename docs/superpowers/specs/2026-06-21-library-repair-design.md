# 书库修复功能页设计

## 背景

桌面端已经有设置页“重建索引”能力：它会从当前下载目录扫描本地漫画，用扫描结果替换 SQLite 书目集合，并裁剪 `catalog.md` 中已经没有本地文件的旧条目。这能解决用户手动删除漫画后，数据库、书库数量和总目录长期不一致的问题。

仍需要新增“书库修复”入口的原因是：历史下载或异常中断可能留下 `作者/JM号-标题/章节图片` 目录，但没有生成最终 PDF。此时书库页可能能显示封面，但点击封面或定位文件没有可用 PDF。设置页重建索引只负责同步现状，不负责把图片补成 PDF。

## 目标

- 在左侧导航新增“书库修复”功能页，位置在“禁漫预览”和底部“设置”之间。
- 新导航项必须复用 `FluentWindow.addSubInterface()` 和 QFluentWidgets 内置图标，样式、选中态、间距与现有“本地书库 / 禁漫下载 / 禁漫预览”一致。
- 页面使用工具型 Fluent 卡片风格，复用 `TitleLabel`、`CaptionLabel`、`CardWidget`、`PrimaryPushButton` 等现有控件。
- 主按钮文案为“开始修复”，按钮使用 `PrimaryPushButton`，颜色跟随项目统一强调色 `#00c8d7`，只适度放大尺寸，不自定义另一套按钮样式。
- 点击“开始修复”后，自动补全所有有图片目录但缺失 PDF 的本地漫画。
- PDF 生成成功后，自动复制封面到下载根目录 `Cover/`，并删除原作品图片目录，最终只保留 `作者/JM号-标题.pdf`。
- PDF 生成失败时保留原图片目录，不删除可恢复数据。
- 修复结束后调用既有 `rebuild_index_from_download_dir()`，同步 SQLite 和 `catalog.md` 数量与条目。

## 非目标

- 不新增多下载目录管理。
- 不重写上游下载器。
- 不把修复功能合并进设置页“重建索引”按钮；设置页继续保持轻量路径和索引维护入口。
- 不在修复前强制要求用户逐项确认。用户已经确认默认行为为“PDF 生成成功后自动删除原图片目录”。
- 不删除无法成功生成 PDF 的图片目录。

## 功能流程

1. 用户进入“书库修复”页。
2. 页面提示当前功能适用于：封面能显示但点击无响应、作者目录下残留 JM 作品图片文件夹、手动删除漫画后数量不一致等情况。
3. 用户点击“开始修复”。
4. 修复服务扫描当前设置的下载目录，跳过 `Cover/`、`covers/`、`.git`、`__pycache__` 等非作品目录。
5. 对每个 `JM{Aid}-{Atitle}` 作品目录：
   - 若同作者目录或作品目录内已经存在对应 `JM{Aid}-{Atitle}.pdf`，不重复生成 PDF。
   - 若不存在 PDF 且目录内有图片，按自然排序收集图片并用 `img2pdf` 生成临时 PDF。
   - PDF 非空并成功替换后，把 PDF 移动或保存到 `作者/JM号-标题.pdf`。
   - 从第一张图片复制封面到 `下载根目录/Cover/JM号-标题.<ext>`。
   - 成功后删除原 `作者/JM号-标题/` 图片目录。
6. 修复服务完成后调用 `rebuild_index_from_download_dir()`。
7. 页面显示摘要：发现残留目录数、补全 PDF 数、清理目录数、失败数、同步后书库数量。
8. 页面显示最近处理日志。失败项写明错误摘要，并说明原图片目录已保留。

## 数据和服务边界

新增独立服务模块用于修复流程，避免把 UI 和文件系统逻辑混在一起。

建议接口：

```python
repair_library(download_dir: str, db_path: str, cover_cache_dir: str = '') -> LibraryRepairResult
```

返回结果包含：

- `found_dirs`：发现的残留作品目录数量。
- `repaired_pdfs`：成功补全 PDF 的数量。
- `removed_dirs`：成功清理的作品图片目录数量。
- `failed`：失败数量。
- `synced_count`：调用重建索引后的本地漫画数量。
- `entries`：每本作品的处理状态和简短说明，用于 UI 日志。

服务可复用 `download_service.py` 中的图片扩展名、自然排序、路径安全和封面复制思路，但不依赖线上 album 对象。扫描目录名和作者目录即可推导 JM ID、标题和第一作者。

## UI 结构

页面文件建议为 `src/jmcomic_shelf/ui/repair_page.py`。

页面结构：

- 标题：`书库修复`。
- 说明文案：说明扫描当前下载目录、补全缺失 PDF、成功后清理图片目录、最后同步 SQLite 和 `catalog.md`。
- 主卡片：`一键修复书库`，包含说明和更大的 `PrimaryPushButton('开始修复')`。
- 摘要卡片：显示发现残留目录、补全 PDF、清理目录、失败数量、同步后数量。
- 日志区域：显示最近处理结果。无结果时显示“尚未运行修复”。

修复执行可能较慢，应放在 `QThread` worker 中运行，避免阻塞 UI。运行中禁用按钮并显示“正在修复...”。完成后恢复按钮。

## 错误处理

- 未设置下载目录：页面提示先到设置页选择下载目录。
- 下载目录不存在：页面提示路径不可用。
- 缺少 `img2pdf`：提示重新安装或更新 JMComic Shelf。
- 单本作品修复失败：记录失败，不删除原目录，继续处理下一本。
- 最终重建索引失败：显示错误，保留已成功生成的 PDF 和已清理目录；用户可稍后重试。

## 测试要求

- 服务测试：
  - 无 PDF 但有图片目录时，生成 `作者/JM号-标题.pdf`，复制封面，删除原图片目录，并重建索引。
  - 已有 PDF 时，不重复生成 PDF，不误删无关目录。
  - PDF 生成失败时保留原图片目录并记录失败。
- UI 测试：
  - 主窗口新增“书库修复”页面并放在底部设置之前。
  - 页面主按钮为 `PrimaryPushButton`，尺寸大于普通按钮。
  - 修复完成后页面显示摘要结果。

验证命令沿用桌面端范围：

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v
$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\download_service.py src\jmcomic_shelf\repair_service.py src\jmcomic_shelf\ui\main_window.py src\jmcomic_shelf\ui\library_page.py src\jmcomic_shelf\ui\download_page.py src\jmcomic_shelf\ui\detail_page.py src\jmcomic_shelf\ui\settings_page.py src\jmcomic_shelf\ui\repair_page.py
```

## 文档同步判断

本次新增用户可见入口和修复工作流，需要同步更新：

- `README.md`：说明桌面端包含书库修复入口。
- `AGENTS.md`：把书库修复纳入桌面端工作流约定和质量要求。
- `.agents/skills/jmcomic-shelf-project/SKILL.md`：记录新增修复页和服务边界。
- `docs/superpowers/plans/2026-06-18-desktop-app-v1.md`：补充后续任务已包含书库修复页。
- `development-log.md`：记录设计、实现、验证和是否发布。
