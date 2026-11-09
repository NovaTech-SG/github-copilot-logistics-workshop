# Tasks: 运输异常跟进

**Input**: spec.md、plan.md、data-model.md、contracts/api.md和已有连接、校验、页面结构。
**Organization**: US1与US2均为P1。预置清单不是实现通过证据。

## Phase 1: Setup
- [ ] T001 按README.md准备本目录环境、独立数据库和源数据权限，运行tools/check_training.py。
- [ ] T002 阅读.specify/memory/constitution.md与spec.md，确认只读源、本机保存和异常编号粒度。

## Phase 2: Foundational
- [ ] T003 核对services/store.py已有validate_change、connect与overlay，以及static/app.js已有API辅助方法。
- [ ] T004 按quickstart.md验证读取准备；空本地库169条源异常的分布为40/69/60，记录实际结果。

## Phase 3: User Story 1 - 保存与重新读取 (Priority: P1)
**Goal**: 保存状态与备注，并从服务端重新读取确认。
**Independent Test**: OPEN改IN_PROGRESS，刷新和重启同一数据库后仍保留。
- [ ] T005 [US1] 在tests/test_tracker.py补保存、重新创建Store、另一条异常保持原值等检查，对应FR-004到FR-006。
- [ ] T006 [US1] 完成services/store.py的save：读取当前状态、核对原状态、复用校验、事务内参数化写入，再overlay读取，对应FR-002到FR-007。
- [ ] T007 [US1] 完成static/app.js的submit：POST后GET同一编号，核对状态与备注，区分源与本机，对应FR-001、FR-005。

## Phase 4: User Story 2 - 非法与过期提交 (Priority: P1)
**Goal**: 失败不改变原记录，也不显示成功。
**Independent Test**: 空备注、超长备注、非法流转、过期状态分别拒绝。
- [ ] T008 [US2] 在tests/test_tracker.py补拒绝非法输入、过期原状态与失败无部分写入的检查，对应FR-002、FR-003、FR-007。
- [ ] T009 [US2] 核对services/store.py、app.py既有错误映射；在static/app.js中完成失败、尚未确认与防重复提交反馈，对应FR-005、FR-007、FR-008。
- [ ] T010 [US2] 按quickstart.md实际保存、重新读取、刷新与重启同一数据库；在docs/validation.md记录结果与未验证项，对应FR-009。

## Phase 5: Polish & Cross-cutting
- [ ] T011 检查README.md、AGENTS.md、活动规格、凭据与数据库排除，再运行离线检查。

## Dependencies & Execution Order
先核对Phase 1、2，再完成US1；US2复用US1保存路径，按T008到T010验证错误边界。
P1仅补两处TODO和必要测试，不重构源查询、列表或详情。

## Parallel Opportunities
确认输入输出合同后，可独立编写tests/test_tracker.py与前端错误反馈；课堂保留顺序演示以便理解。

## Implementation Strategy
先做保存与重读，再检查失败场景。PR/CI放在独立收尾环节。不得回写源表或改动相邻项目。
