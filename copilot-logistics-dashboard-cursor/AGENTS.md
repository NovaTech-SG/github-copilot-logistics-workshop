# Cursor 迁移前对照项目

这是 Dashboard 完成版的 Cursor 对照目录，用于课堂解释 Rules、Skills、上下文、MCP 与调试迁移。业务代码和规格沿用已记录的教学基线；没有明确业务变更请求时只读分析。

先读 `.specify/memory/constitution.md`、`docs/data-source.md` 和 `specs/001-carrier-dashboard/spec.md`、`plan.md`、`tasks.md`。活动指针缺失时，仅在需要 Spec Kit 检查时运行 `uv run python tools/bootstrap_training.py` 恢复已有规格选择。

- 使用本项目 `.cursor/skills/` 中的官方 Spec Kit Skills。每次只执行用户指定的阶段，不自动实现、提交、推送或部署。
- 不从相邻项目读取答案；课堂对照由讲师按指定文件分别展示。
- Python 3.12、独立 uv 环境、原生前端；复用现有连接和校验，不重写业务逻辑。
- 源表仅通过 `execute_sql_read_only`、`poll_sql_result` 读取；不写 Databricks，不使用 CSV、聊天结果或固定数字兜底。
- Token 只在后端使用，不读取或展示实际凭据，不进入代码、页面或 Git。
- 调试配置和 `start.ps1` 使用端口 8770；直接运行 app.py 时显式加 `--port 8770`。
- 验收依据活动 spec 和 acceptance，分别记录离线、实时 MCP、页面及 CI。未执行的 Cursor 或 Copilot 会话不能标为已验证。

业务代码来源与哈希见 `.specify/migration-baseline.json`；变更业务基线需要明确需求。
