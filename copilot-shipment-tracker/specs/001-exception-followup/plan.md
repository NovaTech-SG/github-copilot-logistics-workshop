# Implementation Plan: 运输异常跟进

**Branch**: `main` | **Date**: 2026-11-09 | **Spec**: [spec.md](spec.md)
**Input**: 本功能spec.md和项目constitution；当前目录为参考完成版，用于方案与效果对照。

## Summary
复用只读数据和校验，完成本机SQLite保存及前端提交后重新读取。

## Technical Context
**Language/Version**: Python 3.12、原生HTML/CSS/JavaScript。
**Primary Dependencies**: 现有uv.lock中的mcp、httpx与json5，不新增运行依赖。
**Storage**: Databricks源只读；本项目SQLite保存独立的exception_id跟进记录。
**Testing**: unittest离线测试、node --check；实际MCP与浏览器验收独立记录。
**Target Platform**: Windows本地，127.0.0.1，端口8768。
**Project Type**: 本地Python HTTP服务和原生前端。
**Performance Goals**: 课堂500单/169异常规模；不承诺生产性能SLA。
**Constraints**: 单项目独立uv环境、只读MCP、凭据仅后端、本地运行；P1约15分钟。
**Scale/Scope**: 只完成save与submit及必要验证，不重构源读取。

## Constitution Check
| 项目原则 | 本方案的约束 |
|---|---|
| 规格先行 | 需求对应任务与验收，业务规则变化先更新规格。 |
| 真实只读来源 | 复用只读 MCP 与轮询，不写 Databricks 源表。 |
| 凭据与本地状态 | Token 仅后端使用；只保存本项目的 SQLite 跟进记录。 |
| 小范围实现 | 先完成本次 P1，按需求补充必要验证。 |
| 教学检查点 | 区分起始项目与参考完成版，按实际执行记录进度。 |

这些约束需要在实现与验收时核对，具体结果填写到 README.md 的验收清单。

## Project Structure
```text
specs/001-exception-followup/
  spec.md  plan.md  tasks.md  acceptance.md
  research.md  data-model.md  quickstart.md  contracts/api.md
.specify/memory/constitution.md
app.py
services/  static/  tests/  tools/
```
**Structure Decision**: 沿用现有独立项目，不建立根uv工作区，不读取相邻完成版。

## Implementation Steps
1. 在services/store.py的save中核对原状态、复用校验并参数化写入。
2. 使用既有事务，失败回滚，提交后overlay读取确认。
3. static/app.js的submit在POST后GET同一异常，再更新页面。
4. 补保存恢复、空备注、非法流转和过期提交检查。

## Complexity Tracking
无新增架构或依赖例外。实时连接依赖个人授权与可用计算，离线测试不能替代。
