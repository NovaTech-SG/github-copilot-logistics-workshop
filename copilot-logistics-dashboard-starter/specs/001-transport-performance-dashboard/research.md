# Research: 运输表现看板

**Date**: 2026-11-16 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## 研究依据与真实核对

仅研究当前应用的 app.py、services、static、pyproject.toml、README 与项目数据说明。未读取相邻完成版、内部资料、历史实现或实际凭据。研究均可直接由当前骨架和小规模只读查询确定，无需外部研究服务或新增工具。

本阶段使用 Databricks 只读 MCP 核对：

- carriers 结构为 carrier_id/string、carrier_name/string、service_region/string、is_active/boolean。
- shipments 共 500 行、500 个不同 shipment_id，空 shipment_id 为 0，空 shipment_date 为 0，数据说明以外或空的 status 为 0。
- carriers 共 4 行、4 个不同 carrier_id，空 carrier_id 为 0；shipments 中未匹配 carriers 的记录为 0。
- 上一课堂阶段已读取 shipments 的 15 个字段及类型，与数据说明一致。本次不把当时导出文件作为设计或运行时数据源。

上述为当次源数据观察，不证明物理主键约束、不保证未来数据不变，也不作为测试中硬编码业务期望。未执行待实现 Dashboard SQL，未验证 Python 运行连接或页面功能。

## R1：沿用服务与连接骨架

**Decision**: 保留 get_dashboard(settings, carrier="", page=1) 与 build_query(prefix, carrier="", page=1) 的入口；同步 HTTP 线程通过 asyncio.run 进入异步 MCP 会话，调用 connect → execute_read_only → extract_dashboard，最后验证业务合同。

**Rationale**: 当前 ThreadingHTTPServer 的请求线程没有运行事件循环；已有模块处理工具发现、SQL 状态轮询及结果截断，无需重写。

**Alternatives considered**: 引入异步 Web 框架会增加依赖和课堂迁移成本；浏览器直连会暴露凭据；直接调用 SQL 写工具违反只读边界。

## R2：一次只读查询产生结构化结果

**Decision**: SQL 用公共表表达式构造运输单范围、有效/准时标记、总汇总、承运商汇总及全局选项；最终用结构化 JSON 返回单行单列 dashboard_json。明确使用空数组而不是 null。服务补充请求范围元数据。P1 daily、shipments 为 []。

**Rationale**: extract_dashboard 明确要求单行、单列、完整 JSON，且存在 summary/carriers/by_carrier/daily/shipments 五个键。一次查询减少往返并让同次指标使用一致范围。

**Alternatives considered**: 返回所有单量到 Python 计算不符合 P1 聚合和 P2 查询侧分页目标；多个独立查询会扩大网络成本并可能读取不同时刻数据；修改通用拆包约定没有必要。

## R3：计数与承运商名称分离

**Decision**: 在 shipments 原始粒度上计算总量、有效量、准时量，按 carrier_id 聚合后再关联唯一名称映射。映射按 carrier_id 分组；重复名称时取非空名称的确定性最小值，名称全缺失时回退编号。不关联 exceptions。选项取 carriers 编号与 shipments 出现编号的并集，去重并按编号升序；不按 is_active 或区域过滤。

**Rationale**: 业务统计不应被维度重复或一单多异常放大，且不能丢失没有匹配名称的运输单。源表当前标识唯一，与此设计一致。

**Alternatives considered**: 先直接连接明细再聚合会放大计数；内连接丢弃未匹配运输单；只返回范围内选项会使用户无法切回其他承运商。

## R4：输入验证与 SQL 边界

**Decision**: HTTP 仅接收一个 carrier 和一个 page，拒绝重复及未知参数；carrier 缺省/空表示全部，非空最多 64 字符，允许字母、数字、下划线和短横线，不自动修剪或变更大小写；page 为十进制正整数且不超过 2147483647。P1 只接受 page=1，P2 支持其余页。现有 Settings 校验 Catalog/Schema，build_query 同样校验传入的带反引号双层前缀，不能拼入任意表路径。验证后才构造 SQL 字面值和数值偏移量。

**Rationale**: 当前 execute_read_only 接口接收 SQL 字符串而非绑定参数，因此必须在业务查询入口做严格输入限制。当前 CAR001 等编号满足规则；不存在的合法编号返回空范围，不报输入错误。

**Alternatives considered**: 固定只允许当前四个编号阻碍源表扩展；接受任意用户 SQL 或任意 catalog/schema 字符串不满足固定只读查询边界。

## R5：失败与返回数据校验

**Decision**: 参数错误映射 400，连接/轮询/数据结构错误映射 502；实现阶段捕获连接相关异常与异常组，转为 DataError，保持 Token 遮蔽并避免向前端透出原始连接信息。未知程序异常返回通用 500，不能伪造成功。校验计数为非负整数、计数恒等式和比例有限且在 [0,100] 内，分母为零时比例必须为 null；拒绝不完整、截断和非预期字段类型结果。完成时间仅在解析与校验全部成功后生成。

**Rationale**: 现有提取器验证外层信封但没有全部业务类型检查；app.py 已有 ValueError/DataError 状态映射，网络异常仍需在编排边界转换。

**Alternatives considered**: 所有异常都返回 200 会混淆失败与空结果；捕获后返回固定 0 会误导运营；展示旧结果不标记会违反规格。

## R6：前端范围与状态一致性

**Decision**: 原生 fetch 请求同源 API；请求序号控制所有成功、失败、finally 状态更新，同时用 AbortController 终止过时客户端请求。中止不等于取消后端 SQL，不增加写工具。加载时清除当前图表或隐藏上次成功区；失败只保留可用筛选及错误/重试。源名称与错误使用 textContent。清除、选择、刷新和重试都使用当前范围；P2 筛选与刷新回第 1 页。

**Rationale**: 用户快速切换时，旧请求的成功或失败都不能覆盖最新范围。无需新增状态管理依赖。

**Alternatives considered**: 仅依靠请求返回顺序存在覆盖错误；仅靠 AbortController 不能保证已经完成的解析回调不执行。

## R7：P2 趋势、分页与时间

**Decision**: 以当前范围 min/max shipment_date 生成连续自然日并补零；空范围不展开日期序列。明细在 SQL 用 ROW_NUMBER 按业务日期升序、单号升序编号，依据钳制后的实际页过滤 20 条，再按同一顺序序列化；页总数由范围总量计算，合法但超出末页的请求钳制到末页，空范围 page=1、total_pages=0。采用窗口范围过滤使同一查询能够依据总量钳制末页，无需第二次查询来生成字面量 OFFSET，仍全部在数据库侧分页。查询结果附当前范围最大非空 snapshot_at，成功服务响应附 UTC ISO 8601 查询完成时间；源时间同样规范为带 Z 的 UTC 字符串，页面 Intl.DateTimeFormat 以 Asia/Shanghai 转换。业务日期不做时区换日。

**Rationale**: 与规格自然日补零、稳定分页、上海时间和源快照含义一致。使用单个 SQL 可避免同次总量与分页使用不同筛选；跨请求源变化不在冻结保证内。

**Alternatives considered**: 页面切分全部明细违反查询侧分页；以数据快照代替查询完成时间混淆新鲜度；无时区字符串在不同电脑解释不一致。

## 研究结论

无未决技术澄清。保留所有现有依赖，实施分为 P1 后端、P1 前端与后续 P2；设计细节见 [数据模型](data-model.md) 和 [接口合同](contracts/dashboard-api.md)。
