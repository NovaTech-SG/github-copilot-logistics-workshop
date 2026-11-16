# Dashboard 学员项目规则

## 从需求开始

本项目只预装 Spec Kit、Python HTTP 服务、Databricks MCP 连接模块和页面骨架。初始 `specs/` 只有 `.gitkeep`，没有活动功能指针。没有 spec 是正常起点；bootstrap 不生成规格。新克隆只有一份已写好的 spec 时，仅恢复其本机活动指针；多份未选择时提示人工选择。

先读 `.specify/memory/constitution.md`、`docs/prompts.md` 和 `mockup/README.md`，再看 `mockup/index.html`。需求素材由讲师与学员调整；效果稿说明布局和目标，不能代替业务规则。

## 课堂按阶段推进

1. 用户调用 `/speckit-specify` 后，从本项目需求和 mockup 生成规格，并由官方技能写入 `.specify/feature.json`。
2. 存在活动指针时，只读取它指向的本项目功能目录。先核对 spec，需要时 clarify，再 plan、tasks、analyze、implement 和 converge。
3. 没有 plan/tasks 时先生成相应产物，不从父目录、相邻完成版、内部资料或 Git 历史提取预写规格与答案。
4. 每次只完成用户指定阶段。生成文档后先报告产物与待确认问题，等待下一条课堂指令，不自动继续所有步骤。
5. 实现时先列本次任务 ID、拟改文件和验收方式。P1 是指标、筛选和对比图；趋势与分页是 P2，另行安排。任务 ID 以本次生成的 tasks 为准。

## 技术与数据边界

- Python 3.12、当前项目独立 uv 环境、原生 HTML/CSS/JavaScript。保留现有依赖；确需变更时同步 uv.lock。
- 复用 `services/settings.py` 和 `services/mcp_sql.py`，仅调用 `execute_sql_read_only` 和 `poll_sql_result`；不修改 Databricks 源表。
- `mockup/` 中固定的展示值仅供视觉参考。运行时不导入 mockup，不用 CSV、聊天结果或固定业务数值代替 MCP；失败明确报错。
- Token 只在后端使用，不输出、不提交、不进前端，不读取或展示本机实际凭据。
- 指标以课堂生成且经核对的 spec 为准。所有已实现组件使用同一筛选范围；避免一对多关联放大单量。
- `tools/check_training.py` 检查基础文件和 SDD 阶段，不证明业务完成；不要求为了满足旧检查而保留 NotImplementedError。
- 仅本地运行。按实际执行记录测试、实时查询、页面操作和未验证项。没有用户明确要求，不提交、推送、安装额外扩展或部署。

## 数据来源与表关系

先读本项目 `docs/data-source.md`，核对 Databricks 只读 MCP、三张表的关联键和本项目使用范围。CSV 与效果稿只是参考，不是应用运行时数据源。
