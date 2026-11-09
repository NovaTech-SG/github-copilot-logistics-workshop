GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

# 学员项目规则

## Spec Kit活动功能

活动功能由`.specify/feature.json`记录，当前为`specs/001-carrier-dashboard`。优先读取该目录spec.md、plan.md、tasks.md和`.specify/memory/constitution.md`。docs/spec.md与docs/tasks.md只是兼容入口。

使用本项目官方Copilot skills，逐步执行`/speckit-specify`、`/speckit-clarify`（有歧义时）、`/speckit-plan`、`/speckit-tasks`、`/speckit-implement`和`/speckit-converge`。当前为学员起始检查点，保留尚未完成的业务任务。课堂P1范围见tasks.md，不自动扩展P2。预置产物与任务勾选不作为真实运行证据。不要自动安装其他扩展、提交、推送或部署。

先阅读 `docs/spec.md`、`docs/tasks.md` 和 `docs/data-contract.md`。说明改动计划、涉及文件和验收方式，再按任务逐步实现。

- 这是起始项目，业务功能尚未完成。请在本项目内独立实现，不访问父目录、相邻目录或完成版。
- Python 3.12、uv、原生HTML/CSS/JavaScript。依赖变更同步更新 `uv.lock`。
- 复用已有MCP连接模块。应用运行时通过Python后端调用 `execute_sql_read_only`，必要时调用 `poll_sql_result`。不得调用写入工具，不改动Databricks业务数据。
- 不使用CSV、SQL Connector、聊天结果或硬编码业务数值作为页面数据源。查询失败明确显示错误，不以固定数据兜底。
- Token只在后端使用，不输出、不提交、不进前端；不要读取或展示本机用户配置的实际Token。
- 准时率、排除、零分母规则以Spec为准。筛选后指标、图表、明细采用同一范围。不要关联一单多异常导致重复计数。
- 15分钟先完成基础任务，趋势和分页留作扩展。不要在第一步实现全部扩展。
- 完成后检查diff，并如实报告实际执行的测试与尚未验证的项目。不要自行提交、推送、部署或添加CD。
