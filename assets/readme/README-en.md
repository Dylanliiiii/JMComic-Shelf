<div align="center">
  <img src="../icon.png" alt="JMComic Shelf" width="120" height="120">

  <h1 style="margin-top: 12px" align="center">JMComic Shelf</h1>

  <p align="center">
    <a href="../../README.md">简体中文</a> ·
    <strong>English</strong>
  </p>

  <p align="center">
    <strong>A personal comic downloader, PDF exporter, and local library manager based on JMComic-Crawler-Python</strong>
  </p>

[![GitHub](https://img.shields.io/badge/GitHub-Dylanliiiii%2FJMComic--Shelf-181717?logo=github)](https://github.com/Dylanliiiii/JMComic-Shelf)
[![Upstream](https://img.shields.io/badge/Based%20on-hect0x7%2FJMComic--Crawler--Python-blue)](https://github.com/hect0x7/JMComic-Crawler-Python)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Packaging](https://img.shields.io/badge/Packaging-PyAppify-00aeba)](https://github.com/ok-oldking/pyappify)

</div>

> JMComic Shelf is a personal local-library workflow built on top of [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python).
>
> It keeps the upstream downloader, parser, API, and plugin system, while adding a PySide6 + QFluentWidgets desktop app for local collection management.

## Install and Run

### Release Build

Release builds are published on GitHub:

- [JMComic Shelf Releases](https://github.com/Dylanliiiii/JMComic-Shelf/releases)

The desktop release is packaged with [ok-oldking/pyappify](https://github.com/ok-oldking/pyappify). The PyAppify launcher installs the app from GitHub tags, prepares an isolated Python environment, and uses Git/tag based updates for later launches. The PyAppify entry point is `run-jmcomic-shelf.py`, which prefers the updated `working/src` tree over stale installed `site-packages` code.

### Source Checkout

When running from source, double-click:

```text
start-jmcomic-shelf.bat
```

Or install the project and run:

```shell
pip install -e .
jmcomic-shelf
```

## Desktop Features

- Local library browsing backed by SQLite.
- Rebuildable index from the current download directory.
- Search by JM ID, author, or tag.
- Multi-tag category filtering.
- Non-cropped cover thumbnails.
- Download task list with retry support.
- Detail lookup for a single JM ID.
- The Official JMComic page groups the release page, mirror domains, app download, and support contacts, opening links in the system browser.
- Settings page for download directory, `jmcomic-option.yml`, app data directory, and theme mode.
- Light, dark, and system theme modes, persisted across restarts.

Desktop app data is stored under:

```text
%APPDATA%/JMComic Shelf/
  settings.json
  shelf.db
  covers/
```

Downloaded images, PDF files, and the human-readable `catalog.md` remain in the user-selected download directory.

## Packaging

Packaging files:

- `pyappify.yml`
- `run-jmcomic-shelf.py`
- `.github/workflows/release.yml`
- `icons/icon.png`
- `icons/icon.ico`

Release tags use `vMAJOR.MINOR.PATCH`, for example `v0.1.0`. CNB mirroring is not configured.

## References

- Upstream downloader: [hect0x7/JMComic-Crawler-Python](https://github.com/hect0x7/JMComic-Crawler-Python)
- Desktop UI and project style reference: [Dylanliiiii/LaunchDock](https://github.com/Dylanliiiii/LaunchDock)
- Packaging and updates: [ok-oldking/pyappify](https://github.com/ok-oldking/pyappify)
- PyAppify GitHub Action: [ok-oldking/pyappify-action](https://github.com/ok-oldking/pyappify-action)

Thanks to the upstream author for the core API, downloader, and plugin framework. JMComic Shelf is a personal local-library extension, not a replacement for the upstream project.
