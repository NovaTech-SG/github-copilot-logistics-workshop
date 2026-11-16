---
description: "异常跟进本机保存与重读确认的分阶段实施任务"
---

# Tasks: 异常跟进本机保存与重读确认

**Input**: 当前功能目录下的 [spec.md](spec.md)、[plan.md](plan.md)、[research.md](research.md)、[data-model.md](data-model.md)、[contracts/followups.md](contracts/followups.md) 和 [quickstart.md](quickstart.md)。

**Prerequisites**: 活动功能为 specs/001-save-exception-followup；实际分支 main，目录与分支独立；已按用户指令执行 analyze。本次 implement 经用户明确选择同时实现后端与前端并完成可执行验收；完成证据见 [quickstart.md](quickstart.md)。

**Tests**: 规格验收及已批准阶段计划要求必要测试，故包含聚焦保存、HTTP 和页面确认的用例。先补用例，再实现相应新增行为；新增行为的用例应能在起始版失败。已提供或由前序任务实现的能力可直接通过，不为制造失败重写基础代码。

**Organization**: 先 US1（P1），再同为 P1 的 US3，最后 US2（P2）；保留规格故事编号。后续按用户要求分后端、前端实施，不自动跑完整清单。

## Format: `[ID] [P?] [Story] Description`

- 每个任务都有唯一连续 T 编号、未完成框和明确项目相对文件路径。
- [P] 表示前置完成后，与同阶段其他不同文件任务可并行；不表示可以跳过前置或同时编辑同一文件。
- [US1] / [US2] / [US3] 对应规格故事；Setup、Foundational 和收尾不标故事。

## Path Conventions

所有代码路径均相对当前 starter 应用根目录；不读取父目录、相邻完成版、备份或 Git 历史。仅在本应用独立 uv 环境工作，保留现有依赖、表结构与读取链路。源数据只能通过既有 execute_sql_read_only / poll_sql_result 读取，SQLite 只保存本机跟进。

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 确认当前活动功能与工作边界，不重复初始化已有工程。

- [X] T001 核对 .specify/feature.json 指向本功能，阅读 AGENTS.md、.specify/memory/constitution.md、docs/data-source.md、docs/prompts.md、mockup/README.md、mockup/index.html 和本功能设计文档；检查当前项目 diff，保留已有本机配置改动，不输出凭据，不重新初始化环境或安装无缺失依赖。

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 确认共用能力及约束后再补保存，避免重复建设。

- [X] T002 对照 specs/001-save-exception-followup/contracts/followups.md 核对 app.py 的路由与错误映射、services/tracker.py 的源读取、services/store.py 的 connect/overlay/validate_change 以及 static/app.js 的 busy 和替换记录流程；确认复用边界，并将必要的行为用例分配到 tests/test_store.py、tests/test_followup_api.py、tests/test_followup_submit.js，不新建表、框架或共享夹具模块。

**Checkpoint**: 只确认既有基础；无需新增模型、MCP 连接、鉴权或迁移。T002 依赖 T001，所有故事任务依赖 T002。

## Phase 3: User Story 1 - 保存单条异常并确认结果 (Priority: P1)

**Goal**: 单条异常保存后独立重读，确认真实结果；阻止重复提交并区分失败与尚未确认。

**Independent Test**: 使用临时库与假源或后续真实页面，完成 OPEN → IN_PROGRESS、IN_PROGRESS → RESOLVED，以及三个合法状态下同状态备注更新；仅在同编号 GET 的状态和规范化备注匹配后成功。注入重读失败或不匹配时不得显示成功。

### Tests for User Story 1

- [X] T003 [P] [US1] 在 tests/test_store.py 增加临时库保存行为用例：首次插入、两种逐级推进、三个状态的同状态备注更新、去首尾空格、UTC 保存时间及完整合并返回；按 data-model.md 核对 exception_id 的“PRIMARY KEY；仅对已读取到的源异常写入”、handling_status 的“NOT NULL；既有 CHECK 限定三种状态”、updated_at 的“NOT NULL；本次合法保存的 UTC ISO 8601 时间”，同时断言源字典未变，清理临时库。
- [X] T004 [P] [US1] 在 tests/test_followup_api.py 用假 reader、临时库及本机临时端口覆盖 POST 成功后独立 GET 同一异常，核对 saved_to、完整 record、source_handling_status、local_updated_at 和规范化备注；将 follow_up_note 的“NOT NULL；validate_change 执行 strip 后必填、最多 1000 个 Python 字符”作为行为断言，测试结束关闭服务和线程，不使用真实 MCP。
- [X] T005 [P] [US1] 在 tests/test_followup_submit.js 使用 node:test、vm 和最小 DOM/fetch 替身覆盖 POST → GET 时序、携带原状态与 trim 后备注、编号/状态/备注分别不匹配、POST 拒绝、结果未知、POST 成功但 GET 失败、连续三次提交只发一次 POST 以及各分支恢复控件；不得用字符串源码匹配替代行为验证。

