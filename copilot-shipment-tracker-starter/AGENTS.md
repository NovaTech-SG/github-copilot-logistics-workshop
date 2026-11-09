GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

# 学员跟练约定

## Spec Kit活动功能

活动功能由`.specify/feature.json`记录，当前为`specs/001-exception-followup`。优先读取该目录spec.md、plan.md、tasks.md和`.specify/memory/constitution.md`。docs/spec.md与docs/tasks.md只是兼容入口。

使用本项目官方Copilot skills，逐步执行`/speckit-specify`、`/speckit-clarify`（有歧义时）、`/speckit-plan`、`/speckit-tasks`、`/speckit-implement`和`/speckit-converge`。当前为学员起始检查点，保留尚未完成的业务任务。课堂P1范围见tasks.md，不自动扩展P2。预置产物与任务勾选不作为真实运行证据。不要自动安装其他扩展、提交、推送或部署。

先读docs/spec.md和docs/tasks.md，解释业务规则并列改动计划，再开始实现。

- 仅在当前学员项目开发，不搜索父目录或相邻完成版。
- 本阶段只完成services/store.py的save和static/app.js的表单submit处理，再补相应测试。复用已提供的连接、查询、校验、建表、overlay和api函数。
- 源数据来自Databricks只读MCP。仅调用execute_sql_read_only与poll_sql_result，不写源表、不使用CSV或固定业务数据兜底。
- 跟进状态与备注只写本项目SQLite，不修改Dashboard文件。按exception_id区分，不按shipment_id覆盖。
- 按OPEN→IN_PROGRESS→RESOLVED推进，可同状态更新备注。备注非空、最多1000字；保存带原状态，过期时拒绝覆盖。
- POST成功后重新GET核对。保存失败或未确认时不得提示成功。页面区分源状态与本机跟进。
- Token只在后端，数据库和凭据不入Git。Python3.12与uv，前端保持原生实现。
- 完成后运行离线测试和node --check static/app.js，如实记录实际查询、页面验证和未完成项。
- 不自行提交、推送、部署或增加CD。
