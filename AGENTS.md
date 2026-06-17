# JMComic Shelf 项目协作说明

## 默认语言

本项目的需求说明、开发记录、项目专属 Skill、注释和后续新增中文文档默认使用中文。

以下内容可以使用英文：

- 第三方库、API、命令、文件名、协议和代码标识符。
- 面向开源协作或工具识别的文件名与目录名。
- 用户明确要求英文时。

## 项目定位

JMComic Shelf 是基于 `hect0x7/JMComic-Crawler-Python` 的个人漫画下载与本地书库管理工具。

当前项目仍保留上游 Python API、下载器、命令行和插件体系，并在其基础上增加个人本地收藏工作流：

- Windows 双击脚本下载和查看详情。
- 下载后自动转 PDF。
- 下载后维护 `catalog.md` 总目录。
- 总目录按作者分组，并记录封面、标题、JM ID、链接、标签和章节。
- 封面以内嵌 base64 写入 Markdown，方便单独上传目录文件。
- 下载路径尽量避免 Windows 长路径问题。

后续目标是逐步封装为桌面应用，降低手写命令和 YAML 配置的成本。

## 上游关系

- 当前仓库：`https://github.com/Dylanliiiii/JMComic-Shelf`
- 上游仓库：`https://github.com/hect0x7/JMComic-Crawler-Python`
- 本地 remote 约定：
  - `origin` 指向 Dylanliiiii/JMComic-Shelf。
  - `upstream` 指向 hect0x7/JMComic-Crawler-Python。

本项目应明确保留对上游项目的致谢和来源说明，不应把上游能力描述成完全原创。

## 项目专属 Skill

本项目包含以下只服务于 JMComic Shelf 的项目专属 Skill：

- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`

这些 Skill 使用仓库相对路径，不能写成本机绝对路径。

`jmcomic-shelf-project` 使用场景：

- 修改下载目录规则、PDF 转换、目录插件、Windows 脚本或 README。
- 设计后续桌面应用封装方案。
- 调整项目说明、配置示例和本地书库工作流。

`jmcomic-shelf-maintenance` 使用场景：

- 每次代码或文档修改后更新 `development-log.md`。
- 运行匹配改动范围的验证。
- 提交并 push 到 GitHub。
- 判断是否需要 release。当前默认不创建 release，只有用户明确要求发版时才进入 release 准备。

后续如果新增、修改、删除或移动任何 Skill，必须同步更新本文件中的项目专属 Skill 说明。

## 敏感配置

`jmcomic-option.yml` 是本地配置文件，可能包含账号、密码、下载目录、代理等个人信息，必须保持在 `.gitignore` 中。

不得提交以下内容：

- JMComic 账号密码。
- cookie、token、代理凭据。
- 用户本地下载目录中的漫画、PDF、封面、`catalog.md`。
- 任何只适用于维护者电脑的绝对路径配置。

文档中如需展示配置，应使用脱敏示例。

## 当前工作流约定

### 下载目录

当前推荐路径规则：

```yaml
dir_rule:
  base_dir: D:/path/to/JMComic
  rule: Bd / Aauthor / JM{Aid}-{Atitle} / 第{Pindex}章
  normalize_zh: null
```

说明：

- 保留作者和作品标题，便于人工浏览。
- 章节目录使用短名称，避免标题重复导致 Windows 路径过长。
- 不强制繁简转换，标题、作者和标签保持来源文本。

### PDF

下载完成后通过 `img2pdf` 插件生成 PDF。PDF 命名保持 `JM号-作品名.pdf`。

### Markdown 总目录

`catalog` 插件负责维护下载根目录下的 `catalog.md`：

- 按作者分组。
- 每个作者下独立编号。
- 同一作品如有多个作者，会在每个作者下各登记一份索引。
- 同一作者下按 JM ID 去重更新，不重复追加。
- 封面优先使用本次下载成功的第一章第一张图片。
- 封面以内嵌 base64 写入 Markdown。
- 默认封面宽度为 `120`。

### Windows 脚本

- `download-jmcomic.bat`：输入一个或多个 JM 号后下载。
- `view-jmcomic.bat`：输入 JM 号后查看详情。

脚本应保持简单，适合不熟悉 PowerShell 的用户使用。

## 质量要求

- 修改下载、PDF、目录插件或路径规则时，优先添加或更新测试。
- 修改 `CatalogPlugin` 时至少运行：

```powershell
python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v
python -m py_compile src\jmcomic\jm_plugin.py
```

- 修改 README、AGENTS、Skill 或开发记录时，至少检查相关链接、路径和项目名是否一致。
- 修改脚本时，检查是否仍引用正确的 `jmcomic-option.yml` 和可执行文件路径。
- 每次修改代码或文档后，检查 README、`AGENTS.md`、项目专属 Skill、开发记录是否需要同步更新。

## 开发记录

每次生成或修改代码、脚本、README、AGENTS 或项目专属 Skill 时，都要同步更新 `development-log.md`。

`development-log.md` 不只记录已经落地的代码或文档修改；当进入重要规划阶段、形成关键设计思路、确认技术路线、拆分里程碑或暂停在某个阶段时，也应记录当前进度和下一步。这样新对话只要先阅读开发记录，就能理解项目推进到哪里。

记录内容应包括：

- 修改日期和具体时间。
- 修改范围。
- 涉及文件。
- 具体做了什么。
- 如属于规划或设计阶段，需要记录当前结论、待确认问题和下一步。
- 是否运行验证或测试。
- 如果没有运行验证或测试，需要说明原因。

日常修改不记录版本号。只有用户明确要求发版、打包或创建 release 时，才使用版本号记录。

## GitHub 维护规则

- 普通代码或文档修改完成并验证后，直接 commit 并 push 到 GitHub。
- 默认推送到 `origin master`。
- 不自动创建 tag，不自动创建 GitHub Release。
- 只有用户明确要求“release / 发版 / 打包 / 发布新版本”时，才准备 release。
- 如果用户表达“更新一下”“更新 GitHub”等，按普通 commit + push 处理。
- 提交前确认 `jmcomic-option.yml` 仍是 ignored，且没有账号密码进入 diff。

## 未来方向

- 将当前命令行和 bat 脚本流程封装为桌面应用。
- 提供图形化配置向导，减少手写 YAML。
- 提供下载任务管理、失败重试和补图入口。
- 提供本地书库浏览、筛选、搜索和标签管理。
- 在正式桌面应用阶段再设计 release、打包和版本更新规则。
