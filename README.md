<div align="center">
  <img src="./assets/icon.png" alt="JMComic Shelf" width="120" height="120">

  <h1 style="margin-top: 12px" align="center">JMComic Shelf</h1>

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
[![Packaging](https://img.shields.io/badge/Packaging-PyAppify-00aeba)](https://github.com/ok-oldking/pyappify)
[![License](https://img.shields.io/github/license/hect0x7/JMComic-Crawler-Python?color=red)](https://github.com/hect0x7/JMComic-Crawler-Python)

</div>

> JMComic Shelf 是一个个人向的漫画下载与本地书库管理工具。
>
> 本项目基于 [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python) 二次整理和扩展，保留其核心下载、解析、API 和插件体系，并加入更偏向本地收藏管理的桌面端工作流。
>
> 桌面 UI 和项目协作风格参考 [Dylanliiiii/LaunchDock](https://github.com/Dylanliiiii/LaunchDock) 的 PySide6 + QFluentWidgets 工具应用组织方式；打包和自动更新方向使用 [ok-oldking/pyappify](https://github.com/ok-oldking/pyappify)。

![introduction.jpg](./assets/docs/sources/images/introduction.jpg)

## 项目定位

上游 `JMComic-Crawler-Python` 提供完整的 JMComic Python API、命令行下载能力、图片解码、插件扩展和 PDF/ZIP/长图导出能力。

JMComic Shelf 在此基础上面向个人本地收藏工作流做了整理：

- 通过桌面端维护下载目录、`jmcomic-option.yml` 和应用数据目录。
- 下载完成后自动生成 PDF。
- PDF 会整理到 `下载根目录 / 第一作者 / JM号-作品名.pdf`，作者目录下不再保留作品图片文件夹。
- 下载根目录下的 `Cover/` 会缓存每本作品第一面图片，供书库封面读取。
- 下载完成后自动维护下载根目录下的 `catalog.md`。
- `catalog.md` 按第一作者分组，并记录封面、标题、JM ID、链接、标签和章节。
- 封面以内嵌 base64 写入 Markdown，方便单独上传目录文件。
- 下载路径使用较短章节目录，尽量避开 Windows 长路径问题。
- 桌面端使用 SQLite 保存结构化书库索引，并可从现有下载目录重建。
- 本地书库支持搜索、作者分组、分类标签筛选、批量管理和删除本地作品。
- 书库修复可补全历史残留图片目录缺失的 PDF，成功后清理图片目录，并同步 SQLite 与 `catalog.md`。
- “禁漫官网”集中展示发布页、分流域名、APP 下载和联系方式，点击后使用系统默认浏览器打开。

## 安装与启动

### 方式一：下载 Release 版

正式版本会发布到 GitHub Releases：

- [JMComic Shelf Releases](https://github.com/Dylanliiiii/JMComic-Shelf/releases)

Release 版使用 PyAppify 打包。PyAppify launcher 会从 GitHub 仓库和版本标签安装应用代码、准备隔离 Python 环境，并在后续启动时基于 Git/tag 更新应用。当前 PyAppify 入口是仓库内的 `run-jmcomic-shelf.py`，该脚本会优先从已更新的 `working/src` 运行桌面端源码，避免自动更新后继续加载旧的 `site-packages` 入口。

当前打包配置位于：

- `pyappify.yml`
- `.github/workflows/release.yml`
- `icons/icon.png`
- `icons/icon.ico`

### 方式二：从源码启动

源码仓库阶段可双击：

```text
start-jmcomic-shelf.bat
```

也可以手动安装后运行：

```shell
pip install -e .
jmcomic-shelf
```

首次使用时，在“设置”页选择：

- 下载目录：PDF、`Cover/` 封面缓存和 `catalog.md` 会保存到这里。
- 配置文件：项目根目录中的 `jmcomic-option.yml`。
- 外观主题：跟随系统、浅色或深色；选择后会立即预览并保存。

## 桌面端功能

### 本地书库

- 启动或切回书库页时，可从当前下载目录重建 SQLite 索引。
- 搜索框支持 JM 号、作者名和标签，并带输入防抖。
- “全部”显示当前结果总数。
- “分类”展开当前书库出现过的全部标签，最多展示五行并支持滚动。
- 可同时选择多个标签，满足任一选中标签的作品都会显示。
- 封面完整等比例显示，不裁剪、不截断。
- 点击封面打开 PDF，右键可在文件资源管理器中定位。
- 批量管理支持全选、反选、取消全选和删除选中作品。

### 禁漫下载

- 输入一个或多个 JM 号，支持空格、逗号和换行分隔。
- 下载任务会进入表格，显示等待、下载中、已完成或失败。
- 下载完成后沿用当前插件流程生成 PDF，随后整理为作者目录下仅保留 PDF、根目录 `Cover/` 缓存封面，并更新 `catalog.md` 和 SQLite 索引。
- 失败任务保留错误摘要并提供重试入口。

### 禁漫预览

- 输入单个 JM 号查看详情。
- 点击“查看详情”或在输入框按 Enter 都会查询；查询期间会显示搜索中状态。
- 详情文字上方会显示封面图；本地已有封面时优先使用本地缓存，否则会缓存线上封面。
- 展示标题、作者、标签、章节和链接。
- 如果本地索引已有 PDF，可直接打开或定位文件。

### 书库修复

- 一键扫描当前下载目录中历史残留的作品图片目录。
- 对缺失 PDF 的作品补全 `作者 / JM号-作品名.pdf`。
- PDF 生成成功后复制封面到根目录 `Cover/`，并删除原图片目录。
- 修复结束后会重建索引，同步 SQLite 与 `catalog.md` 的数量和条目。

### 禁漫官网

- 按发布页、国际域名、东南亚路线、大陆分流、APP 下载和联系方式分组展示官方入口。
- 点击地址后交给系统默认浏览器打开，不在应用内嵌网页。
- 用户提供的裸域名保持原样，由 Qt 在点击时按网址输入解析。

### 设置

- 维护下载目录和 `jmcomic-option.yml` 路径。
- 显示应用数据目录：默认在 `%APPDATA%/JMComic Shelf/`。
- 支持清理封面缓存和重建索引。
- 支持浅色、深色和跟随系统主题，并会持久化到下次启动。

## 数据位置

桌面端应用数据默认保存：

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
    JM号-作品名.pdf
  Cover/
    JM号-作品名.jpg
  catalog.md
```

`jmcomic-option.yml` 可能包含账号、cookie、代理等本地敏感配置，已被 `.gitignore` 忽略，不应提交到仓库。

## 目录文件

下载后会自动维护：

```text
D:/path/to/JMComic/catalog.md
```

目录示例：

```md
# 作者名

1. <img src="data:image/jpeg;base64,..." alt="JM211899" width="120" style="vertical-align: top;">

   - 📖 标题：作品标题
   - 🆔 ID：JM211899
   - 🔗 链接：https://18comic.vip/album/211899/
   - 🏷️ 标签：标签1, 标签2
   - 📑 章节：第1话 作品标题 (id: 211899)
```

只对标签做繁简统一；标题、作者、章节标题和封面内容保持来源文本。

## 打包与发布

本项目的桌面应用发布使用 PyAppify：

- `pyappify.yml` 定义应用名、Git 仓库、入口脚本和 Python 版本；`main_script` 应保持为 `run-jmcomic-shelf.py`，不要改回 pip 安装生成的 `jmcomic-shelf` console script。
- `run-jmcomic-shelf.py` 是 PyAppify 运行入口，负责把当前工作目录的 `src` 放到 `sys.path` 最前，再启动 `jmcomic_shelf.app.main()`。
- `icons/` 预留 PyAppify 打包图标，当前由 `assets/icon.png` 生成。
- `.github/workflows/release.yml` 在推送 `v*` tag 时构建 Windows 包并上传到 GitHub Release。

版本号采用 `vMAJOR.MINOR.PATCH`，例如 `v0.1.0`。当前暂不配置 CNB 镜像或对应同步 Action。

## 参考项目

- 上游下载能力：[hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
- 桌面 UI 与项目风格参考：[Dylanliiiii/LaunchDock](https://github.com/Dylanliiiii/LaunchDock)
- 打包与自动更新：[ok-oldking/pyappify](https://github.com/ok-oldking/pyappify)
- PyAppify GitHub Action：[ok-oldking/pyappify-action](https://github.com/ok-oldking/pyappify-action)

感谢上游作者提供稳定的核心 API、下载器和插件框架。JMComic Shelf 主要用于个人本地书库工作流扩展，不替代上游项目。
