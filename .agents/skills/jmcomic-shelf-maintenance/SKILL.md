---
name: jmcomic-shelf-maintenance
description: 仅用于 JMComic Shelf 项目的维护技能。用于代码或文档修改后的开发记录、验证、提交和 GitHub push；当用户要求更新 GitHub、维护 README/AGENTS/Skill、或完成普通代码文档修改后需要收尾时使用。
---

# JMComic Shelf 维护技能

## 核心原则

- 只服务当前 JMComic Shelf 仓库。
- 普通代码或文档更新完成后，必须更新 `development-log.md`，运行匹配风险的验证，然后 commit 并 push 到 GitHub。
- 重要规划、桌面应用设计、技术路线确认、阶段性进度和下一步安排，也应写入 `development-log.md`；开发记录用于帮助新对话理解项目状态，不只用于记录已落地 diff。
- 交付附带新增功能、文件结构变化、工作流变化或用户可见行为变化时，必须同步检查并按需更新 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/`；不能只更新 `development-log.md`。
- 默认只 push 到 GitHub，不创建 tag，不创建 release。
- 只有用户明确要求“release / 发版 / 打包 / 发布新版本”时，才进入 release 准备。
- 正式桌面版 release 使用 `vMAJOR.MINOR.PATCH` 版本号，例如 `v0.1.0`。
- Release 版本基线必须来自当前仓库 `origin` 远端：优先执行 `git ls-remote --tags origin`，必要时再查看 `https://github.com/Dylanliiiii/JMComic-Shelf/releases`。不要使用本地 `git tag`、`git describe --tags` 或 `src/jmcomic/__init__.py` 推断本项目最新 Release，因为本仓库包含上游 `hect0x7/JMComic-Crawler-Python` 的历史 tag 和版本号。
- 桌面应用打包使用 `pyappify.yml` 和 `.github/workflows/release.yml`；推送 `v*` tag 后由 GitHub Actions 调用 `ok-oldking/pyappify-action` 构建 Windows 包并上传到 GitHub Release。
- PyAppify release profile 的 `main_script` 必须保持为 `run-jmcomic-shelf.py`，不能改回 `jmcomic-shelf` console script；否则自动更新在依赖未变化时可能跳过 pip 同步并继续运行旧代码。
- 不涉及 CNB 镜像维护或对应 Action，除非用户未来明确要求。
- 不提交 `jmcomic-option.yml`、账号密码、cookie、token、代理凭据、下载内容、PDF 或本地 `catalog.md`。

## 意图判断

- “修改代码”“修 README”“更新 GitHub”“push 一下”：普通更新，完成后 commit + push。
- “发版”“release”“打包”“发布新版本”：先确认版本号和发布范围，再准备 release。
- “更新版本”但语义不清：先询问是普通 push 还是正式 release。
- 用户明确说“暂时不 release”：只 commit + push。

## 普通更新流程

1. 读取 `AGENTS.md` 和相关项目专属 Skill。
2. 完成代码、脚本或文档修改。
3. 更新 `development-log.md`，日常条目使用时间标题，不写版本号；如果只是普通开发、测试、文档同步或未正式发布，明确写“未更新项目版本号，也未发布 Release”。
4. 检查 README、`AGENTS.md`、项目专属 Skill、`docs/superpowers/specs/` 和 `docs/superpowers/plans/` 是否因本次改动需要同步更新；如果无需更新，在开发记录中写明判断。
5. 运行匹配改动范围的验证。
6. 检查 `git status --short` 和关键 diff。
7. 确认 `jmcomic-option.yml` 仍为 ignored，且 diff 中无账号密码。
8. `git add`、`git commit`。
9. `git push origin master`。

## 开发记录格式

在 `development-log.md` 顶部新增：

```markdown
## YYYY-MM-DD HH:mm:ss +08:00

### 修改范围

- ...

### 涉及文件

- `path/to/file`

### 具体内容

- ...
- 如果是规划记录，写清当前结论、待确认问题和下一步。

### 验证情况

- 已运行 `...`，结果通过。
- 或：本次为文档更新，未运行代码测试。
```

