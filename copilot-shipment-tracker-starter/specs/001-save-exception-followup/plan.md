# Implementation Plan: 异常跟进本机保存与重读确认

**Branch**: `main`（实际 Git 分支，未切换） | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-save-exception-followup/spec.md`

**Feature identifier**: `001-save-exception-followup`。setup-plan 输出的 BRANCH 为该功能标识；实际 Git 分支经核对为 main，二者独立。

**Stage**: 本轮完成 Phase 0 研究与 Phase 1 设计，不创建 tasks.md，不实现应用，不提交或推送。

## Summary

补齐 FollowUpStore.save 与原生页面提交处理。复用 Tracker 的源记录读取、已有规则校验、事务连接及 overlay，以 exception_id 为键保存本机状态、规范化备注和 UTC 保存时间。用 SQLite BEGIN IMMEDIATE 将本机当前状态读取、expected_status 核对和参数化写入置于同一事务；提交成功后重新读取合并记录返回。页面 POST 后 GET 同一异常并匹配编号、状态及规范化备注，匹配后才成功；处理中禁重入，明确反馈写入失败和已提交未确认。

代码核对发现 FR-010 所需的源更新时间尚未由现有查询投影返回。设计包含 services/queries.py 的最小只读字段增补及 app.js 现有 source-state 文本展示，不改变关联、过滤、分页、MCP 连接或解析链路。其余已有行为保持。分后端和前端两个实施范围，均待用户后续逐阶段调用。

## Technical Context

**Language/Version**: Python 3.12；原生 JavaScript、HTML、CSS；Node.js 22 用于语法及可选内置测试运行。

**Primary Dependencies**: 保持 mcp>=1.28,<2、httpx>=0.28,<1、json5>=0.12,<1；HTTP 服务和 SQLite 使用标准库，不新增依赖。

**Storage**: 当前项目 SQLite followups 表，默认 data/followups.sqlite3，可用 --db 选择；沿用既有表结构，不迁移。Databricks 仅为只读源。

**Testing**: 现有 unittest、tools/check_training.py、compileall、node --check；新增聚焦保存行为和提交确认的离线用例，不访问真实 MCP。前端用 Node 内置 node:test 与 vm、最小 DOM/fetch 替身验证请求顺序及错误分支，不引入 npm 工具链；真实页面另行验收。

**Target Platform**: Windows 本机运行，127.0.0.1:8769，现代浏览器；每个项目独立 uv.lock 与 .venv。

**Project Type**: 本机 Python HTTP 服务与原生前端。

**Performance Goals**: 每次点击流程最多一次 POST，成功提交后一次详情 GET；不新增全量查询来确认单条结果。保留 SQLite 5 秒连接等待和现有 MCP 轮询策略，不增加未经需求支持的吞吐或延迟指标。

**Constraints**: 仅 execute_sql_read_only / poll_sql_result；Token 留在后端；事务失败无部分写入；原状态比较；不读相邻应用、备份或历史；不新增部署、认证或存储依赖。

**Scale/Scope**: 沿用现有最多 500 条异常的查询保护、10 条分页；按异常独立保存。原状态相同的并发备注不承诺版本冲突检测。源查询不可用时不提供离线业务队列。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 宪章门禁 | Phase 0 前 | Phase 1 后设计复核 |
| --- | --- | --- |
| 在已有应用上新增功能，逐阶段形成产物 | 通过：活动 spec 已存在 | 通过：只生成计划与设计，不生成任务或实现 |
| 源只读，本机按异常编号保存 | 通过：已有只读查询与 overlay | 通过：仅写 followups；源时间只读投影，不改变源值 |
| 规则、原状态、原子保存与重读确认 | 通过：规则与错误映射已提供 | 通过：写事务内比较并校验；POST 后独立 GET；失败不误报成功 |
| 小范围修改，独立环境与现有依赖 | 通过：仅查看当前应用 | 通过：两处主要补齐、必要源时间字段和测试，无新依赖或读取链路重写 |
| 凭据与验收证据 | 通过：未读取本机凭据配置 | 通过：假数据仅测试；离线、实时 MCP、页面及重启分别记录；不提交或部署 |

结论：设计前后均通过，无需宪章例外。源 updated_at 的实际类型及可用权限在后续实时只读验收核对，不将文档约定当作本次查询证据。

## Project Structure

### Documentation (this feature)

```text
specs/001-save-exception-followup/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── followups.md
└── checklists/
    └── requirements.md
```

后续 tasks.md 仅由用户调用 /speckit-tasks 后生成。

### Source Code (repository root)

```text
app.py                      复用 HTTP 路由与错误映射
services/
├── store.py                主要修改：save
├── tracker.py              复用源读取、update、detail 与 list
├── queries.py              必要增补：只读源更新时间字段
├── mcp_sql.py              复用，不重写
└── settings.py             复用，不读取凭据内容
static/
├── app.js                  主要修改：submit、必要确认交互及源时间文本
├── index.html              沿用布局与控件
└── style.css               沿用
tests/
├── test_preflight.py       已有规则检查
├── test_training_state.py  已有阶段检查
├── test_store.py           拟新增：保存、冲突、回滚及重开恢复
├── test_followup_api.py    拟新增：使用假源的本机 HTTP 契约
└── test_followup_submit.js 拟新增：提交确认流程，无新增依赖
```

**Structure Decision**: 保持当前单应用结构，不创建 backend/frontend 新工程。文档中的新增测试文件是后续任务建议，本阶段不创建测试或应用实现。

后端实施范围：store.save、必要只读时间投影与后端测试。前端实施范围：提交快照、POST/GET 确认、失败分支、防重复、确认后列表更新，以及必要的手动重读确认上下文；源时间在现有文本区域展示。实施时同步修正 README 中已不再准确的练习未完成说明，不扩大页面重构。

## Complexity Tracking

无宪章违规或需批准的额外复杂度；不引入 ORM、迁移、框架、版本表或新 MCP 连接。

## Design Deliverables and Validation

- [研究决策](research.md)：事务、返回结构、确认语义、现有缺口与测试边界。
- [数据模型](data-model.md)：既有表、有效状态及时间来源。
- [交互契约](contracts/followups.md)：沿用 HTTP 接口与页面状态机。
- [验收指南](quickstart.md)：离线命令及真实源、页面、重启场景。

本次通过源码和规格核对完成设计，无遗留待澄清项。未执行应用离线测试、实时 MCP、页面或重启验收，未生成任务。文档结构核对不代表业务功能通过。
