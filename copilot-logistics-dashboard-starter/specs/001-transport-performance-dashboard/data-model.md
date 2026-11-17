# Data Model: 运输表现看板

**Spec**: [spec.md](spec.md) | **Contract**: [dashboard-api.md](contracts/dashboard-api.md)

## 1. 源实体

### Shipment：运输单

粒度为一张运输单；shipment_id 是逻辑唯一标识，不宣称源表已经定义物理主键。

| 源字段 | 已核对类型 | 用途与约束 |
| --- | --- | --- |
| shipment_id | string | 非空业务标识；P2 排序的第二关键字 |
| order_ref | string | 订单参考号，本次不必展示 |
| carrier_id | string | 关联承运商、筛选与分组；名称缺失不丢单 |
| origin_city / destination_city | string | P2 线路 |
| transport_mode | string | 源运输方式，本次不增加筛选 |
| shipment_date | date | 业务日期，P2 趋势及分页第一排序字段；不随展示时区改日 |
| shipped_at | timestamp | 源发运时刻，本次不必展示 |
| planned_arrival / actual_arrival | timestamp | 准时判断；任一缺失则不进入有效分母 |
| status | string | DELIVERED、IN_TRANSIT、CANCELLED |
| carton_count | int | 本次不统计 |
| weight_kg | decimal(10,2) | 本次不统计 |
| freight_cost_cny | decimal(12,2) | 本次不统计 |
| snapshot_at | timestamp | P2 当前范围最新源快照候选值，不能代替查询完成时间 |

### Carrier：承运商

| 字段 | 已核对类型 | 用途与约束 |
| --- | --- | --- |
| carrier_id | string | 逻辑标识，一对多关联 shipments.carrier_id |
| carrier_name | string | 展示名称，空值或空字符串时回退编号 |
| service_region | string | 源资料，不自动过滤 |
| is_active | boolean | 源资料，不自动过滤 |

统计先在运输单粒度完成，承运商资料仅提供展示映射。同编号源资料重复时先按编号合并，取非空名称的确定性最小值，避免放大统计。运输单有编号但没有承运商资料时仍参与统计、对比和筛选。

### Exception：运输异常（范围外）

exception_id 为逻辑标识，shipment_id 指向运输单；一张运输单对应零到多条异常。本功能不访问 exceptions、不展示处理进度，也不根据异常记录推断准时或延误。

## 2. 过滤范围

- carrier=""：全部业务日期、全部运输单。
- carrier 为合法编号：严格匹配 shipments.carrier_id；其他所有已实现组件使用同一范围。
- 选项数组独立于当前过滤范围，取源 carriers 与 shipments 中承运商编号的去重并集，按编号升序。
- page 影响 P2 明细切片，不改变指标、对比或趋势。
- 输入长度、格式、页码及错误见 [接口合同](contracts/dashboard-api.md)。源标识超出已记录格式属于需要重新核对的数据变化，不通过静默截断修改其含义。

## 3. 派生指标

| 字段 | 规则 |
| --- | --- |
| total_count | 当前范围运输单数 |
| eligible_count | status=DELIVERED 且 planned_arrival、actual_arrival 均非空的单数 |
| on_time_count | 有效单中 actual_arrival <= planned_arrival 的单数 |
| delayed_count | eligible_count − on_time_count |
| excluded_count | total_count − eligible_count |
| on_time_rate | eligible_count>0 时为 100 × on_time_count / eligible_count，四舍五入两位；否则 null |

前端将比例显示为两位小数加百分号，null 显示 N/A；不得用 0 替换 null。全部计数为非负整数；on_time_count ≤ eligible_count ≤ total_count。按承运商汇总的各计数合计必须等于整体计数，整体比例直接使用总准时量和总有效量。

SQL 生成空范围时显式 coalesce 求和为空的计数到 0，比例保持 null。不能把失败或结果损坏转换成空范围。

## 4. 结果对象

完整字段、必填性及 HTTP 语义见接口合同。核心结构：

- summary：上述六项指标。
- carriers：全局承运商选项，包含 carrier_id、carrier_name。
- by_carrier：范围内有运输单的承运商及六项指标，按编号升序；零有效量记录保留。
- daily：P1 固定为空数组；P2 为连续日期及 daily total_count，按日期升序。
- shipments：P1 固定为空数组；P2 仅包含本页明细，按日期与单号升序。
- scope：服务附加的规范化 carrier 筛选，不能携带凭据。
- pagination、source_snapshot_at、queried_at：P2 增量字段，P1 不承诺提供。

## 5. P2 明细运输结果

依次判断下表，不能对在途或取消单应用送达准时率判断。

| 条件 | result | 展示 |
| --- | --- | --- |
| status=IN_TRANSIT | IN_TRANSIT | 在途 |
| status=CANCELLED | CANCELLED | 已取消 |
| status=DELIVERED 且任一到达时间缺失 | MISSING_TIMESTAMP | 时间缺失 |
| status=DELIVERED 且时间完整、实际不晚于计划 | ON_TIME | 准时 |
| status=DELIVERED 且时间完整、实际晚于计划 | DELAYED | 延误 |

源状态不属于上述枚举时不猜测为已送达，返回数据错误以便核对源数据。时间缺失以 null 传输，以“—”展示。

## 6. P2 日期、分页与时间

- daily 从范围内最早 shipment_date 到最晚日逐日生成；缺失日为 0，合计等于 summary.total_count；空范围 daily=[]。
- page_size=20；total_pages=ceil(total_count/20)。非空时响应 page=min(请求页,total_pages)；空范围 page=1、total_pages=0、shipments=[]。
- 同一源集合中明细排序为 shipment_date ASC、shipment_id ASC；排序、分页及数组序列化顺序必须一致。分页查询不加载所有逐单结果到 Python 或浏览器。
- source_snapshot_at=max(当前范围非空 snapshot_at)，空范围或全缺失为 null，展示名“源数据最新快照”。该值不代表每一张单的快照时刻。
- queried_at 由后端在 MCP 成功、结果解析和业务校验通过后生成；失败不产生新的成功时间。
- 时刻传输为含 Z 的 UTC ISO 8601 字符串，页面按 Asia/Shanghai 展示；业务日期直接保持 YYYY-MM-DD。

## 7. 状态转移

初始进入 loading；请求成功后根据 total_count 进入 success 或 empty；请求失败进入 error。筛选、清除、刷新、重试均从当前状态进入 loading，新请求序号成为唯一可提交结果的请求。

- loading：显示加载，不将前一次成功指标或图表标记为当前结果。
- success：同时渲染同一响应的范围、指标、对比及已实现的 P2 组件。
- empty：显示无记录、计数 0、比例 N/A，对比/趋势/明细为空。
- error：显示安全错误与重试，保留当前筛选；不回退业务值。
- 过时请求成功、失败或取消均不得更新最新请求的视图或加载状态。
- P2 筛选变化、清除或重新查询重置请求页为 1；普通翻页保持范围，失败重试保留目标页。

## 8. 数据与凭据边界

不创建本地业务库，不保存 Token 到响应、文档或日志，不读取本机实际凭据。业务表不可写；mockup 和聊天导出文件都不是应用运行时数据源。单元测试允许构造独立验收数据，实际业务验收仍需运行时只读查询。
