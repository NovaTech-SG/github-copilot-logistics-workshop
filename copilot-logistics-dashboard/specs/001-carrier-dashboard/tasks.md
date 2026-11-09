# Tasks: 物流承运商Dashboard

**Input**: 同目录spec.md、plan.md、research.md、data-model.md和contracts/api.md。
**Organization**: P1为课堂范围，P2是课后扩展。勾选需依据实际执行，不由预置状态推断完成。

## Phase 1: Setup
- [ ] T001 核对README.md中的环境、账号和本目录端口，运行tools/check_training.py。
- [ ] T002 阅读.specify/memory/constitution.md和spec.md，确认P1、分母、N/A和真实数据边界。

## Phase 2: Foundational
- [ ] T003 核对services/settings.py与services/mcp_sql.py已有只读连接，实际查询培训表；不修改读取凭据的边界。
- [ ] T004 阅读contracts/api.md和docs/data-contract.md，核对services/mcp_sql.py解析需要的字段与类型。

## Phase 3: User Story 1 - 指标与承运商筛选 (Priority: P1)
**Goal**: P1指标、筛选、清除和对比图可验证。
**Independent Test**: 全部500/380/304/80.00%，CAR002为134/104/77/74.04%，零分母N/A。
- [ ] T005 [US1] 在tests/test_dashboard.py补指标口径、CAR002、零分母和非法输入检查，对应FR-002到FR-005。
- [ ] T006 [US1] 在services/queries.py实现固定只读查询与筛选参数校验，对应FR-001到FR-005。
- [ ] T007 [US1] 在services/dashboard.py复用MCP调用，等待完成并校验指标与范围，对应FR-001、FR-006、FR-007。
- [ ] T008 [US1] 在static/index.html、static/app.js和static/style.css实现四个指标、筛选与承运商对比图，对应FR-005。
- [ ] T009 [US1] 在static/app.js补加载、空结果、错误和重试反馈，核对凭据不进入页面，对应FR-006、FR-007。
- [ ] T010 [US1] 按quickstart.md运行离线检查并实际核对全部与CAR002，将证据记入docs/validation.md，对应FR-010。

## Phase 4: User Story 2 - 趋势与分页 (Priority: P2)
**Goal**: 课后添加日期趋势和20条一页的运输明细。
**Independent Test**: CAR002七页、末页14条、相邻页无重复；趋势合计等于范围总量。
- [ ] T011 [US2] 在services/queries.py扩展按shipment_date聚合和分页查询，对应FR-008。
- [ ] T012 [US2] 在services/dashboard.py补齐自然日并验证趋势、汇总、明细一致，对应FR-008、FR-009。
- [ ] T013 [US2] 在static/app.js实现趋势、明细分页、筛选复位和时间标注，对应FR-008、FR-009。
- [ ] T014 [US2] 在tests/test_dashboard.py补分页边界和趋势合计检查，在docs/validation.md记录实际验证。

## Phase 5: Polish & Cross-cutting
- [ ] T015 核对README.md、AGENTS.md与活动规格入口一致；运行本项目检查后更新docs/validation.md。

## Dependencies & Execution Order
Phase 1、2先核对，P1按T005到T010执行。P2仅在学员或讲师明确安排时开始。T015在本次范围结束后执行。
P1完成标准不包含P2；运行converge时明确只核对P1，P2待办属于已知扩展。

## Parallel Opportunities
本次P1涉及共同接口，课堂按顺序执行，不强制并行。P2接口确定后，可分别处理tests/test_dashboard.py与static/style.css中的独立调整。

## Implementation Strategy
课前环境就绪。课堂先完成P1，再核对样例与改动。不要在一次implement中自动扩展P2。
