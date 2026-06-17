<!-- 顶部标题 & 统计徽章 -->
<div align="center">
  <h1 style="margin-top: 0" align="center">JMComic Shelf</h1>

  <p align="center">
    <strong>简体中文</strong> ·
    <a href="#english">English</a>
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

### 3. 双击脚本下载

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

### 4. 命令行下载

也可以直接使用命令行：

```shell
jmcomic 211899 --option="D:/Others/JMComic-Crawler-Python/jmcomic-option.yml"
```

批量下载：

```shell
jmcomic 211899 123456 654321 --option="D:/Others/JMComic-Crawler-Python/jmcomic-option.yml"
```

## 目录文件

下载后会自动维护：

```text
D:/Others/JMComic/catalog.md
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
- 增加下载失败重试、失败记录和重新补图入口。

## 上游项目

本项目基于以下开源项目修改：

- [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)

感谢原作者提供稳定的核心 API、下载器和插件框架。本仓库主要用于个人本地书库工作流扩展，不替代上游项目。

## English

JMComic Shelf is a personal comic download and local library management tool based on [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python).

This fork keeps the upstream downloader, parser and plugin architecture, while adding a local-library workflow:

- automatic PDF generation,
- an author-grouped Markdown catalog,
- embedded cover images in `catalog.md`,
- Windows-friendly helper scripts,
- shorter chapter directory names to avoid long-path issues,
- and a future path toward a small desktop app.

Sensitive local configuration such as account credentials should stay in `jmcomic-option.yml`, which is intentionally ignored by Git.
