<!-- Header & badges -->
<div align="center">
  <h1 style="margin-top: 0" align="center">JMComic Shelf</h1>

  <p align="center">
    <a href="../../README.md">简体中文</a> ·
    <strong>English</strong>
  </p>

  <p align="center">
    <strong>A personal comic download, PDF export, and local library management workflow based on JMComic-Crawler-Python</strong>
  </p>

[![GitHub](https://img.shields.io/badge/GitHub-Dylanliiiii%2FJMComic--Shelf-181717?logo=github)](https://github.com/Dylanliiiii/JMComic-Shelf)
[![Upstream](https://img.shields.io/badge/Based%20on-hect0x7%2FJMComic--Crawler--Python-blue)](https://github.com/hect0x7/JMComic-Crawler-Python)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/hect0x7/JMComic-Crawler-Python?color=red)](https://github.com/hect0x7/JMComic-Crawler-Python)

</div>

> JMComic Shelf is a personal comic download and local library management tool.
>
> This project is based on [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python). It keeps the upstream downloader, parser, API, and plugin architecture, while adding a workflow focused on local collection management.
>
> The long-term plan is to wrap the current command-line and script workflow into a small desktop application.

![introduction.jpg](../docs/sources/images/introduction.jpg)

## Project Purpose

The upstream `JMComic-Crawler-Python` project provides a stable Python API, command-line downloader, image decoding, plugin system, and export features such as PDF, ZIP, and long images.

This repository builds on top of that foundation and focuses on a personal local-library workflow:

- unified local configuration for download paths, login, image format, concurrency, and plugins;
- automatic PDF generation after downloads;
- automatic maintenance of a Markdown catalog named `catalog.md`;
- author-grouped catalog entries;
- duplicate-safe updates for already downloaded albums;
- support for multi-author albums, where the same album is indexed under each author;
- catalog entries containing cover image, title, JM ID, link, tags, and chapters;
- embedded base64 cover images, so `catalog.md` can be uploaded by itself to cloud drives, note apps, or personal collection websites;
- shorter chapter folder names such as `Chapter 1` / `第1章` style paths to avoid Windows long-path issues;
- Windows helper scripts for users who do not want to run PowerShell commands manually.

## Current Changes

Compared with the upstream project, this repository currently adds or changes:

- a new `catalog` plugin that updates a local Markdown library catalog after album downloads;
- author-grouped catalog sections;
- duplicate-safe catalog updates by JM ID;
- preservation of the original title, author, and tag text returned by the source site, without forced Simplified/Traditional Chinese conversion;
- embedded cover images generated from the first successfully downloaded image of the album;
- configurable catalog cover width, currently defaulting to `120`;
- a shorter download path rule to avoid repeated long titles in Windows paths;
- Windows batch scripts:
  - `download-jmcomic.bat` for downloading one or more album IDs;
  - `view-jmcomic.bat` for viewing album details;
- `.gitignore` protection for `jmcomic-option.yml`, which may contain local credentials.

## Usage

### 1. Install Dependencies

Python 3.12 or newer is recommended.

```shell
pip install -e .
pip install img2pdf
```

If you only want to use the upstream package, see the upstream documentation or install it directly:

```shell
pip install jmcomic -U
```

### 2. Prepare Local Configuration

Create a local `jmcomic-option.yml` file in the project root.

This file stores local settings such as download directory, login credentials, concurrency, PDF export, and catalog plugin configuration. It may contain account credentials, so it is intentionally ignored by Git.

The current personal workflow uses a path structure like:

```text
download directory / author / JM ID-title / chapter number
```

PDF files and `catalog.md` are generated in the download directory.

### 3. Download with the Windows Script

On Windows, double-click:

```text
download-jmcomic.bat
```

Then enter one or more JM album IDs, for example:

```text
211899 123456
```

To view album details without downloading, double-click:

```text
view-jmcomic.bat
```

### 4. Download from the Command Line

You can also call the upstream CLI directly:

```shell
jmcomic 211899 --option="D:/Others/JMComic-Crawler-Python/jmcomic-option.yml"
```

Batch download:

```shell
jmcomic 211899 123456 654321 --option="D:/Others/JMComic-Crawler-Python/jmcomic-option.yml"
```

## Catalog File

After downloads, the project automatically maintains:

```text
D:/Others/JMComic/catalog.md
```

Example catalog entry:

```md
# Author

1. <img src="data:image/jpeg;base64,..." alt="JM211899" width="120" style="vertical-align: top;">

   - 📖 Title: Album title
   - 🆔 ID: JM211899
   - 🔗 Link: https://18comic.vip/album/211899/
   - 🏷️ Tags: tag1, tag2
   - 📑 Chapters: Chapter 1 Album title (id: 211899)
```

Cover images are embedded directly into the Markdown file, so the catalog can still display covers when uploaded as a standalone file.

## Roadmap

- Wrap the current script workflow into a desktop application.
- Add a graphical download task manager.
- Add local library browsing, filtering, searching, and tag management.
- Add a configuration wizard to avoid hand-editing YAML.
- Add a clearer failed-download list and retry flow.

## Upstream Project

This project is based on:

- [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)

Thanks to the upstream author for providing the core API, downloader, and plugin framework. This repository is a personal local-library workflow extension and is not intended to replace the upstream project.
