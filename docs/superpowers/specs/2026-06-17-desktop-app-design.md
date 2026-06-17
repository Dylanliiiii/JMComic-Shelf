# JMComic Shelf 桌面应用设计

## 目标

把当前依赖 `download-jmcomic.bat` 和 `view-jmcomic.bat` 的脚本式工作流，整理为一个 Windows 桌面应用。第一版不重写上游下载能力，而是把现有下载、查看详情、PDF 转换、Markdown 总目录和本地书库浏览整合到一个可持续扩展的 UI 中。

桌面应用只管理当前设置里的一个下载目录。下载得到的漫画图片、PDF 和 `catalog.md` 仍保存在用户选择的下载目录；桌面端自己的 `settings.json`、`shelf.db` 和封面缩略图缓存在应用数据目录。

## 技术方向

- GUI：PySide6 + QFluentWidgets。
- 风格：深色 Fluent / Windows 11 Settings 风格。
- 强调色：青色，当前建议 `#00c8d7`。
- 下载能力：继续复用当前 `jmcomic` Python API、CLI、下载器和插件体系。
- 参考项目：`https://github.com/Dylanliiiii/LaunchDock`，只参考其 QFluentWidgets 桌面应用组织方式、深色 Fluent 风格和项目协作说明。

## UI 原则

- 使用 `FluentWindow` 左侧导航，导航项包含图标和文字。
- 页面主区域背景保持透明或跟随 QFluentWidgets 主题。
- 不给全局 `QWidget` 强行设置白底或黑底。
- 不出现突兀的大块黑色矩形、白色画布、黑底白字说明条或网页后台式布局。
- 优先使用 QFluentWidgets 控件：`TitleLabel`、`SubtitleLabel`、`CaptionLabel`、`CardWidget`、`SmoothScrollArea`、`PrimaryPushButton`、`PushButton`。
- 设置页和列表页采用卡片式分组，整体紧凑、稳定、适合高频使用。
- 封面必须完整等比例显示，不裁剪、不截断。

## 页面结构

### 书库

书库页用于浏览当前下载目录中的本地漫画。

核心能力：

- 顶部搜索框支持输入 JM 号、作者名或标签。
- 默认筛选器为“全部”。
- 从 SQLite 读取索引前，先递归扫描当前设置的下载目录，把现有漫画目录和 PDF 同步到 SQLite。
- 按作者分组展示作品。
- 作品以封面卡片展示，封面在上，底部显示 `JM号 + 标题` 的省略文本。
- 点击封面打开 PDF。
- 右键封面提供“打开 PDF”和“在文件资源管理器中显示位置”。

“全部”是桌面端内置筛选器，不写入真实标签。

### 下载

下载页替代 `download-jmcomic.bat`。

核心能力：

- 输入一个或多个 JM 号，支持空格、换行、英文逗号和中文逗号分隔。
- 使用当前设置中的 `jmcomic-option.yml` 和下载根目录。
- 下载完成后继续沿用当前目录结构。
- 下载完成后继续生成 PDF。
- 下载完成后继续更新下载根目录下的 `catalog.md`。
- 下载完成后同步更新 SQLite 书库索引。
- 失败任务保留错误摘要，并提供重试入口。

### 查看详情

查看详情页替代 `view-jmcomic.bat`。

核心能力：

- 输入单个 JM 号。
- 复用当前 `jmcomic` 查看详情能力。
- 展示标题、作者、标签、章节、链接等信息。
- 查询前同步扫描下载目录，以便识别本地 PDF。
- 如果作品已下载，提供打开 PDF 和定位文件入口。

### 设置

设置页管理桌面端运行所需的本地路径。

第一版设置：

- 当前下载目录。
- `jmcomic-option.yml` 路径。
- 应用数据目录，只读显示。
- 清理封面缓存按钮。
- 重建索引按钮。

保存设置时，如果选择了配置文件和下载目录，应同步更新 `jmcomic-option.yml` 中的 `dir_rule.base_dir`。

## 数据存储

桌面端主数据源使用 SQLite，不使用 `catalog.md` 作为唯一结构化索引。

默认位置：

```text
%APPDATA%/JMComic Shelf/
  settings.json
  shelf.db
  covers/
```

下载目录仍保存用户内容：

```text
下载目录/
  作者/
    JM号-作品名/
      第1章/
        图片
  JM号-作品名.pdf
  catalog.md
```

## 索引重建

第一版必须支持从下载目录重建索引。

扫描规则：

- 识别 `作者 / JM{Aid}-{Atitle} / 第{Pindex}章 / 图片`。
- 识别下载根目录或子目录中的 `JM{Aid}-{Atitle}.pdf`。
- 合并相同 JM ID 的目录信息和 PDF 路径。
- 生成桌面端封面缩略图，缩略图完整等比例，不裁剪。

## 错误处理

- 下载目录不存在：设置页提示重新选择。
- `jmcomic-option.yml` 不存在：下载页禁用或显示中文错误。
- PDF 文件不存在：封面卡片仍可显示，但打开 PDF 动作禁用或提示缺失。
- 数据库不可读：书库页显示错误卡片，不让应用启动失败。
- 封面缓存缺失：使用占位封面，并可重建缓存。

## 技术债

- 当前桌面端是 PySide6 + QFluentWidgets，不是原生 WinUI 3；后续 UI 修改必须遵守 QFluentWidgets 的主题和控件体系。
- 仓库内部分历史中文文档和测试文本曾出现 mojibake 乱码；修改到的文件必须恢复正常 UTF-8 中文。
- 当前目录扫描是同步执行；下载目录变大后应改为后台线程或增量索引。
- 书库页不能再只依赖下载完成后的 SQLite 写入；必须保留从现有下载目录重建的能力。

## 非目标

第一版不做：

- 多下载目录聚合。
- 在线账号管理复杂向导。
- 完整自动更新系统。
- 正式 release/tag。
- 重写上游下载器。
- 删除 `catalog.md`。
