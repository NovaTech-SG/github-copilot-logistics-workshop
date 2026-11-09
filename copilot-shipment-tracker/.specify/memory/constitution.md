# Session 2 Logistics Constitution

## Core Principles

### I. 业务规格与验收先行
功能以活动功能目录的spec.md为业务依据，plan.md写技术选择，tasks.md记录步骤。需求变化先更新规格及验收，再调整代码。生成内容必须由业务人员核对。

### II. 真实来源与最小权限
业务源数据只通过已有Databricks只读MCP获取。只调用execute_sql_read_only与poll_sql_result。不回写源表，不用CSV、聊天结果或硬编码答案替代运行时查询。连接失败明确提示。

### III. 凭据与本地状态隔离
Token仅供后端使用，不输出、不入Git、不进前端。异常跟进只写当前项目SQLite，以exception_id为键。只在当前仓库工作，学员不得读取相邻完成版。

### IV. 小范围实现与可核对结果
课堂先实现P1任务，P2扩展另行安排。复用已有连接和校验，不新增无必要依赖。必要测试对应业务规则，分别报告离线检查、实时查询、页面验证与远程CI。

### V. 保留教学检查点
起始项目的TODO必须由学员实现；完成版用于讲师展示和结果复盘。预置文档不表示Copilot已经在课堂运行，任务勾选不表示实时环境已通过。

## Technical Constraints
Python 3.12、各项目独立uv环境、原生HTML/CSS/JavaScript。应用只在本地运行。CI仅离线检查；提交、推送、PR和发布需要用户另行安排。

## Workflow
项目原则课前准备一次。每个功能按specify、clarify（需要时）、plan、tasks、implement和converge推进。技能在Copilot聊天中逐步调用，CLI只负责项目设置与元数据检查。

## Governance
本文件记录项目原则，AGENTS.md负责Agent操作入口。平台权限、测试和人工审阅共同约束结果。修改这些教学约定时同步Spec、计划、任务、运行说明和课件。

**Version**: 1.0.0 | **Ratified**: 2026-11-09 | **Last Amended**: 2026-11-09
