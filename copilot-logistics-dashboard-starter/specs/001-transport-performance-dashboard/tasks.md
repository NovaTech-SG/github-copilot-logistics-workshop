---
description: "运输表现看板：按用户故事组织的 P1/P2 实施任务"
---

# Tasks: 运输表现看板

**Input**: 当前功能目录的 [spec.md](spec.md)、[plan.md](plan.md)、[research.md](research.md)、[data-model.md](data-model.md)、[接口合同](contracts/dashboard-api.md)、[quickstart.md](quickstart.md)。

**Prerequisites**: 当前活动功能指针指向本目录；遵守 [项目原则](../../.specify/memory/constitution.md) 及当前应用 AGENTS.md；仅当前 starter 项目，无跨项目业务复制。

**Tests**: 按项目原则“测试覆盖本次业务规则”及方案中必要业务/接口测试安排少量针对性用例。不新增测试框架，不测试语言常量或为覆盖率补测试。测试任务先于对应实现；确认为业务缺口导致失败后再实现。无需连接真实源表的测试使用独立构造数据与 MCP 假对象。

**Organization**: US1—US3 为 P1；US4—US5 为 P2。用户故事仍各有独立验收，实施可按下方“后端轮/前端轮”选择不连续任务 ID，不能自动执行 P2。

## Format: `[ID] [P?] [Story] Description`

