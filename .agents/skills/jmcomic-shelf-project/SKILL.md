---
name: jmcomic-shelf-project
description: 仅用于 JMComic Shelf 项目的专属技能。用于修改下载路径、PDF 转换、Markdown 目录插件、封面嵌入、Windows 脚本、README、项目说明、桌面端 PySide6 + QFluentWidgets UI、书库索引和本地漫画工作流；当用户在本仓库中要求维护漫画下载与本地书库工作流时使用。
---

# JMComic Shelf 项目技能

## 使用原则

- 只服务当前 JMComic Shelf 仓库，不作为全局通用技能。
- 默认使用中文编写说明、开发记录、协作约定、界面文案和用户可见文档。
- 新增文件名和目录名优先使用简洁英文。
- 仓库内路径使用相对路径，不写死开发者本机绝对路径。
- 用户要求实现功能时，先读取根目录 `AGENTS.md`，再读取本 Skill、维护 Skill、相关 spec/plan 和最近开发记录。
- 如果发现 `AGENTS.md`、spec、plan、Skill 或开发记录中有乱码、过期规则或矛盾，先修正或记录判断，再改代码。
- 每次修改代码、脚本或文档后，同步更新 `development-log.md`。
- 如果本次交付包含新增功能、文件结构变化、工作流变化或用户可见行为变化，必须同步检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/` 是否需要更新；不能只写开发记录。
- 普通更新完成后，使用 `.agents/skills/jmcomic-shelf-maintenance/SKILL.md` 的流程提交并 push 到 GitHub。
- 始终避免提交 `jmcomic-option.yml`、账号密码、下载内容、PDF、`catalog.md` 或用户本地绝对路径配置。

## 项目目标

JMComic Shelf 基于 `hect0x7/JMComic-Crawler-Python`，面向个人本地收藏工作流：

- 通过配置下载漫画。
- 自动转换 PDF。
- 自动维护 Markdown 总目录。
- 提供适合 Windows 用户双击启动源码桌面端的脚本。
- 用 PySide6 + QFluentWidgets 桌面端降低手写命令和 YAML 配置成本。

## 当前核心模块

### 上游下载能力

保留上游项目的 API、CLI、下载器、图片解码和插件体系。修改时优先沿用上游结构，避免无关重构。

### `CatalogPlugin`

位置：`src/jmcomic/jm_plugin.py`

职责：

- 在 `after_album` 后维护 `catalog.md`。
- 按作者分组。
- 每个作者下独立编号。
- 同一作者下按 JM ID 去重更新。
- 保留来源标题和作者文本；标签统一转换为中文简体后写入，方便搜索和分类筛选。
- 记录标题、ID、链接、标签、章节。
- 从本次下载成功的第一章第一张图片生成 base64 封面。
- 使用 HTML `<img>` 控制封面宽度和顶部对齐。

修改目录插件时，同步检查：

- `tests/test_jmcomic/test_jm_plugin.py` 的 catalog 测试。
- README 中目录格式示例。
- `AGENTS.md` 中目录规则说明。
- `development-log.md`。

### 桌面端

桌面端包位于 `src/jmcomic_shelf/`。

核心职责：

- `settings.py`：桌面端本地设置。
- `database.py`：SQLite 书库索引。
- `index_service.py`：JM album 元数据和下载目录扫描到 SQLite 的同步逻辑。
- `download_service.py`：桌面端下载任务和下载后索引更新。
- `detail_service.py`：单个 JM 号详情查询。
- `cover_cache.py`：完整封面缩略图缓存，不裁剪。
- `ui/`：PySide6 + QFluentWidgets 页面。

书库页不能只读空 SQLite。必须在启动或 reload 时，从当前设置的下载目录递归扫描现有漫画目录和 PDF，再显示结果。
SQLite 标签应与 `catalog.md` 一致统一保存为中文简体；书库页的“分类”按钮应展开当前书库出现过的全部标签，标签面板最多展示五行并支持滚动；可同时选择多个标签，满足任一选中标签的漫画都会显示。

### Windows 脚本

- `start-jmcomic-shelf.bat`

桌面端已经替代下载和查看详情脚本。当前只保留源码仓库启动脚本。

脚本应：

- 使用脚本所在目录推导源码目录，并通过环境变量让桌面端找到项目根目录下的 `jmcomic-option.yml`。
- 给不熟悉命令行的用户清晰提示。
- 不写死账号密码。

## 桌面 UI 规则

桌面端技术栈是 PySide6 + QFluentWidgets。不要误以为这是原生 WinUI 3 项目，也不要改成普通 Qt Widgets 风格。

UI 必须保持：

- 工具型桌面应用气质。
- 深色 Fluent / Windows 11 Settings 观感。
- 左侧 `FluentWindow` 导航，图标 + 中文文字。
- 右侧主区域透明背景，使用 QFluentWidgets 原生控件和卡片。
- 青色强调色，当前建议 `#00c8d7`。
- 卡片式信息分组，避免网页式大白底和黑色说明条。
- 设置页类似 Windows 设置项：标题、说明、路径输入、按钮在同一 Fluent 卡片中。
- 书库页以封面卡片网格展示作品，按作者分组。
- 封面完整等比例显示，不裁剪、不截断。
- 中文文案必须正常 UTF-8，不能提交乱码。

