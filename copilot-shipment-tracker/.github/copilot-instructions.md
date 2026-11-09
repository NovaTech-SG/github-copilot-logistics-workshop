GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

遵守根目录AGENTS.md和.specify/memory/constitution.md。活动需求、计划与任务以.specify/feature.json指向的`specs/001-exception-followup`为准。Spec Kit课堂步骤见docs/speckit.md与docs/prompts.md。

遵守根目录AGENTS.md，需求与验收见docs/spec.md。先计划，再小步实现。

本案例练习状态更新与持久化。Databricks源记录只读，跟进状态和备注只保存在本项目SQLite。不要改变Dashboard项目、复制凭据、改用CSV或调用MCP写入工具。
