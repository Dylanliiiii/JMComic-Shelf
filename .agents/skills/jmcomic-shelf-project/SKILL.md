---
name: jmcomic-shelf-project
description: 仅用于 JMComic Shelf 项目的专属技能。用于修改下载路径、PDF 转换、Markdown 目录插件、封面嵌入、Windows 脚本、README、项目说明和后续桌面应用封装设计；当用户在本仓库中要求维护漫画下载与本地书库工作流时使用。
---

# JMComic Shelf 项目技能

## 使用原则

- 只服务当前 JMComic Shelf 仓库，不作为全局通用技能。
- 默认使用中文编写说明、开发记录、协作约定和用户可见文档。
- 新增文件名和目录名优先使用简洁英文。
- 仓库内路径使用相对路径，不写死开发者本机绝对路径。
- 用户要求实现功能时，先读取根目录 `AGENTS.md`，再按当前代码结构做最小必要修改。
- 每次修改代码、脚本或文档后，同步更新 `development-log.md`。
- 每次修改后检查 README、`AGENTS.md`、项目专属 Skill 和相关说明是否仍与当前行为一致。
- 普通更新完成后，使用 `.agents/skills/jmcomic-shelf-maintenance/SKILL.md` 的流程提交并 push 到 GitHub。
- 始终避免提交 `jmcomic-option.yml`、账号密码、下载内容、PDF、`catalog.md` 或本地绝对配置。

## 项目目标

JMComic Shelf 基于 `hect0x7/JMComic-Crawler-Python`，面向个人本地收藏工作流：

- 通过配置下载漫画。
- 自动转换 PDF。
- 自动维护 Markdown 总目录。
- 提供不熟悉 PowerShell 的 Windows 用户可双击使用的脚本。
- 未来逐步封装为桌面应用。

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
- 保留来源标题、作者和标签文本，不强制繁简转换。
- 记录标题、ID、链接、标签、章节。
- 从本次下载成功的第一章第一张图片生成 base64 封面。
- 使用 HTML `<img>` 控制封面宽度和顶部对齐。

修改目录插件时，应同步检查：

- `tests/test_jmcomic/test_jm_plugin.py` 的 catalog 测试。
- README 中目录格式示例。
- `AGENTS.md` 中目录规则说明。
- `development-log.md`。

### Windows 脚本

- `download-jmcomic.bat`
- `view-jmcomic.bat`

脚本应：

- 使用脚本所在目录下的 `jmcomic-option.yml`。
- 给不熟悉命令行的用户清晰提示。
- 支持批量输入 JM 号。
- 不写死账号密码。

### 本地配置

`jmcomic-option.yml` 是用户本地文件，必须保持 ignored。

如需写配置示例，使用脱敏内容，不要复制真实账号、密码、代理或本机私有路径。

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
- 明确说明基于上游项目修改。
- 中文 README 为主入口。
- 英文 README 独立放在 `assets/readme/README-en.md`。
- 不把英文说明只追加在中文 README 末尾。

修改文档时，检查项目名、仓库链接、脚本名、配置文件名和目录示例是否一致。

## 后续桌面应用方向

如果用户开始做桌面应用，优先考虑：

- 继续复用当前下载配置和插件逻辑。
- 把账号、下载目录、封面宽度、并发等放入本地设置界面。
- UI 不直接保存账号密码到仓库文件。
- 下载任务、失败重试、目录预览和 PDF 打开是优先级较高的桌面功能。

在真正进入桌面开发前，应先明确技术栈和数据位置，不要把现有脚本逻辑一次性重写。

## 验证清单

根据改动范围选择验证：

- 目录插件：

```powershell
python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v
python -m py_compile src\jmcomic\jm_plugin.py
```

- README / AGENTS / Skill：
  - 检查链接和相对路径。
  - 检查是否误写本机绝对路径。
  - 检查是否泄露 `jmcomic-option.yml` 内容。

- Windows 脚本：
  - 检查脚本仍使用 `%~dp0jmcomic-option.yml`。
  - 检查没有写死维护者用户名或密码。

## 常见风险

- 长标题导致 Windows 路径过长。
- 多作者作品下载文件只存第一作者目录，但 catalog 会在所有作者下索引。
- base64 封面会让 `catalog.md` 变大。
- 使用网络封面接口可能拿到裁切缩略图，目录封面应优先使用已下载的第一张图片。
- 真实配置文件不能提交。