参考项目：

- `https://github.com/Dylanliiiii/LaunchDock`

只参考其 QFluentWidgets 桌面应用组织方式、深色 Fluent 风格和项目协作说明，不照搬业务功能。

## 当前技术栈与限制

- 部分历史中文文档和测试文本存在 mojibake 乱码，修改到的文件必须逐步恢复为正常 UTF-8 中文。
- 书库索引必须支持从下载目录重建，否则已有漫画不会显示。
- 当前下载目录扫描是同步执行；后续如果目录很大，需要迁移到后台线程或增量索引。
- 当前桌面端不是原生 WinUI 3；需要用 QFluentWidgets 控件实现接近 Windows Fluent 的观感。
- 真实配置文件不能提交，测试只能使用临时目录和脱敏示例。

## 路径规则

当前推荐：

```yaml
rule: Bd / Aauthor / JM{Aid}-{Atitle} / 第{Pindex}章
```

原因：

- 保留作者和作品标题，便于浏览。
- 章节目录使用短名称，避免标题重复造成 Windows 长路径失败。
- 不强制繁简转换，减少和源站文本不一致导致的重复下载。

如果用户要求恢复章节标题目录，需要提醒 Windows 长路径风险。

## README 与文档

README 应保持：

- 顶部居中标题和徽章风格。
- 顶部展示 `assets/icon.png` 作为软件图标。
- 明确说明基于上游项目修改。
- 中文 README 为主入口。
- 英文 README 独立放在 `assets/readme/README-en.md`。
- 不把英文说明只追加在中文 README 末尾。
- 使用方式优先说明 GitHub Release 和桌面端入口；不要再把旧下载/预览脚本作为主要入口。

修改文档时，检查项目名、仓库链接、脚本名、配置文件名和目录示例是否一致。

如果文档、开发记录或设计说明引用用户提供的参考项目、教程、工具或外部资料，应保留完整 URL。

新增功能或调整桌面端用户可见行为时，README 应同步描述用户能看到和使用的能力；如果只是内部实现细节、测试修复或不影响使用方式的整理，可以在开发记录中说明无需更新 README 的判断。

## 验证清单

根据改动范围选择验证。

目录插件：

```powershell
python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v
python -m py_compile src\jmcomic\jm_plugin.py
```

桌面端索引 / UI：

```powershell
$env:PYTHONPATH='src;tests'; python -m unittest discover -s tests -p 'test_shelf_*.py' -v
$env:PYTHONPATH='src;tests'; python -m py_compile src\jmcomic_shelf\app.py src\jmcomic_shelf\index_service.py src\jmcomic_shelf\ui\main_window.py
```

README / AGENTS / Skill：

- 检查链接和相对路径。
- 检查是否误写本机绝对路径。
- 检查是否泄露 `jmcomic-option.yml` 内容。
- 检查参考项目是否保留完整 URL。

Windows 脚本：

- 检查 `start-jmcomic-shelf.bat` 仍使用 `%~dp0` 推导源码目录和配置路径。
- 检查没有写死维护者用户名或密码。

## 常见风险

- 长标题导致 Windows 路径过长。
- 多作者作品下载文件只在第一作者目录，但 catalog 和桌面索引可能需要在多个作者下展示。
- base64 封面会让 `catalog.md` 变大。
- 网络封面接口可能拿到裁切缩略图，目录封面应优先使用已下载的第一张图片。
- 真实配置文件不能提交。
- 只写 SQLite 不扫现有下载目录，会导致用户已有漫画在书库页不显示。
