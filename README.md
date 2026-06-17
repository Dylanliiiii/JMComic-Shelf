<!-- 顶部标题 & 统计徽章 -->
<div align="center">
  <h1 style="margin-top: 0" align="center">JMComic Shelf</h1>

  <p align="center">
    <strong>简体中文</strong> ·
    <a href="./assets/readme/README-en.md">English</a>
  </p>

  <p align="center">
    <strong>基于 JMComic-Crawler-Python 的个人漫画下载、PDF 转换与本地书库管理工具</strong>
  </p>

[![GitHub](https://img.shields.io/badge/GitHub-Dylanliiiii%2FJMComic--Shelf-181717?logo=github)](https://github.com/Dylanliiiii/JMComic-Shelf)
[![Upstream](https://img.shields.io/badge/Based%20on-hect0x7%2FJMComic--Crawler--Python-blue)](https://github.com/hect0x7/JMComic-Crawler-Python)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/hect0x7/JMComic-Crawler-Python?color=red)](https://github.com/hect0x7/JMComic-Crawler-Python)

</div>

> JMComic Shelf 是一个个人向的漫画下载与整理工具。
>
> 本项目基于 [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) 开源项目进行二次整理和功能扩展，保留其核心下载、解析、插件机制，并加入更偏向“本地书库管理”的自动化流程。
>
> 后续计划逐步封装为桌面应用，把当前命令行和脚本流程包装成更易用的图形界面。

![introduction.jpg](./assets/docs/sources/images/introduction.jpg)

## 项目定位

原项目 `JMComic-Crawler-Python` 提供了完整的 JMComic Python API、命令行下载能力、图片解码、插件扩展和 PDF/ZIP/长图导出能力。

本仓库在此基础上，主要面向个人本地收藏工作流做了整理：

- 通过本地配置文件统一下载目录、登录、图片格式、并发和插件行为。
- 下载完成后自动生成 PDF。
- 自动维护一个 Markdown 总目录 `catalog.md`。
- 总目录按作者分组，同一作品如果有多个作者，会在每个作者下面各登记一份索引。
- 每条目录记录包含封面、标题、JM ID、链接、标签和章节。
- 封面会以内嵌 base64 的方式写入 Markdown，方便把单个目录文件放到网盘、笔记软件或收藏网站中查看。
- 针对 Windows 路径过长问题，章节目录默认使用短名称，例如 `第1章`。
- 提供 Windows 双击脚本，减少手动输入 PowerShell 命令的成本。

## 当前改动

相比上游项目，本仓库当前主要修改集中在：

- 新增 `catalog` 插件：下载完成后生成和更新本地 Markdown 书库目录。
- `catalog.md` 使用作者分组，并支持作品去重更新。
- 目录记录保留原站点返回的标题、作者和标签文本，不强制繁简转换。
- 目录记录支持内嵌封面图，默认使用本次下载成功的第一章第一张图片作为封面。
- 目录封面默认宽度为 `120`，可通过配置调整。
- 下载路径规则调整为 `作者 / JM号-作品名 / 第N章`，避免长标题重复导致 Windows 路径过长。
- 增加 Windows 批处理脚本：
  - `download-jmcomic.bat`：输入 JM 号后下载。
  - `view-jmcomic.bat`：输入 JM 号后查看详情。
- 将本地敏感配置文件 `jmcomic-option.yml` 加入 `.gitignore`。

## 使用方式

### 1. 安装依赖

建议使用 Python 3.12 或以上版本。

```shell
pip install -e .
pip install img2pdf
```

如果只想使用上游包，也可以参考原项目文档：

```shell
pip install jmcomic -U
```

### 2. 准备本地配置

在项目根目录创建 `jmcomic-option.yml`。

这个文件用于保存下载目录、账号登录、并发、PDF、目录插件等本地配置。它可能包含账号密码，因此不会提交到仓库。

当前个人工作流使用的下载目录结构大致为：

```text
下载目录 / 作者 / JM号-作品名 / 第N章
```

PDF 和 `catalog.md` 会生成在下载目录中。

### 3. 桌面应用预览

当前仓库已开始加入 PySide6 + QFluentWidgets 桌面端入口。直接使用源码仓库时，可以双击：

```text
start-jmcomic-shelf.bat
```

安装项目后也可以运行：

```shell
jmcomic-shelf
```

桌面端第一版包含左侧图标文字导航：

- `本地书库`：读取桌面端 SQLite 索引，支持 `全部`、JM 号、作者和标签搜索；`全部` 会显示当前结果总数，并用轻量背景框与下划线区分当前筛选；封面卡片按作者分组，并根据窗口宽度自动调整每行数量；展开或收起左侧导航时会延迟重排封面网格，避免反复切换时明显卡顿；从其他页面切回本地书库时会先显示已有索引，再在后台扫描下载目录并刷新新内容，避免切页被目录扫描阻塞；批量管理模式支持多选、全选、反选、取消全选和删除所选本地漫画。
- `禁漫下载`：输入一个或多个 JM 号，任务会立即进入列表，并在开始后清空输入框；下载时显示总进度、当前任务状态，所有任务结束后进度条归零并保留表格里的成功或失败记录；失败任务保留重试入口。
- `禁漫预览`：输入单个 JM 号查看详情；标题单独成行，查询输入和按钮位于标题下方；如果本地索引已有 PDF，可直接打开或在文件资源管理器中定位。
- `设置`：维护下载目录、`jmcomic-option.yml` 路径、应用数据目录、浅色/深色/跟随系统主题和封面缓存清理。

桌面端数据默认保存在 Windows 用户数据目录：

```text
%APPDATA%/JMComic Shelf/
```

其中 `settings.json` 保存桌面端设置，`shelf.db` 是桌面书库索引，`covers/` 只保存桌面端缩略图。下载得到的图片、PDF 和人工可读的 `catalog.md` 仍然保留在你设置的下载目录中。

桌面端 UI 风格参考：

- [ok-oldking/ok-script](https://github.com/ok-oldking/ok-script)

后续打包与自动更新方向参考：

- [ok-oldking/pyappify](https://github.com/ok-oldking/pyappify)

### 4. 双击脚本下载

Windows 下可以直接双击：

```text
download-jmcomic.bat
```

然后输入一个或多个 JM 号，例如：

```text
211899 123456
```

查看作品详情可以双击：

```text
view-jmcomic.bat
```

### 5. 命令行下载

也可以直接使用命令行：

```shell
jmcomic 211899 --option="./jmcomic-option.yml"
```

批量下载：

```shell
jmcomic 211899 123456 654321 --option="./jmcomic-option.yml"
```

## 目录文件

下载后会自动维护：

```text
D:/path/to/JMComic/catalog.md
```

目录格式示例：

```md
# 作者名

1. <img src="data:image/jpeg;base64,..." alt="JM211899" width="120" style="vertical-align: top;">

   - 📖 标题：作品标题
   - 🆔 ID：JM211899
   - 🔗 链接：https://18comic.vip/album/211899/
   - 🏷️ 标签：标签1, 标签2
   - 📑 章节：第1话 作品标题 (id: 211899)
```

封面图片直接嵌在 Markdown 文件里，因此单独上传 `catalog.md` 到其他地方时，图片也能跟着显示。

## 后续计划

- 将当前脚本流程封装为桌面应用。
- 增加图形界面的下载任务管理。
- 增加本地书库浏览、筛选、搜索和标签管理。
- 增加配置向导，避免手写 YAML。
- 增加更细粒度的下载进度、失败记录和重新补图入口。

## 上游项目

本项目基于以下开源项目修改：

- [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)

感谢原作者提供稳定的核心 API、下载器和插件框架。本仓库主要用于个人本地书库工作流扩展，不替代上游项目。