- 所有执行项为 `- [ ] Tnnn [P?] [USn?] 描述与文件路径`，完成后标记 `[X]`；本次用户已明确授权完整 P1 与 P2，实施状态以勾选及 [实际验收记录](quickstart.md#8-本次完整-p1p2-实现与执行证据2026-11-16) 为准。
- `[P]` 表示在所列前提完成后，可与指定不同文件任务并行；同文件修改串行。
- 故事阶段必须带 `[USn]`；Setup、Foundational、Polish 不带故事标签。
- 所有代码路径相对当前应用根目录；本目录文档路径显式使用 `specs/001-transport-performance-dashboard/`。

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 核对已有骨架与课堂范围，不重新初始化项目或无故安装依赖。

- [X] T001 核对 AGENTS.md、.specify/feature.json、.specify/memory/constitution.md、pyproject.toml、uv.lock 及 specs/001-transport-performance-dashboard/plan.md，确认 Python 3.12、当前项目独立环境、活动功能及本轮范围；实施前在课堂会话列任务 ID、拟改文件和验收方式，不读取实际凭据、不新增根工作区或依赖。

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 固定所有故事共用的输入边界与 HTTP 参数合同。此阶段完成后才开始故事实现。

- [X] T002 在 tests/test_queries.py 增加输入边界用例：空 carrier、合法编号、非法字符/超长、非法 prefix、正整数页码及非法页码；约束原文为“非空符合 ^[A-Za-z0-9_-]{1,64}$；不修剪、不变更大小写”和“十进制数字且 1≤page≤2147483647”；P1 page 只接受 1，不存在的合法编号不在校验层拒绝。
- [X] T003 在 services/queries.py 实现可复用的 prefix/carrier/page 校验，保持 build_query(prefix, carrier="", page=1) 入口；仅允许经验证的反引号 Catalog/Schema 前缀，禁止参数注入 SQL，非法值抛 ValueError，在调用源服务前拒绝；此任务仅建立校验基础，业务查询由 T008 实现。
- [X] T004 在 tests/test_app.py 增加 /api/dashboard 参数合同用例：重复或未知参数、空/负/小数/非数字 page 和 P1 page=2 均为 400 且不调用 fetch；使用假 settings/假 fetch，不使用本机 Token。
- [X] T005 在 app.py 的既有 make_handler 中执行单值参数约束、整数解析和 T003 的校验，保留默认 carrier=""、page=1 及安全 400 响应；保持静态资源服务和现有 127.0.0.1 启动方式，不改为新框架。

**Checkpoint**: 参数错误无需业务源即可明确拒绝；输入相关定向测试通过。

## Phase 3: User Story 1 - 查看整体运输表现 (Priority: P1) — 最小演示增量

**Goal**: 全部范围的四指标、口径与承运商对比可核对。

**Independent Test**: 使用 spec 故事 1 的六单验收集合核对总量 6、有效 3、准时 2、延误 1、排除 3、准时率 66.67%；再核对 1/1 与 1/3 的整体比例为 50.00%，及零分母 N/A。数字仅用于独立测试。

### Tests for User Story 1

- [X] T006 [P] [US1] 在 tests/test_queries.py 为有效/准时分类、相等算准时、缺失判断时间、在途/取消、空集合、整体加权比例及维度不放大建立少量针对性用例；真实 SQL 语义在 T013 通过只读源查询独立核对，不用仅匹配 SQL 字符串证明指标正确。
- [X] T007 [P] [US1] 在 tests/test_dashboard.py 使用构造 MCP 信封验证 get_dashboard 的只读编排与成功合同、空范围、零分母和计数不变量；约束原文为“全部计数为非负整数；on_time_count ≤ eligible_count ≤ total_count”，零分母 on_time_rate 必须为 null；验证只调用 execute_read_only 与 extract_dashboard。

### Implementation for User Story 1

- [X] T008 [US1] 在 services/queries.py 生成单行单列 dashboard_json 的只读聚合查询：运输单先派生有效/准时标记再汇总；“status=DELIVERED 且 planned_arrival、actual_arrival 均非空的单数”为有效，“有效单中 actual_arrival <= planned_arrival 的单数”为准时；按总计数求比例，“四舍五入两位；否则 null”；空集合计数置 0；同查询返回 summary、全局 carriers、按编号有序的 by_carrier，以及 daily=[]、shipments=[]；不读取 exceptions、CSV 或 mockup。
- [X] T009 [US1] 在 services/dashboard.py 实现 get_dashboard 同步入口桥接 asyncio.run，复用 services/settings.py 和 services/mcp_sql.py 的 connect/execute_read_only/extract_dashboard，补 scope 并验证嵌套结构、有限比例和计数恒等式；承运商显示遵守“空值或空字符串时回退编号”，名称映射先唯一化、汇总后关联，避免丢单或重复计数。
- [X] T010 [P] [US1] 在 static/index.html 将起始页替换为四指标、口径、准时/有效/排除数及承运商对比区域，保留原生资源引用和可访问标题；布局参考 mockup/index.html，不复制固定业务数字，不放入 P2 图表或样例明细。
- [X] T011 [P] [US1] 在 static/style.css 实现与效果稿一致的色彩、指标卡及对比条布局、桌面/窄屏适配和焦点样式；源文件仅本应用，名称较长或 N/A 时不挤掉计数。
- [X] T012 [US1] 在 static/app.js 请求本地 /api/dashboard 并一次渲染同响应的范围、四指标、口径和对比，比例始终显示两位百分数，null 为 N/A 且不画成 0% 的有效比例，名称用 textContent；不加入任何运行时固定业务结果。
- [X] T013 [US1] 按 specs/001-transport-performance-dashboard/quickstart.md 对 US1 定向测试、独立只读聚合与页面成功结果逐项核对，并验证成功后 30 秒可读出四指标及关注对象；本轮未包含前端时仅记录后端实际结果，页面验收留待前端轮，不提前勾选本项。

**Checkpoint**: US1 可单独演示总体表现；完整 P1 仍须交付 US2/US3，尤其筛选与失败状态。

## Phase 4: User Story 2 - 筛选、清除与重新查询 (Priority: P1)

**Goal**: 在全部与单个承运商间切换，所有结果范围一致，旧请求不能覆盖新选择。

**Independent Test**: “全部 → 单个承运商 → 重新查询 → 清除”四次成功结果范围一致；控制旧请求晚返回，最终只显示新范围。

### Tests for User Story 2

- [X] T014 [US2] 在 tests/test_queries.py 增加单承运商和不存在的合法编号用例，验证范围统计/对比同步、空结果仍保留全局选项、未匹配名称仍保留编号、未启用承运商不被自动排除及重复维度不放大计数；真实过滤结果由 T019 独立核对。

### Implementation for User Story 2

- [X] T015 [US2] 在 services/queries.py 为 T008 的运输单范围应用经过验证的 carrier 条件，选项采用 carriers 与 shipments 编号并集且不随筛选缩减；遵守“名称缺失不丢单”和“不自动过滤”，按编号稳定排序，不额外过滤日期、区域或 is_active。
- [X] T016 [US2] 在 services/dashboard.py 为当前请求回显 scope.carrier，并检查返回 by_carrier 属于请求范围；保留未知但合法编号的成功空结果，不把空结果转为参数错误；在 tests/test_dashboard.py 添加对应范围合同断言。
- [X] T017 [US2] 在 static/index.html 增加带 label 的单选承运商、清除筛选和重新查询按钮及当前范围标签，选项内容从接口获取，不固定为当前四家承运商。
- [X] T018 [US2] 在 static/app.js 实现选中和清除自动查询、刷新保留选择；用请求序号与 AbortController 共同保护成功、失败及 finally，只有最新请求可更新范围和组件；禁用过时结果提交，不宣称客户端中止会取消后端 SQL。
- [X] T019 [US2] 按 specs/001-transport-performance-dashboard/quickstart.md 核对全部/单个/刷新/清除的接口及页面范围，并用受控延迟验证旧成功和旧失败均不覆盖新请求；记录 SC-002 和 FR-007 的实际结果，离线模拟不替代实际运行查询。

**Checkpoint**: 用户能来回切换并核对同范围数据，选项不随筛选丢失。

## Phase 5: User Story 3 - 加载、空结果、失败与恢复 (Priority: P1)

**Goal**: 明确区分四类请求状态，失败后保持当前范围重试，防止旧值或固定值冒充结果。

**Independent Test**: 触发延迟、成功无记录、源失败及恢复；无记录显示零计数/N/A，失败显示错误，重试只需一次操作且沿用当前范围。

### Tests for User Story 3

- [X] T020 [P] [US3] 在 tests/test_dashboard.py 增加 MCP 连接/权限失败、异常组、轮询失败或超时、截断/分块/无效 JSON 与嵌套类型不符用例，确认均抛 DataError 而不返回成功零值；用虚构测试 Token 验证错误脱敏，不读取真实凭据。
- [X] T021 [P] [US3] 在 tests/test_app.py 验证 DataError→502、未知内部异常→安全 500、空业务集合→200，检查 UTF-8 JSON/no-store 以及错误不泄露虚构 Token 或 traceback；不把既有起始 501 视为最终成功行为。

### Implementation for User Story 3

- [X] T022 [US3] 在 services/dashboard.py 将连接、轮询和结果校验错误转换为安全 DataError，处理连接异常组并保留原始错误链供本地调试；拒绝截断或不完整结果，不捕获后返回固定业务值；继续复用 services/mcp_sql.py 的既有只读与轮询行为，不重写连接模块。
- [X] T023 [US3] 在 app.py 补充未预期错误的通用 JSON 500 响应，保留 400/502 的凭据遮蔽和缓存禁止；业务完成后 /api/dashboard 不再以 NotImplementedError/501 作为正常分支，不改变无关静态路由。
- [X] T024 [P] [US3] 在 static/index.html 增加 loading/empty/error 状态容器与重试按钮，使用 role=status 或等效可访问提示，加载/失败时隐藏旧结果区，成功无记录有明确说明。
- [X] T025 [P] [US3] 在 static/style.css 实现加载、空结果和错误的可辨识样式、隐藏规则及重试焦点状态，在窄屏中仍能操作，不依赖颜色作为唯一状态提示。
- [X] T026 [US3] 在 static/app.js 将当前请求统一推进 loading→success/empty/error；空结果计数为 0、比例 N/A、对比清空；失败保留当前筛选并允许重试，不保留其他范围图表冒充结果；网络中断/非 JSON 响应显示安全错误，沿用 T018 的最新请求保护。
- [X] T027 [US3] 按 specs/001-transport-performance-dashboard/quickstart.md 验证四种状态和恢复后单次重试、零分母、旧请求乱序及无数据兜底，记录 SC-003 与 FR-008；与真实 MCP 连接核验分别记录，页面未完成或未运行时不勾选本项。

**Checkpoint**: US1—US3 完成后才可验收完整 P1；P2 保留未完成。

## Phase 6: User Story 4 - 每日运输量趋势 (Priority: P2，后续安排)

**Goal**: 当前范围内自然日连续、无单日补零，趋势合计与运输总量一致。

**Independent Test**: 缺日、多日、单日及空范围分别核对，空范围不制造日期；无需明细模块。

### Tests for User Story 4

- [X] T028 [US4] 在 tests/test_queries.py 增加趋势范围首尾、缺失自然日、单日、空范围及筛选后合计的用例；验证业务日期“不随展示时区改日”的数据含义，最终 SQL 结果用只读查询核对。

### Implementation for User Story 4

- [X] T029 [US4] 在 services/queries.py 基于同一过滤运输单集合构造 min/max shipment_date、连续日期序列与逐日计数，约束原文为“daily 从范围内最早 shipment_date 到最晚日逐日生成；缺失日为 0，合计等于 summary.total_count；空范围 daily=[]”，按日期升序输出，保留 P1 计数口径。
- [X] T030 [US4] 在 services/dashboard.py 校验 daily 日期有序连续、计数非负及与 summary.total_count 的合计一致，空范围要求 []；在 tests/test_dashboard.py 增加合计错误和空范围虚构日期的拒绝用例。
- [X] T031 [US4] 在 static/index.html 和 static/style.css 增加可访问每日趋势区域及响应式布局，不加入分页或虚构日期。
- [X] T032 [US4] 在 static/app.js 用接口 daily 绘制原生 SVG 趋势，兼容空集合/单日/补零日期，与指标和对比同响应更新并遵守加载及错误隐藏规则。
- [X] T033 [US4] 按 specs/001-transport-performance-dashboard/quickstart.md 验证缺日、单日、空范围及承运商切换的真实趋势，核对 SC-005，确认不影响 P1 的筛选和比例。

## Phase 7: User Story 5 - 分页明细与时间说明 (Priority: P2，后续安排)

**Goal**: 当前范围内每页 20 单、稳定排序、结果分类准确，源快照和查询时间分别显示。

**Independent Test**: 使用包含同日多单的 41 单稳定集合验证 20/20/1、三页无重复遗漏、筛选重置；覆盖五类结果与缺失时间、已知 UTC→上海时间转换。可在 US4 未实现时单独验证明细；全组件联验须等待 US4。

### Tests for User Story 5

- [X] T034 [P] [US5] 在 tests/test_queries.py 增加 41 单分页、同日排序、越界钳制、空范围及五类结果/源快照的用例，将 T002 中仅限 P1 的 page>1 拒绝预期更新为 P2 合法页可用；源标识约束原文为“非空业务标识；P2 排序的第二关键字”，页码限制仍按合同；真实分页无遗漏验证由 T043 执行。
- [X] T035 [P] [US5] 在 tests/test_dashboard.py 验证页大小/总数/实际页、UTC Z 字符串、缺失时间 null、成功后才生成 queried_at、损坏明细拒绝，以及源快照不被当前时间替代；使用构造时刻，不依赖真实源快照固定值。
- [X] T036 [P] [US5] 在 tests/test_app.py 扩展合法 page>1、保留筛选、越界钳制响应及无效页码拒绝的合同用例，替换仅适用于 P1 的 page=2 拒绝预期，保持其他 400/502/500 测试有效。

### Implementation for User Story 5

- [X] T037 [US5] 在 services/queries.py 同一范围查询中用 SQL 侧 ROW_NUMBER 与实际页范围过滤实现每页 20 条、总页数及稳定有序数组，放开合法 page>1；依据总量在同查询中钳制末页，不依赖动态 OFFSET；明细返回合同所列编号、名称、日期、起讫城市、计划/实际到达、status/result，源状态“DELIVERED、IN_TRANSIT、CANCELLED”先区分在途/取消，再对已送达按缺时间/准时/延误分类；同查询计算范围最大非空 snapshot_at 并将时刻规范为 UTC Z 字符串；遵守“同一源集合中明细排序为 shipment_date ASC、shipment_id ASC；排序、分页及数组序列化顺序必须一致”，空范围“page=1、total_pages=0、shipments=[]”，超末页钳制；不在 Python 或页面加载全部明细再切页。
- [X] T038 [US5] 在 services/dashboard.py 校验并返回分页和明细合同，时间约束原文为“时刻传输为含 Z 的 UTC ISO 8601 字符串，页面按 Asia/Shanghai 展示；业务日期直接保持 YYYY-MM-DD”；到达时间缺失为 null，源快照按“source_snapshot_at=max(当前范围非空 snapshot_at)，空范围或全缺失为 null”；仅成功校验后生成 queried_at；结果枚举为 ON_TIME、DELAYED、IN_TRANSIT、CANCELLED、MISSING_TIMESTAMP，源状态不符时报错。
- [X] T039 [US5] 在 app.py 使用已扩展到 P2 的页码校验，允许 page>1 且仍拒绝非法格式/重复参数；维持 GET /api/dashboard 入口与 no-store，不新增可绕过筛选的明细接口。
- [X] T040 [P] [US5] 在 static/index.html 增加运输明细表、当前页/总页/总单数、上一页/下一页及两种时间说明，列至少包含编号、承运商、业务日期、线路、计划/实际到达和结果；空集合显示无记录而非矛盾页码。
- [X] T041 [P] [US5] 在 static/style.css 增加表格窄屏滚动、五类结果和分页/时间说明样式，禁用按钮可辨识，保留 P1 指标与控件布局。
- [X] T042 [US5] 在 static/app.js 渲染每页最多 20 单、五类结果和 Intl.DateTimeFormat 的 Asia/Shanghai 时间；源起讫城市约束“缺失时页面显示‘—’”，时间缺失同样显示“—”；“筛选变化、清除或重新查询重置请求页为 1；普通翻页保持范围，失败重试保留目标页”；首次/末页禁用越界操作，继续遵守请求序号保护。
- [X] T043 [US5] 按 specs/001-transport-performance-dashboard/quickstart.md 逐页核对稳定源集合，验证 SC-006/SC-007、五类结果、空范围与快照缺失；US4 已完成时联验指标/对比/趋势/明细范围一致，否则明确记录趋势联验尚未完成。

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: 根据获准交付范围执行收尾，不让 P1 验收依赖未授权 P2。

- [X] T044 更新 README.md 及 specs/001-transport-performance-dashboard/quickstart.md 的 P1 使用和验收说明，区分连接成功/结构检查/业务验收，列出 P2 尚未实现的范围，去除已完成 P1 的起始页/正常 501 说法；不承诺尚未运行的验证。
- [X] T045 按 specs/001-transport-performance-dashboard/quickstart.md 执行当前 P1 适用的离线检查、Python 运行连接、真实业务查询及桌面/窄屏操作；检查 app.py、services/、static/ 不含业务假值兜底或凭据，保留 tests/test_training_state.py 的既有行为，在课堂会话如实记录结果及未验证项，不创建额外记录文件。
- [X] T046 仅 P2 获准并完成时更新 README.md 及 specs/001-transport-performance-dashboard/quickstart.md 的趋势、分页、时间与完整验收说明，将 P2 未实现表述改为实际状态；记录源快照变化会影响固定历史数字。
- [X] T047 仅 P2 获准并完成时按 specs/001-transport-performance-dashboard/quickstart.md 执行全部范围联验及 P1 回归，核对 services/queries.py 的分页仍在查询侧、static/app.js 无过时状态覆盖，记录离线/实时/页面证据；不自动提交、推送或部署。

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 T001 无前置；Phase 2 T002—T005 依赖 T001。所有故事依赖 Phase 2。
- Phase 3—5 合起来构成完整 P1；交付遵守先 P1 后端、再 P1 前端，非简单按整段 Phase 顺序一次执行。
- Phase 6—7 为 P2，只有用户明确安排后才启动。US4 与 US5 可分别验收，但修改同一个查询/服务/页面文件时必须串行合并。
- Phase 8 中 T044/T045 仅依赖 P1 完成，T046/T047 依赖获准的完整 P2；P1 不等待 US4/US5。

### 具体任务前置

| 任务 | 必须先完成 |
| --- | --- |
| T002 | T001 |
| T003 | T002 |
| T004 | T001 |
| T005 | T003、T004 |
| T006、T007 | T005 |
| T008 | T006 |
| T009 | T007、T008 |
| T010、T011 | T009 |
| T012 | T009、T010、T011 |
| T013 | T012 |
| T014 | T009 |
| T015 | T014 |
| T016 | T009、T015 |
| T017 | T010、T011 |
| T018 | T012、T016、T017 |
| T019 | T018 |
| T020、T021 | T005、T009、T016 |
| T022 | T020 |
| T023 | T021、T022 |
| T024、T025 | T010、T011 |
| T026 | T018、T023、T024、T025 |
| T027 | T026 |
| T028、T034、T035、T036 | T013、T019、T027、T044、T045，以及用户明确安排 P2 |
| T029 | T028 |
| T030 | T029 |
| T031 | T030 |
| T032 | T031 |
| T033 | T032 |
| T037 | T034 |
| T038 | T035、T037 |
| T039 | T036、T038 |
| T040、T041 | T039 |
| T042 | T040、T041 |
| T043 | T042 |
| T044 | T013、T019、T027 |
| T045 | T044 |
| T046 | T033、T043 |
| T047 | T046 |

测试任务编写后允许观察预期业务缺失造成的失败；对应实现通过测试才满足后续代码任务的前提。页面任务可基于已确定合同，但本课堂优先实际后端完成后集成。

### User Story Dependencies

```text
Setup → Foundational → US1 后端 → US2 后端 → US3 后端
                                  ↓
                     US1 页面 → US2 页面 → US3 页面
                                  ↓
                         P1 独立验收与收尾
                                  ↓ 用户另行安排 P2
                        US4 趋势 / US5 明细时间
                                  ↓
                            全范围联验收尾
```

US2/US3 复用 US1 的查询和页面基础，并可在自己的验收集合上独立核对。US4 与 US5 不互为业务前提，US5 的全组件范围检查在 US4 完成后联验。共享文件意味着实现顺序需串行，不把故事都标记为完全可并行。

### Parallel Opportunities & Examples per Story

| 故事 | 可并行示例 | 前提与限制 |
| --- | --- | --- |
| US1 | T006 tests/test_queries.py 与 T007 tests/test_dashboard.py；T010 static/index.html 与 T011 static/style.css | 前一组需 T005，后一组需 T009；JS 集成等两文件完成 |
| US2 | T014 tests/test_queries.py 与 T017 static/index.html 可由不同人员基于合同准备 | 分别满足 T009 与 T010/T011；实际课堂仍按后端轮/前端轮推进，不为此跨轮自动实施；T015 与 T016 有先后关系 |
| US3 | T020 tests/test_dashboard.py 与 T021 tests/test_app.py；T024 static/index.html 与 T025 static/style.css | 分别满足前置表；T022/T023、T026 串行集成 |
| US4 | T028 tests/test_queries.py 与基于已定合同准备 T031 的页面区域可分工 | 正式 T031 合并仍等待 T030；本故事无已就绪且完全独立的实现任务对，不额外标 [P] |
| US5 | T034/T035/T036 三个不同测试文件；T040 static/index.html 与 T041 static/style.css | 测试组须 P1 已验收且 P2 获准；页面组需 T039；T037/T038/T039 串行 |

不要在 US4/US5 同时修改 services/queries.py、services/dashboard.py 或 static/app.js；同文件任务即使故事不同也不并行。

## Implementation Strategy

### MVP First

最小业务演示增量为 US1：T001—T013。它能独立验证整体运输表现；正式 P1 验收还必须包含 US2/US3 的筛选、刷新和状态恢复，不以 US1 代替完整 P1。

### 课堂推荐实施轮次

| 轮次 | 任务 ID | 范围与结束条件 |
| --- | --- | --- |
| P1 后端 | T001—T009、T014—T016、T020—T023 | 输入、聚合、筛选、MCP、结果验证与错误响应；必要测试和实际查询通过。UI 验收 T013/T019/T027 暂不勾选 |
| P1 前端与验收 | T010—T013、T017—T019、T024—T027、T044—T045 | 指标、筛选、对比及四类状态，桌面/窄屏与同范围真实查询验收 |
| P2 趋势 | T028—T033 | 获准后单独实现并核对自然日补零与合计 |
| P2 明细与时间 | T034—T043 | 获准后单独实现查询侧分页、五类结果和时间说明 |
| P2 完整收尾 | T046—T047 | 两个 P2 故事完成后全范围联验及 P1 回归 |

### Incremental Delivery

按用户本次指定范围选择任务，先报告 ID、拟改文件及验收；完成相应故事或后端轮后记录实际证据。只完成当前课堂阶段，等待下一条指令，不自动进入其余轮次。任务生成时 T028—T043 保留待办；本次用户已明确选择完整 P1 与 P2，因此这些任务也已纳入实施与验收。

## Notes

- FR-001—FR-004/FR-009 → US1 的 T006—T013，并由 US2 维度边界 T014—T016 补充；FR-005/FR-007 → US2；FR-006/FR-008 → US3 和基础错误/只读编排；FR-010 → US4；FR-011—FR-014 → US5。
- SC-001/SC-004 → T013；SC-002 → T019；SC-003 → T027；SC-005 → T033；SC-006/SC-007 → T043。T045/T047 负责获准范围的交叉回归。
- 执行已有 uv 环境中的定向测试优先；只有缺依赖失败或清单变化时才安装/恢复依赖，不引入 npm 工程。
- 任务生成阶段仅形成待办。本次实施按用户明确选择完成完整 P1/P2；凭据仍仅由后端运行连接读取，不在聊天中查看或展示。本次未提交、推送或部署。具体测试与未验证项见 quickstart.md 第 8 节。