记录要具体，但不要写入账号、密码、cookie、token 或本机私有下载内容。

## 验证建议

目录插件或下载逻辑：

```powershell
python -m unittest discover -s tests -p test_jm_plugin.py -k catalog -v
python -m py_compile src\jmcomic\jm_plugin.py
```

README / AGENTS / Skill：

- 检查相对链接是否正确。
- 检查仓库名、脚本名、配置文件名是否一致。
- 检查是否出现本机绝对路径或敏感信息。
- 如果文档提到用户提供的参考项目、教程、工具或外部资料，检查是否保留完整 URL，避免只写项目名导致后续无法追溯。

脚本：

- 检查 `start-jmcomic-shelf.bat` 仍通过 `%~dp0` 推导源码目录。
- 如果可行，手动说明未实际执行下载，避免误触网络或下载内容。

## Release 预留规则

当前项目暂不默认 release。只有用户明确要求 release、发版或打包时才执行。

如果用户明确要求 release：

1. 先获取远端版本基线：运行 `git ls-remote --tags origin`，只读取 `origin` 的 `refs/tags/v*`；如果命令失败或结果可疑，再查看 GitHub Releases 页面。禁止用本地 tag 列表推断版本号。
2. 按语义化版本选择新版本：主版本号用于大改或不兼容变更，次版本号用于新功能，修订号用于 bug 修复或小型改进。例如当前 `origin` 最新为 `v0.1.0` 时，普通新功能用 `v0.2.0`，小修小改用 `v0.1.1`；不确定时先询问用户。
3. 如果需要同步项目自身版本文件，只更新本项目自己的版本号；不要把 `src/jmcomic/__init__.py` 的上游版本号当作桌面版 Release 基线。
4. 在 `development-log.md` 顶部新增 `## Version x.x.x - YYYY-MM-DD HH:mm:ss +08:00` 记录，并写明远端最新 tag 查询结果、版本递增理由、修改重点和验证情况。日常开发记录不使用 `Version` 标题。
5. 汇总自上次带 `Version` 的发布记录以来的 `development-log.md` 重点作为 Release 正文；正文不应过长，小型格式、文案和布局调整可概括。
6. 确认 `pyappify.yml`、`run-jmcomic-shelf.py`、`.github/workflows/release.yml`、`icons/icon.png` 和 `icons/icon.ico` 存在且与当前入口一致；`pyappify.yml` 的 `main_script` 应为 `run-jmcomic-shelf.py`。
7. 创建 tag 和 GitHub Release 前再次确认不会包含本地配置、账号密码、下载内容、PDF 或 `catalog.md`。
8. `git push origin master` 后再推送 tag；GitHub Actions 会构建并上传 PyAppify 产物。
9. 不创建 CNB 镜像同步配置，除非用户未来明确要求。

## 收尾检查

完成后确认：

- `git status --short` 为空，除非明确说明剩余文件。
- `origin` 指向 `https://github.com/Dylanliiiii/JMComic-Shelf.git`。
- `upstream` 指向 `https://github.com/hect0x7/JMComic-Crawler-Python.git`。
- `development-log.md` 已记录本次修改。
- 如果本次是正式 release，已记录 `git ls-remote --tags origin` 查到的最新远端 tag 和新版本选择理由；如果不是正式 release，开发记录明确说明未更新项目版本号。
- `TASKS.md` 已更新当前步骤状态；如果本次任务已全部完成并验证通过，则已清空本次任务，只保留“暂无进行中任务”。
- README、AGENTS、项目专属 Skill、spec 和 plan 没有明显过期，或已在开发记录中说明无需更新。
- 最终回复包含提交哈希、push 结果和验证情况。

## 任务续做台账

根目录 `TASKS.md` 是普通修改流程的一部分。

- 开始维护、收尾、提交或 push 前，检查 `TASKS.md` 是否仍有未完成任务。
- 如果还有未完成任务，不要清空；在最终回复中说明剩余步骤。
- 如果所有任务已完成且验证通过，提交前把本次任务清空为“暂无进行中任务”。
- `TASKS.md` 只记录任务状态，不记录敏感配置或用户本地下载内容。
