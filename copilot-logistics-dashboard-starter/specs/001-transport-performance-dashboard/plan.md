# Implementation Plan: 运输表现看板

**Branch**: `main`（实际 Git 分支） | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-transport-performance-dashboard/spec.md`

**Note**: setup-plan 返回的 BRANCH 为活动功能标识 `001-transport-performance-dashboard`；功能目录独立于 Git 分支。本阶段不创建或切换分支。

## Summary

沿用当前 Python HTTP 服务、现有只读 MCP 连接与原生前端，实现按承运商分析的运输表现看板。P1 后端与前端分轮：先实现参数校验、只读聚合查询和结果校验，再实现四指标、筛选、对比和状态反馈。P2 单列为后续扩展，增加连续日期趋势、查询侧 20 条分页及时间说明。

每次请求生成一个只读查询，返回一行一列 `dashboard_json`；复用已有 `extract_dashboard`，P1 保留 `daily`、`shipments` 空数组。源运输单先形成有效/准时标记再汇总；承运商名称在统计后关联，避免重复放大。不关联异常表。前端仅请求本地 `/api/dashboard`，不能持有 Token 或采用聊天导出数据。

## Technical Context

**Language/Version**: Python 3.12；原生 HTML/CSS/JavaScript，无前端构建框架。

**Primary Dependencies**: 保持 pyproject.toml 和 uv.lock：mcp>=1.28,<2、httpx>=0.28,<1、json5>=0.12,<1；标准库 http.server、asyncio、unittest。不新增依赖。

**Storage**: 配置的 Databricks Catalog/Schema 下 shipments、carriers，只读访问；不建立本地业务数据库或业务缓存文件。

**Testing**: unittest 覆盖业务边界、参数和服务/HTTP 合同，沿用既有课堂状态测试；node --check 检查 JS；浏览器验证筛选、各状态和桌面/窄屏。业务测试在实现阶段执行。

**Target Platform**: Windows、本项目独立 uv 环境；服务绑定 127.0.0.1:8767，浏览器同源访问。

**Project Type**: 本地 Web 看板，Python 后端与静态前端。

**Performance Goals**: P1 只返回汇总与承运商数组；P2 每次最多 20 条明细，趋势大小由日期跨度决定。发起请求即显示加载；不承诺未经测量的业务查询响应时间，页面信息支持 SC-004 的 30 秒阅读任务。

**Constraints**: 复用 settings.py、mcp_sql.py；仅调用 execute_sql_read_only、poll_sql_result；失败报错、凭据仅后端；不读取实际凭据。沿用 execute_read_only 的 90 秒轮询预算及 HTTP 120 秒读取超时；预算在工具调用返回后检查，不宣称严格 90 秒端到端期限；不增加无限自动重试。

**Scale/Scope**: 单课堂本地使用。2026-11-16 核对 shipments 为 500 单且编号唯一，不作为容量上限或固定结果。P1 故事 1—3，P2 故事 4—5；本命令止于 Phase 1 设计，不生成任务或业务实现。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原则与门禁 | Phase 0 前 | Phase 1 后 | 设计依据 |
| --- | --- | --- | --- |
| 先规格再实现、每阶段独立 | PASS | PASS | 已核对活动 spec；本次只产出方案与设计，任务由下一命令生成 |
| 源数据只读、失败不兜底 | PASS | PASS | 单次只读聚合，复用 execute_read_only/extract_dashboard；失败不返回固定业务值 |
| 项目独立、技术与凭据边界 | PASS | PASS | 仅阅读当前项目；保留 Python 3.12/uv 和原生前端；无新增依赖、无凭据输出 |
| P1 优先、P2 单列 | PASS | PASS | 后端 P1、前端 P1 分轮；P2 字段和接口语义提前约定但不要求 P1 实现 |
| 执行证据验收 | PASS | PASS | quickstart 区分离线、运行时连接、真实查询与浏览器验证；本阶段不声称业务完成 |

无原则冲突或需豁免项。

## Project Structure

### Documentation (this feature)

```text
specs/001-transport-performance-dashboard/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── dashboard-api.md
└── checklists/
    └── requirements.md
```

下一阶段单独生成 tasks.md，本阶段不创建。

### Source Code (current application root)

```text
app.py                     HTTP 路由与参数错误/数据错误映射
services/
├── settings.py            复用配置与标识符验证
├── mcp_sql.py             复用连接、只读执行、轮询与单元格提取
├── queries.py             待实现：参数验证、只读 SQL 组装
└── dashboard.py           待实现：同步入口桥接异步 MCP、合同验证
static/
├── index.html             待实现：看板结构、控件、状态区域
├── style.css              待实现：效果稿风格及响应式布局
└── app.js                 待实现：同源请求、渲染、最新请求保护
tests/
├── test_training_state.py  保留已有课堂阶段测试
├── test_queries.py         拟新增：业务查询与输入边界
├── test_dashboard.py       拟新增：只读编排、结果校验和错误
└── test_app.py             拟新增：HTTP 参数与响应合同
```

**Structure Decision**: 不引入新框架或通用仓储层；在现有练习入口填充业务。测试文件为下一阶段候选落点，实际任务由 tasks 确定。文档内路径均相对当前应用。

## Phase 0: Research

[research.md](research.md) 记录连接合同、聚合策略、参数规则、结果状态、P2 分页及时间处理。研究依据为当前应用骨架与只读源表结构，不调用相邻完成版或历史答案。所有技术未知项已有明确决策，无待澄清项。

## Phase 1: Design & Contracts

- [data-model.md](data-model.md)：源实体、派生指标、不变量、筛选与界面状态转移。
- [contracts/dashboard-api.md](contracts/dashboard-api.md)：GET 参数、成功结构、失败状态及 P1/P2 边界。
- [quickstart.md](quickstart.md)：实现后的启动、离线与实时核验、页面验收步骤及本阶段证据。

### 实施轮次与验收交接

1. **P1 后端**：queries.py 校验筛选/页码并组装查询；dashboard.py 复用 MCP 并验证结果；app.py 补必要错误映射与参数约束。运输单先派生计数，汇总后关联唯一承运商名称；同次查询返回全局选项与范围内对比。验证 SC-001、HTTP 合同、只读调用、拒绝截断和失败行为。
2. **P1 前端**：index.html/style.css/app.js 使用真实 API，完成四指标、口径、筛选、清除、刷新、对比、加载/空/错误与重试；以请求序号配合 AbortController 防止旧响应覆盖。验证 SC-002—SC-004，桌面与窄屏可操作。只参考效果稿布局，不导入固定样例。
3. **P2 扩展**：查询增加自然日补零、数据库侧分页与最新源快照；后端附成功查询完成时间，前端渲染趋势、明细、分页与上海时间说明。验证 SC-005—SC-007；同一范围聚合与明细同次生成，跨请求不保证冻结源快照。

以上为规划分轮，不是任务清单或实施授权；每轮开始前须按用户指定任务列出任务 ID、拟改文件和验收方式。

## Complexity Tracking

无原则豁免，不新增依赖、持久化层或部署组件。保留现有单接口与单行 JSON 约定，降低课堂连接和结果拆包成本。
