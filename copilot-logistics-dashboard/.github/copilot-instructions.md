数据来源与表关系先读本项目 `docs/data-source.md`。运行时通过 Databricks 只读 MCP 获取业务源表；按表关系与本次范围生成规格和实现。

GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

遵守根目录AGENTS.md和.specify/memory/constitution.md。活动需求、计划与任务以.specify/feature.json指向的`specs/001-carrier-dashboard`为准。Spec Kit课堂步骤见README.md与docs/prompts.md。

# Copilot 项目说明

请遵守根目录 `AGENTS.md`。需求和验收口径见 `specs/001-carrier-dashboard/spec.md`，只读复盘见 `README.md` 和 `docs/prompts.md`，按 README 验收，在课堂笔记或 PR 中记录实际结果。

先说明计划，再做小范围改动。开发时可以用 `databricksTraining` 的只读工具检查表结构和结果；应用运行时仍必须由 Python 后端通过 MCP 查询，不要把聊天中的查询结果硬编码到页面。

Token 不进仓库、不进前端。连接失败展示明确错误。准时率使用总分子除以总分母，分母零显示 N/A。不要引入 CSV、SQL Connector、服务器部署或 CD。
