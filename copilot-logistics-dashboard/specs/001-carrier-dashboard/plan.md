# Implementation Plan: 物流承运商Dashboard

**Branch**: `main` | **Date**: 2026-11-09 | **Spec**: [spec.md](spec.md)
**Input**: 本功能spec.md和项目constitution；当前目录为讲师完成版。

## Summary
复用只读MCP连接，完成指标、承运商筛选和对比图；P2趋势与分页另行安排。

## Technical Context
**Language/Version**: Python 3.12、原生HTML/CSS/JavaScript。
**Primary Dependencies**: 现有uv.lock中的mcp、httpx与json5，不新增运行依赖。
**Storage**: Databricks为业务源；本地不持久化运输业务数据。
**Testing**: unittest离线测试、node --check；实际MCP与浏览器验收独立记录。
**Target Platform**: Windows本地，127.0.0.1，端口8766。
**Project Type**: 本地Python HTTP服务和原生前端。
**Performance Goals**: 课堂500单/169异常规模；不承诺生产性能SLA。
**Constraints**: 单项目独立uv环境、只读MCP、凭据仅后端、本地运行；P1约15分钟。
**Scale/Scope**: P1指标与筛选；P2趋势和分页。

## Constitution Check
| 原则 | 实施约束 | 设计复核 |
|---|---|---|
| 规格先行 | FR对应任务与验收 | 通过：见tasks.md映射 |
| 真实只读来源 | 复用execute_sql_read_only与轮询 | 通过：不引入写源表步骤 |
| 凭据与状态隔离 | Token后端、不落地业务数据 | 通过：边界不扩大 |
| 小范围实现 | P1先行，必要测试 | 通过：不增加运行依赖 |
| 教学检查点 | 起始未完成，完成版复盘 | 通过：不声称已在Copilot课堂执行 |

以上为设计约束复核，不表示实时业务验收通过。

## Project Structure
```text
specs/001-carrier-dashboard/
  spec.md  plan.md  tasks.md  acceptance.md
  research.md  data-model.md  quickstart.md  contracts/api.md
.specify/memory/constitution.md
app.py
services/  static/  tests/  tools/
```
**Structure Decision**: 沿用现有独立项目，不建立根uv工作区，不读取相邻完成版。

## Implementation Steps
1. 在services/queries.py组织固定只读SQL与筛选参数；核对口径。
2. 在services/dashboard.py复用mcp_sql，整理并校验真实结果。
3. 在static/index.html、app.js、style.css实现指标、筛选和对比图。
4. 覆盖指标边界和失败反馈；P2任务按明确范围另行实现。

## Complexity Tracking
无新增架构或依赖例外。实时连接依赖个人授权与可用计算，离线测试不能替代。
