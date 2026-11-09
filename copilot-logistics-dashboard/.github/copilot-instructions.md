GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

遵守根目录AGENTS.md和.specify/memory/constitution.md。活动需求、计划与任务以.specify/feature.json指向的`specs/001-carrier-dashboard`为准。Spec Kit课堂步骤见docs/speckit.md与docs/prompts.md。

# Copilot 项目说明

请遵守根目录 `AGENTS.md`。需求和验收口径见 `docs/spec.md`，讲师演示流程见 `docs/demo.md`。

先说明计划，再做小范围改动。开发时可以用 `databricksTraining` 的只读工具检查表结构和结果；应用运行时仍必须由 Python 后端通过 MCP 查询，不要把聊天中的查询结果硬编码到页面。

Token 不进仓库、不进前端。连接失败展示明确错误。准时率使用总分子除以总分母，分母零显示 N/A。不要引入 CSV、SQL Connector、服务器部署或 CD。
