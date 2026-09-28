# 书库文本复制与批量传输实施计划

## 任务 1：传输服务

- 在 `tests/test_jmcomic/test_shelf_share_service.py` 先写服务测试，确认当前缺少模块时失败。
- 在 `src/jmcomic_shelf/share_service.py` 实现 `existing_pdf_paths`、`safe_archive_name`、`create_pdf_archive` 和 `copy_file_urls` 所需的纯逻辑。

## 任务 2：书库 UI

- 在 `CoverCard` 和作者分组标题上启用 Qt 文本选择与复制。
- 批量栏增加默认主要按钮“复制 PDF”和次要按钮“打包 ZIP”。
- 复制操作写入系统剪贴板并报告缺失文件；ZIP 操作使用保存对话框并报告输出路径。
- 用 UI 测试覆盖按钮文本、默认状态及文本交互标志。

## 任务 3：文档与验证

- 同步 README、AGENTS、项目 Skill 的书库能力描述，并在 `development-log.md` 记录设计、实现和验证。
- 运行 `$env:PYTHONPATH='src;tests'; py -3.13 -m unittest discover -s tests -p 'test_shelf_*.py' -v`。
- 运行相关 `py_compile`、`git diff --check`、`git check-ignore -v jmcomic-option.yml`。
- 提交并推送 `origin master`，确认工作区干净后清空 `TASKS.md`。
