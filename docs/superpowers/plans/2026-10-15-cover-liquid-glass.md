# 书库封面液态玻璃与透视倾斜实施计划

## 任务 1：玻璃瓦片控件

- 新增 `src/jmcomic_shelf/ui/glass_cover.py`，实现 `GlassCoverView`：固定尺寸 168×228、封面区 150×210、圆角封面缓存、`QTransform.quadToQuad` 透视贴图、跟随指针的径向高光、青色内缘辉光、柔和投影。
- 抽出模块级 `dip_quad` / `perspective_transform` 作为共享透视数学，并让控件在悬停或指针变化时发出 `view_changed` 信号。
- 提供 `set_cover_path`、`set_placeholder`、`has_cover`、`set_pointer`、`hover_in`、`hover_out`、`dip_quad`、`view_transform`，以及 `hoverProgress` 属性供动画驱动。

## 任务 2：接入书库卡片

- `src/jmcomic_shelf/ui/library_page.py` 的 `CoverCard` 用 `GlassCoverView` 替换封面 `QLabel`，`_load_cover` 改为调用 `set_cover_path`。
- 卡片内边距改为 5px、间距改为 4px，使瓦片在 178px 宽的卡片中居中。
- `CoverCard` 监听 `view_changed`，悬停时把标题文字置为透明并用同一单应变换绘制倾斜标题，指针移开后恢复真实标签。

## 任务 3：测试

- 先写 `tests/test_jmcomic/test_shelf_glass_cover.py`，确认缺少 `glass_cover` 模块时失败。
- 覆盖：近鼠标角内压/对角外扩、指针裁剪、动画终值与时长、离屏渲染非透明且有差异、无封面占位、`CoverCard.cover` 类型与尺寸、悬停时标题置为透明并在移开后恢复、封面与标题共用同一透视变换。
- 运行 `$env:PYTHONPATH='src;tests'; py -3.13 -m unittest discover -s tests -p 'test_shelf_*.py' -v`。

## 任务 4：视觉验证

- 用离屏脚本渲染常态与四个角悬停状态，逐张核对倾斜方向、玻璃高光和投影是否正确，必要时调整方向常量或强度参数。

## 任务 5：文档与提交

- 同步 README、英文 README、`AGENTS.md`、项目专属 Skill 的书库封面说明，并在 `development-log.md` 记录实现与验证。
- 运行相关 `py_compile`、`git diff --check`、`git check-ignore -v jmcomic-option.yml`。
- 提交并推送 `origin master`，确认工作区干净后清空 `TASKS.md`。
