GitHub首次克隆后，如`.specify/feature.json`不存在，先运行`uv run --locked python tools/bootstrap_training.py`，再定位当前活动规格。不要覆盖已有有效的功能选择。

# 项目约定

## Spec Kit活动功能

活动功能由`.specify/feature.json`记录，当前为`specs/001-exception-followup`。优先读取该目录spec.md、plan.md、tasks.md和`.specify/memory/constitution.md`。docs/spec.md与docs/tasks.md只是兼容入口。

使用本项目官方Copilot skills，逐步执行`/speckit-specify`、`/speckit-clarify`（有歧义时）、`/speckit-plan`、`/speckit-tasks`、`/speckit-implement`和`/speckit-converge`。当前为讲师完成版，只有明确要求修改业务时才执行implement；通常作只读复盘。课堂P1范围见tasks.md，不自动扩展P2。预置产物与任务勾选不作为真实运行证据。不要自动安装其他扩展、提交、推送或部署。

本项目是Session 2第二个案例的完成版。先阅读docs/spec.md，再给出改动计划和验收方式。

- Python 3.12、uv、原生HTML/CSS/JavaScript。依赖变更同步更新uv.lock。
- 源数据仅从Databricks MCP读取。只调用execute_sql_read_only与poll_sql_result，不调用写入工具，不用CSV或固定数据兜底。
- 课堂状态和备注仅写入本项目的本地SQLite，以exception_id为主键。不要回写Databricks，不访问Dashboard项目的数据文件。
- 待处理→处理中→已解决，不跳过或退回；允许当前状态下更新备注。备注必填、去首尾空格后最多1000字。
- 保存后从服务端重新读取确认；源记录和本机记录必须明确区分。失败不能显示成功。
- Token仅后端使用，不输出、不提交、不进前端。数据库、虚拟环境、QA输出不入Git或学员包。
- 改动后运行uv run --locked python -m unittest discover -s tests -v与node --check static/app.js。实际MCP、浏览器检查、远程CI分别报告。
- 本地运行，不部署、不增加CD、不修改相邻仓库。
