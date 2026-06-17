---
name: jmcomic-shelf-maintenance
description: 仅用于 JMComic Shelf 项目的维护技能。用于代码或文档修改后的开发记录、验证、提交和 GitHub push；当用户要求更新 GitHub、维护 README/AGENTS/Skill、或完成普通代码文档修改后需要收尾时使用。
---

# JMComic Shelf 维护技能

## 核心原则

- 只服务当前 JMComic Shelf 仓库。
- 普通代码或文档更新完成后，必须更新 `development-log.md`，运行匹配风险的验证，然后 commit 并 push 到 GitHub。
- 重要规划、桌面应用设计、技术路线确认、阶段性进度和下一步安排，也应写入 `development-log.md`；开发记录用于帮助新对话理解项目状态，不只用于记录已落地 diff。
- 默认只 push 到 GitHub，不创建 tag，不创建 release。
- 只有用户明确要求“release / 发版 / 打包 / 发布新版本”时，才进入 release 准备。
- 不涉及 CNB 镜像维护，除非用户未来明确要求。
- 不提交 `jmcomic-option.yml`、账号密码、cookie、token、代理凭据、下载内容、PDF 或本地 `catalog.md`。

## 意图判断

- “修改代码”“修 README”“更新 GitHub”“push 一下”：普通更新，完成后 commit + push。
- “发版”“release”“打包”“发布新版本”：先确认版本号和发布范围，再准备 release。
- “更新版本”但语义不清：先询问是普通 push 还是正式 release。
- 用户明确说“暂时不 release”：只 commit + push。

## 普通更新流程

1. 读取 `AGENTS.md` 和相关项目专属 Skill。
2. 完成代码、脚本或文档修改。
3. 更新 `development-log.md`，日常条目使用时间标题，不写版本号。
4. 检查 README、`AGENTS.md`、项目专属 Skill 是否因本次改动需要同步更新。
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

- 检查 `.bat` 仍引用 `%~dp0jmcomic-option.yml`。
- 如果可行，手动说明未实际执行下载，避免误触网络或下载内容。

## Release 预留规则

当前项目暂不默认 release。

如果用户明确要求 release：

1. 先确认版本号。
2. 汇总自上次 release 以来的 `development-log.md` 重点。
3. 确认是否需要打包桌面应用；当前未形成桌面应用前，不要伪造安装包。
4. 创建 tag 和 GitHub Release 前再次确认不会包含本地配置、账号密码、下载内容、PDF 或 `catalog.md`。

## 收尾检查

完成后确认：

- `git status --short` 为空，除非明确说明剩余文件。
- `origin` 指向 `https://github.com/Dylanliiiii/JMComic-Shelf.git`。
- `upstream` 指向 `https://github.com/hect0x7/JMComic-Crawler-Python.git`。
- `development-log.md` 已记录本次修改。
- README、AGENTS 和项目专属 Skill 没有明显过期。
- 最终回复包含提交哈希、push 结果和验证情况。
