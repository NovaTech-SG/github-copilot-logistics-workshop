数据来源与表关系先读本项目 `docs/data-source.md`。运行时通过 Databricks 只读 MCP 获取业务源表；按表关系与本次范围生成规格和实现。

GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

遵守根目录AGENTS.md和.specify/memory/constitution.md。活动需求、计划与任务以.specify/feature.json指向的`specs/001-exception-followup`为准。Spec Kit课堂步骤见README.md与docs/prompts.md。

遵守根目录AGENTS.md。业务规则与验收见specs/001-exception-followup/spec.md，跟练任务见specs/001-exception-followup/tasks.md。

本项目是起始项目，读取已准备，保存待完成。先计划，再实现store.save与前端submit处理。使用真实只读MCP，跟进仅保存在本项目SQLite。不要访问相邻完成版，不输出Token，不修改Dashboard项目。
