GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

# 项目约定

## Spec Kit活动功能

活动功能由`.specify/feature.json`记录，当前为`specs/001-carrier-dashboard`。优先读取该目录spec.md、plan.md、tasks.md和`.specify/memory/constitution.md`。docs/spec.md与docs/tasks.md只是兼容入口。

使用本项目官方Copilot skills，逐步执行`/speckit-specify`、`/speckit-clarify`（有歧义时）、`/speckit-plan`、`/speckit-tasks`、`/speckit-implement`和`/speckit-converge`。当前为讲师完成版，只有明确要求修改业务时才执行implement；通常作只读复盘。课堂P1范围见tasks.md，不自动扩展P2。预置产物与任务勾选不作为真实运行证据。不要自动安装其他扩展、提交、推送或部署。

这是 Session 2 的本地物流 Dashboard，所有展示数据均为培训模拟数据。

- 开始改动前先读 `docs/spec.md`，说明要修改的文件和验收方式。
- 采用 Python 3.12、uv 和现有原生 HTML/CSS/JavaScript。依赖变更同时更新 `uv.lock`。
- 应用运行时从 Databricks MCP 获取实际结果，仅调用 `execute_sql_read_only` 和 `poll_sql_result`。不得改用 CSV、SQL Connector 或在失败时返回固定数据。
- 不创建、修改或删除 Databricks 业务数据。不要调用具有写入能力的 `execute_sql`。
- Token 只在服务端使用。不要输出、持久化、提交或通过 API 返回 Token。配置通过环境变量或显式 `--vscode-config` 读取。
- 准时率和排除规则以 `docs/spec.md` 为准。筛选后指标、图表和明细必须使用同一数据范围。
- 新增行为需要有相应验证。完成后运行 `uv run --locked python -m unittest discover -s tests -v` 和 `node --check static/app.js`。
- 未执行真实 MCP 查询、浏览器检查或远程 CI 时，应明确说明未验证。
- 当前只在本地运行。不要添加服务器部署或 CD。
