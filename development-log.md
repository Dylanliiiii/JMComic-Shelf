# Development Log

## 2026-06-17 21:32:32 +08:00

### 修改范围

- 本地项目目录命名
- 项目文档与协作说明检查

### 涉及文件

- `development-log.md`

### 具体内容

- 准备将本地项目文件夹从 `JMComic-Crawler-Python` 重命名为 `JMComic-Shelf`，与 GitHub 仓库名保持一致。
- 检查 README、英文 README、`AGENTS.md` 和项目专属 Skill 中的 `JMComic-Crawler-Python` 引用，确认这些引用均指向上游原作者项目，应保留作为来源说明，不应误改为当前仓库名。
- 确认当前仓库远程仍为 `origin -> Dylanliiiii/JMComic-Shelf`，`upstream -> hect0x7/JMComic-Crawler-Python`。

### 验证情况

- 已运行文本检索，确认没有需要修改的本地旧目录名引用。
- 已确认 `D:\Others\JMComic-Shelf` 当前不存在，可以用于重命名。

## 2026-06-17 21:31:00 +08:00

### 修改范围

- 项目协作说明
- 项目专属 Skill
- 开发记录

### 涉及文件

- `AGENTS.md`
- `README.md`
- `assets/readme/README-en.md`
- `.agents/skills/jmcomic-shelf-project/SKILL.md`
- `.agents/skills/jmcomic-shelf-project/agents/openai.yaml`
- `.agents/skills/jmcomic-shelf-maintenance/SKILL.md`
- `.agents/skills/jmcomic-shelf-maintenance/agents/openai.yaml`
- `development-log.md`

### 具体内容

- 新增 `AGENTS.md`，记录项目定位、上游关系、敏感配置、下载目录、PDF、Markdown 总目录、Windows 脚本、质量要求和 GitHub 维护规则。
- 新增 `jmcomic-shelf-project` 项目专属 Skill，用于后续维护下载工作流、目录插件、README、脚本和桌面应用规划。
- 新增 `jmcomic-shelf-maintenance` 项目专属 Skill，用于后续每次修改后的开发记录、验证、commit 和 GitHub push。
- 新增 `development-log.md`，用于记录项目后续演进。
- 将 README 中的本机绝对路径示例改为相对配置文件示例，避免开源文档依赖维护者电脑路径。

### 验证情况

- 本次为项目协作说明、Skill 和 README 文档更新，未运行应用单元测试。
- 已参考 LaunchDock 的 `AGENTS.md`、项目专属 Skill 和 `development-log.md` 结构。
