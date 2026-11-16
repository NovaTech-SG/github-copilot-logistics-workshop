# Phase 0 Research: 本机保存与确认

日期：2026-11-16。依据当前应用源码、[规格](spec.md)、[宪章](../../.specify/memory/constitution.md)及[数据说明](../../docs/data-source.md)。未读取相邻项目、Git 历史或凭据配置，未调用实时源查询。现有技术选择已明确，无需外部研究或新增依赖。

## 1. 写入事务与过期检查

**Decision**: 沿用 FollowUpStore.connect，在保存连接中先执行 BEGIN IMMEDIATE，再按 exception_id 查询本机记录。当前有效状态优先取本机记录，否则取本次 Tracker.source_record 读取的源状态。校验 expected_status 的合法性和相等性，复用 validate_change，使用参数占位符执行 INSERT ... ON CONFLICT(exception_id) DO UPDATE。由现有连接上下文完成提交或回滚。

**Rationale**: 服务是 ThreadingHTTPServer，多次请求可能并行。先取得写锁再读状态，避免两个不同连接同时依据旧本机状态通过检查。既有连接 timeout=5 和异常映射可复用。事务内不调用 MCP，源记录仍按既有流程在事务前获取；该锁只串行化本机写入，不承诺锁住外部源变更。

**Alternatives considered**: 先 overlay 再在另一连接写入有本机竞态；默认延迟事务不能可靠保护读后写；新建 ORM、锁服务或完整版本体系超出范围。同状态并发备注沿用后一次合法保存更新，不增加版本字段。

## 2. 保存结果与时间

**Decision**: 不改表。以 datetime.now(timezone.utc).isoformat() 生成本机 updated_at。事务退出成功后通过已有 overlay([source]) 重新读取并返回合并记录，保持 Tracker.update 的响应结构。

**Rationale**: 后端返回和详情使用相同合并规则，保留业务背景及 source_handling_status，避免把原始 SQLite 行误当完整详情。提交后读取失败时，写入可能已完成，页面仍需重新读取核对；保存方法内部重读不替代前端独立 GET。

**Alternatives considered**: 直接返回提交内容不能证明已保存；在同一尚未提交的事务中返回数据不足以证明提交成功；另建历史表或保存源快照没有需求支持。

## 3. 页面确认与重复提交

**Decision**: submit 入口立即捕获 id、目标状态、trim 后备注及原状态，setBusy(true) 覆盖 POST 和后续 GET 全流程。只按捕获编号 GET，匹配编号、状态和备注后 replaceRecord，再显示成功。POST 成功但 GET 失败或不匹配显示已提交但尚未确认。原生 fetch 失败代表结果不确定，不冒称肯定未保存。

**Rationale**: 现有 setBusy 同时禁用保存、读取、全量刷新及编辑控件；选中行已有 busy 检查。replaceRecord 会清空 save-message，因此最终提示必须置于它之后。更新已确认单条记录即可重算概览、筛选和分页，不增加全量 MCP 查询。

**Alternatives considered**: 只看 POST 返回会误报确认；直接将输入覆盖列表伪造保存结果；再次 POST 作为确认会重复写入。无需引入前端框架或状态库。

## 4. 手动重读与错误恢复

**Decision**: 保存尚未确认时保留本次提交的编号、状态及规范化备注作为轻量确认上下文。手动重读对应异常可再次匹配；一致才报告已确认，不一致继续提示未确认并展示实际读取值。切换到其他异常或开始新一轮提交时不沿用旧确认上下文。普通手动重读仅提示已读取，不暗示新保存成功。

**Rationale**: 已有 read-record 会无条件显示读取成功，需要最小配合才能准确区分读取成功和保存核对成功。重新读取后更新 selected，使冲突后的原状态可重新建立。

**Alternatives considered**: 只在首次提交函数内保存局部上下文，后续重读无法核对原提交；持久化浏览器待确认队列超出本轮需求。刷新后以服务实际记录为准，不恢复历史提示。

## 5. 源更新时间的现有缺口

**Decision**: FR-010 要区分源更新时间与本机保存时间。当前 queries.build_query 没有返回 e.updated_at；计划仅增加 unix_timestamp(e.updated_at) AS source_updated_epoch 并将该字段放入现有 JSON 行，app.js 在现有 source-state 中显示。空源时间显示“—”，不拿 source.queried_at 或本机时间代替。

**Rationale**: docs/data-source.md 已说明 exceptions.updated_at。现有 extract_records 允许额外字段，overlay 保留源字段，故无需重写解析或服务层。实际源字段类型及权限留待实时只读核对，不能假称已验证。

**Alternatives considered**: 忽略此字段不满足活动规格；将查询完成时间标为源更新时间语义错误；单独加查询增加不必要往返。保留原关联、条数保护、排序和只读 MCP 路径。

## 6. 最小验证方案

**Decision**: Python unittest 使用临时数据库与假源覆盖插入、更新、同状态、trim、边界、过期拒绝、同单隔离、重开恢复以及事务失败回滚；本机 HTTP 测试核对现有错误码及 POST 后 GET。前端用 Node 内置 test/vm 与最小 DOM、fetch 替身覆盖时序、内容不匹配、请求失败和重复提交，不新增依赖。完整 README 离线命令在实施完成后执行，真实 MCP、真实页面和同库重启另记证据。

**Rationale**: 目前只有规则及阶段检查，不能证明保存。使用临时表触发器等失败注入可验证写入发生后异常仍回滚，避免只测校验报错。前端语法检查不能替代流程验证，替身测试也不能代替真实页面。

**Alternatives considered**: 新装浏览器测试框架不符合依赖边界；只断言 SQL 文本、函数存在或常量不能证明行为；直接跑真实写入验收不属于本次计划阶段。

## Resolution

技术决策已确定，无待澄清项。待实施后执行的实际 MCP、页面及重启检查是验证工作，不能用本研究或效果稿结果代替。
