# 在现有异常队列上新增保存功能

遵守本项目 AGENTS.md 和 `.specify/memory/constitution.md`，先读 `docs/data-source.md`、`docs/prompts.md` 和 mockup。

列表、详情和 Databricks 只读查询是已有基础，本轮补本机 SQLite 保存与前端 POST 后 GET 确认。初始 specs 为空，由用户逐条调用 Spec Kit 生成新增功能的规格、计划和任务，再分后端、前端实现。

复用已有校验、连接和 overlay，不重写读取链路，不读取相邻项目或历史答案。按 exception_id 保存，源数据不变。效果稿只作参考，实际数据仍来自只读 MCP；Token 不输出或进入页面。

按 README 验收，如实记录本次结果与未验证项，不自动推进后续阶段或提交推送。
