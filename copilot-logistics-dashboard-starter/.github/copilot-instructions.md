GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

遵守根目录AGENTS.md和.specify/memory/constitution.md。活动需求、计划与任务以.specify/feature.json指向的`specs/001-carrier-dashboard`为准。Spec Kit课堂步骤见docs/speckit.md与docs/prompts.md。

# 跟练说明

遵守根目录 `AGENTS.md`。读取 `docs/spec.md` 明确业务口径，按 `docs/tasks.md` 完成当前阶段。先计划，再小步实现与验收。

请在本项目内独立实现，不搜索相邻完成版。复用已提供的MCP连接模块；运行时后端必须调用真实MCP。Token不进前端或仓库。指标数值用于验收，不可硬编码到业务实现。只在用户要求的阶段追加扩展功能。
