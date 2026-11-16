数据来源与表关系先读本项目 `docs/data-source.md`。运行时通过 Databricks 只读 MCP 获取业务源表；按表关系与本次范围生成规格和实现。

# Dashboard 从需求开始的课堂约定

遵守本项目 `AGENTS.md` 和 `.specify/memory/constitution.md`。初始 `specs/` 为空，没有预置 spec、plan、tasks 或活动功能指针。

先读 `docs/prompts.md` 和 `mockup/README.md`。由用户逐条调用 `/speckit-specify`、需要时 clarify、plan、tasks，再按生成的任务实现。生成规格之前不要开始业务编码，也不要跳去读取相邻完成版、内部资料或 Git 历史中的答案。

`mockup/index.html` 是静态效果参考，固定样例不能用作应用数据。复用本项目只读 MCP 与启动骨架，Token 仅后端使用。按 README 验收，在本次课堂记录中如实说明结果，下一步由课堂指令决定。