### Implementation for User Story 1

- [X] T006 [US1] 补齐 services/store.py 的 save：沿用 connect，BEGIN IMMEDIATE 后在同连接按 exception_id 读取本机状态，缺记录则取传入源状态；校验 expected_status 并复用 validate_change，通过参数化 upsert 一次写入状态、备注和 UTC 时间，退出事务成功后用 overlay 重新读取返回；同步包含不可拆开的原状态拒绝及回滚保障，不先发布缺校验的保存；运行 tests/test_store.py 和 tests/test_followup_api.py 的聚焦 unittest 验证。
- [X] T007 [US1] 补齐 static/app.js 的 submit：入口捕获异常编号、目标状态、规范化备注和原状态，立即 setBusy(true)，POST 成功后 GET 捕获编号，匹配三项后 replaceRecord 并设置成功提示；不把 POST 输入或响应替代独立 GET，不额外全量查询，失败保留必要草稿；同时给 api 错误保留 HTTP 状态，区分明确拒绝与提交结果未知，避免 US1 依赖后置错误分类；finally 恢复控件，保持现有筛选分页和布局。
- [X] T008 [US1] 在 static/app.js 增加轻量待确认上下文并最小调整 read-record/selectRecord：手动重读同一异常时核对原提交，一致才确认，不一致或失败继续说明未确认；无上下文只显示读取完成，切换异常或新提交废弃旧上下文，replaceRecord 清空提示后须重设最终反馈；在 tests/test_followup_submit.js 补手动恢复、切换及迟到响应用例。
- [X] T009 [US1] 运行 tests/test_followup_submit.js 的 node --test 和 static/app.js 的 node --check，核对已确认单条记录触发列表、概览、状态筛选和分页重算，未确认结果不被伪造；在 specs/001-save-exception-followup/quickstart.md 记录本轮实际前端测试命令和结果，不将替身测试写成真实页面验收。

**Checkpoint**: US1 的完整交互可独立验收。T006 同时实现保存必需的 US3 核心规则；US3 后续增强拒绝与原子性证据，不再另建保存方法。

## Phase 4: User Story 3 - 拒绝无效或过期跟进且保持异常独立 (Priority: P1)

**Goal**: 旧状态、无效备注与非法推进不能破坏记录；同单其他异常及源记录保持独立。

**Independent Test**: 用预置异常和临时库提交八类拒绝输入，对比保存前后状态、备注、时间及同单其他异常；注入事务失败，首次保存无残留、已有记录完整保留。

### Tests for User Story 3

- [X] T010 [P] [US3] 扩展 tests/test_store.py：覆盖空白、1001 字、跳级、退回、未知状态、缺失或无效 expected_status、有效但过期原状态，及 1/1000 字可保存；覆盖无本机记录时采用源状态、有记录时采用本机状态、同单异常隔离与源对象不变；通过临时触发器等可控故障验证插入/更新回滚，使用两个连接验证并行推进后旧状态不能覆盖，不要求同状态备注版本冲突检测。
- [X] T011 [P] [US3] 扩展 tests/test_followup_api.py：按 contracts/followups.md 验证编号的“单条异常唯一标识；接口沿用 1–64 位字母、数字、下划线或连字符校验”、请求体 1–16384 字节、无效状态/备注/原状态返回 400、不存在异常 404、过期 409、本机故障 500、源读取失败 502，并验证拒绝后本机内容不变，错误不含测试用凭据且无模拟业务数据兜底。
- [X] T012 [P] [US3] 扩展 tests/test_followup_submit.js：覆盖 400/404/409 明确拒绝、500 可能提交后读取失败、网络中断及响应解析失败的结果未知；验证不自动重复 POST、不宣称确定未写入，冲突后手动重读更新原状态，失败保留草稿且控件恢复。

### Implementation and Verification for User Story 3

- [X] T013 [US3] 基于 T007 已完成的错误分类，在 static/app.js 按 T012 扩展用例核对并完善恢复反馈：400/404/409 等明确拒绝展示原因；500 或运输/解析异常不武断判断写入结果；已收到 POST 成功而 GET 失败显示“已提交但尚未确认”；仅调整错误元信息及相关反馈，不改变已有 GET、加载与筛选行为。
- [X] T014 [US3] 运行 tests/test_store.py、tests/test_followup_api.py 聚焦测试，核对 services/store.py 的过期比较和状态/备注/时间一起回滚；若新用例发现紧耦合缺口，仅在该保存逻辑内修正；在 specs/001-save-exception-followup/quickstart.md 记录后端结果和未验证项，不因覆盖率重写规则或查询链路。
- [X] T015 [US3] 运行 tests/test_followup_submit.js 与 static/app.js 语法检查，验证 T012/T013 的错误分类、冲突恢复及最终提示；在 specs/001-save-exception-followup/quickstart.md 如实记录前端证据，不将本机 HTTP 假源等同实时 MCP。

