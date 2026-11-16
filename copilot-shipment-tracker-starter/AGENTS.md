# 异常跟进新增功能课堂规则

## 起点和练习目标

这是在现有应用上新增功能的练习。Databricks MCP、异常查询、队列、搜索筛选、分页、详情、规则校验、SQLite 建表和 overlay 已提供；本轮补齐本机保存与前端提交后确认。

初始 `specs/` 只有 `.gitkeep`，没有预置 spec、plan、tasks 或活动功能指针。先读 `.specify/memory/constitution.md`、`docs/data-source.md`、`docs/prompts.md` 和 `mockup/README.md`。效果稿展示新增功能完成后的目标，不提供保存实现。

## 按阶段新增功能

1. 用户调用 `/speckit-specify` 后，针对本机保存与重读确认生成新功能规格。官方技能创建功能目录和 `.specify/feature.json`；bootstrap 不恢复旧规格。
2. 按用户指令逐步 clarify、plan、tasks、analyze、implement 和 converge。已有活动规格时按指针读取，保留学员自己的内容。
3. 需求没有要求改变的读取、列表、详情、查询和页面布局保持现有行为。本次主要修改 `services/store.py` 的 `save`、`static/app.js` 的 submit，以及必要测试。
4. 每步先报告产物或拟改任务与文件，完成当前阶段后停下，不自动跑完整个流程。任务 ID 以本次生成结果为准。
5. 不读取父目录、相邻完成版、内部备份或 Git 历史中的答案，不复制完整成品实现。

## 数据与保存边界

- 运行时源数据通过现有 Databricks 只读 MCP 获取，只调用 `execute_sql_read_only` 和 `poll_sql_result`，不写源表。
- 跟进状态和备注仅保存到本项目 SQLite，以 `exception_id` 区分。同一运输单的其他异常和源数据保持独立。
- 复用已有状态与备注校验、事务连接及 overlay。状态按 OPEN → IN_PROGRESS → RESOLVED 推进，允许同状态补备注；提交要携带原状态。
- 前端 POST 保存后 GET 同一异常，核对结果后才显示成功；已提交但未确认要单独说明。处理加载、失败与重复提交。
- mockup 中的固定样例仅用于视觉参考；不作为运行时数据，不伪装成真实保存结果。
- 保持 Python 3.12、独立 uv 环境、原生前端和现有依赖。Token 只在后端，不输出、不提交、不进页面；本机数据库不提交。
- 结构检查允许没有规格、只有 spec、已有 plan 或已有 tasks，不用保留无效 TODO 来满足旧检查。
- 完成后运行本项目离线测试与 `node --check static/app.js`。分别报告实时 MCP、页面与重启恢复的实际验证；没有用户明确要求，不提交、推送、部署或增加 CD。