**Checkpoint**: US3 拒绝及失败原子性证据完整。原状态并发边界保持规格约定，无新增版本号、历史表或锁服务。

## Phase 5: User Story 2 - 刷新和同库重启后继续跟进 (Priority: P2)

**Goal**: 刷新与同库重启保留结果；队列采用合并状态并区分源、本机时间。

**Independent Test**: 对同一临时数据库关闭并重建 store/tracker，详情与列表结果保留；后续真实服务刷新及同库重启再次核对。使用另一文件时没有旧本机记录，源状态和空源更新时间正确显示。

### Tests for User Story 2

- [X] T016 [P] [US2] 扩展 tests/test_store.py 覆盖关闭连接后使用同一路径重建 FollowUpStore/Tracker，状态、备注和 local_updated_at 保留；对同单两条异常核对列表合并结果，换新库回到源值；包含源 updated_at 只读投影的“空值允许”，无本机记录的 local_updated_at 为 null，source.queried_at 不冒充源更新时间。

### Implementation for User Story 2

- [X] T017 [US2] 在 services/queries.py 的既有只读投影和 JSON 行中最小加入 unix_timestamp(e.updated_at) AS source_updated_epoch，不改变关联、筛选、排序、500 条完整性保护或 MCP 路径；在 tests/test_preflight.py 补字段经现有 extract_records 与 overlay 后保持源时间、空值及本机状态区别的行为用例，不以 SQL 字符串常量断言替代行为验证。
- [X] T018 [US2] 在 static/app.js 的现有 source-state 文本展示源状态与 source_updated_epoch，沿用上海时间格式，空值显示“—”，本机时间仍取 local_updated_at；不改 static/index.html 布局，不用查询完成时间代替源更新时间，保留没有本机记录时的源结果。
- [X] T019 [US2] 在 tests/test_followup_submit.js 覆盖重新加载已有保存记录、同单另一异常不变、合并状态概览/筛选/分页以及源时间为空的显示；使用假响应测试现有 load/renderList，不新增读取链路，验证待确认提示不会在新页面假恢复。
- [X] T020 [US2] 运行 tests/test_store.py、tests/test_preflight.py 和 tests/test_followup_submit.js 的聚焦验证及 static/app.js 语法检查，在 specs/001-save-exception-followup/quickstart.md 记录重开临时库和页面替身结果，明确其不能证明真实服务同库重启；只修复上述范围内的实际回归。

**Checkpoint**: US2 的离线恢复与展示行为通过；实时源时间类型、真实页面及服务重启仍分别验收。

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 同步直接相关说明并收集真实证据，不自动提交、推送或部署。

- [X] T021 更新 README.md 与 specs/001-save-exception-followup/quickstart.md 中已过时的保存 501/未完成说明及测试命令，使其符合实际完成范围；若只完成后端须继续标明前端未完成，避免提前宣称功能整体可用，保持原有安装和 MCP 配置流程。
- [X] T022 按 README.md 执行 tools/check_training.py、完整 tests 的 unittest、app.py/services/tools 的 compileall、static/app.js 的 node --check 及 tests/test_followup_submit.js 的 node --test；在 specs/001-save-exception-followup/quickstart.md 分别记录退出码和未验证项，审阅项目 diff，确认无凭据或本机数据库加入产物且无读取链路回归。
- [X] T023 按 specs/001-save-exception-followup/quickstart.md 仅用只读 MCP 核对实际 Catalog/Schema、三表与 exceptions.updated_at 类型，再用 app.py --check 核对独立 Python 运行连接；在该 quickstart.md 分开记录两条连接的真实结果或阻塞原因，不以静态 169/40/69/60 或聊天查询冒充运行查询，不输出 Token。
- [X] T024 按 specs/001-save-exception-followup/quickstart.md 在安全配置的本机服务和明确练习库中，使用 static/app.js 对应真实页面验收 POST 后 GET、三项匹配、重复点击、正常失败/冲突恢复、刷新及同单异常隔离，在该 quickstart.md 记录实际编号与观察；未执行分支明确记未验证，不用 mockup 结果替代。
- [X] T025 按 specs/001-save-exception-followup/quickstart.md 正常停止自己启动的 app.py 服务，用完全相同 --db 文件重启，核对状态、备注、本机时间、源区别及概览并记录前后结果；保留本机库，清理仅用于测试的临时资源，不影响其他进程，不提交推送或部署。

## Dependencies & Execution Order

### Phase Dependencies

- T001 → T002 → 故事工作。
- US1 与 US3 都为 P1，先完成共享保存和确认能力，再收齐规则及失败证据；US2 为 P2。
- 同一文件跨故事的任务必须串行。后端和前端分别实施时，允许完成本轮授权的任务后停下，不等待未授权范围。
- 收尾文档按实际完成范围更新；完整验收在全部必要代码和离线测试通过后进行。真实 MCP 不可用时如实记录阻塞，不能勾选未完成的实时验收任务。

### Task Dependencies

下表未重复列出的故事任务均依赖 T002；逗号表示所有列出的前置均须完成。

| 任务 | 直接前置 |
| --- | --- |
| T002 | T001 |
| T003、T004、T005 | T002 |
| T006 | T003、T004 |
| T007 | T005、T006 |
| T008 | T007 |
| T009 | T008 |
| T010 | T006 |
| T011 | T006 |
| T012 | T009 |
| T013 | T012 |
| T014 | T010、T011 |
| T015 | T013 |
| T016 | T014 |
| T017 | T014 |
| T018 | T015、T017 |
| T019 | T018 |
| T020 | T016、T017、T019 |
| T021 | T020 |
| T022 | T021 |
| T023 | T022 |
| T024 | T023 |
| T025 | T024 |

US2 的数据恢复测试可独立使用预置记录，不依赖前端保存操作；表中前置表示本项目共享文件的安全实施顺序。US3 拒绝测试可直接使用假源和预置库，不依赖 US2 的源时间展示。

### User Story Completion Graph

```text
T001 → T002
          ├─ US1 后端保存 → US3 后端拒绝与原子性 → US2 重开库/源时间投影
          └─ US1 前端确认 → US3 前端错误恢复 ───┬→ US2 时间与合并展示
                                             └→ US2 验证
全部必要实现与离线验证 → 文档同步 → 全套离线 → 真实 MCP → 页面 → 同库重启
```

### Within Each User Story

- 优先补对应行为用例，再补最小实现；不复制成品答案，不重写已提供能力。
- 后端原状态比较、规则校验与回滚是保存的不可拆分条件，在 T006 一次完成；US3 提供更完整边界证据。
- 使用现有 app.py 路由与错误映射，不为通过测试增加新接口。
- 某范围完成后只勾选已实现且验证的任务；部分验证不能将整项勾选完成。

## Parallel Examples

### User Story 1

T002 后可并行编写 T003（tests/test_store.py）、T004（tests/test_followup_api.py）、T005（tests/test_followup_submit.js）；它们不同文件且各自使用独立替身与临时资源。T006 等待后端用例，T007 等待已可用后端和前端用例。

### User Story 3

前置满足后，T010（tests/test_store.py）与 T011（tests/test_followup_api.py）可并行；T012（tests/test_followup_submit.js）也可在 T009 后独立进行。不得同时运行改写同一测试文件的跨故事任务。

### User Story 2

T014 后，T016（tests/test_store.py）可与 T017（services/queries.py 和 tests/test_preflight.py）并行。T018/T019 涉及前端及其测试，等待前端前置和源字段投影完成后串行。没有为制造并行而拆出无依赖的模型或公共模块。

## Implementation Strategy

### MVP First

最小可审阅范围为 T001–T009：US1 的有效保存、独立重读确认、未确认反馈和防重复；T006 已包含必要校验及事务安全。该范围可作为课堂功能演示，但不能替代 US3 的完整拒绝证据或 US2 的恢复验收，也不能提前宣称全部完成。

### Incremental Delivery and Scoped Calls

- **只实现后端保存与必要测试**：T001、T002、T003、T004、T006、T010、T011、T014、T016、T017；按 T021 原则同步后端完成范围和验证证据，不执行前端任务。
- **只实现前端提交与确认**：在后端接口可用的前提下执行 T005、T007–T009、T012、T013、T015、T018、T019，再汇合 T020；不顺带重写后端或读取链路。
- **收敛与完整验收**：按后续用户指令完成 T021–T025，先离线后实时，逐类保留证据；无凭据或其他阻塞明确记录。

以上范围保留为分阶段调用参考。本次用户已在 implement 范围选择中授权同时实现后端、前端及可执行验收，未改变任务 ID 或故事归属；analyze 已单独完成，不自动调用 converge。

## Notes

- 共 25 项：Setup 1、Foundational 1、US1 7、US3 6、US2 5、收尾 5。
- 2026-11-16 实施及可执行验收完成，T001–T025 已勾选；真实页面未逐一复演的故障分支和重启时环境问题均在 quickstart.md 单独说明。
- 禁止自动提交、推送、发布、部署；不为每个任务创建 Git 提交。
- 规格与设计保留既有内容；实际完成证据记录在 quickstart.md，不新增未经要求的跟踪文档。
