# Databricks 数据来源与表关系

## 数据从哪里来

应用运行时的业务数据来自 Databricks 中的培训表，通过现有只读 MCP 获取。数据路径是“浏览器 → 本地 Python 后端 → Databricks MCP → 业务表”。浏览器不直接连接 Databricks，也不持有 Token。

开发时，Cursor Agent 可以通过本项目 `.cursor/mcp.json` 配置的 Databricks MCP 查看表结构和核对结果；应用运行时则由自己的 Python 后端调用 MCP。聊天中查到的数据不能代替应用的实际查询。

只调用 `execute_sql_read_only` 和 `poll_sql_result`。不写 Databricks 源表，查询失败时明确报错，不使用本地 CSV、mockup 数字或固定结果兜底。

表名前缀由当前项目的 Catalog 和 Schema 配置决定。课堂示例为 `dev_databricks.default`，实际查询前通过只读 MCP 核对表名、字段类型与权限。

## 三张业务表

| 表 | 中文含义 | 一行代表什么 | 逻辑唯一标识 |
|---|---|---|---|
| `carriers` | 承运商 | 一个承运商 | `carrier_id` |
| `shipments` | 运输单 | 一张运输单 | `shipment_id` |
| `exceptions` | 运输异常 | 一条异常记录 | `exception_id` |

这些是业务上的标识与关联关系；是否定义了物理主键或外键约束，以实际建表结构为准。

## 如何关联

| 关联字段 | 对应字段 | 业务关系 |
|---|---|---|
| `shipments.carrier_id` | `carriers.carrier_id` | 一个承运商可以负责多张运输单 |
| `exceptions.shipment_id` | `shipments.shipment_id` | 一张运输单可以没有异常，也可以有多条异常 |

异常通过运输单找到承运商，不直接用 `exception_id` 关联承运商。一张运输单出现多条异常时，每条异常仍由各自的 `exception_id` 标识。

## 关键字段怎么理解

- `carriers`：`carrier_id` 用于关联，`carrier_name` 用于展示；`service_region` 是服务区域，`is_active` 表示是否启用。是否据此筛选，由本次规格决定。
- `shipments`：`shipment_id` 是运输单编号，`order_ref` 是订单参考号，`carrier_id` 是负责承运商；`origin_city`、`destination_city` 是线路，`transport_mode` 是运输方式。
- 运输时间：`shipment_date` 是运输业务日期，`shipped_at` 是发运时间，`planned_arrival` 与 `actual_arrival` 用于判断准时；`snapshot_at` 表示源数据快照时间，不是本次查询完成时间。
- 运输状态：`shipments.status` 包括 `DELIVERED`、`IN_TRANSIT`、`CANCELLED`。已送达不自动等于准时。
- 其他运输字段：`carton_count` 是箱数，`weight_kg` 是重量，`freight_cost_cny` 是运费。新增指标前先确认规格和统计粒度。
- `exceptions`：`exception_id` 标识异常，`shipment_id` 指向运输单，`exception_type` 说明问题类型，`detected_at` 是发现时间，`assigned_team` 是负责团队。
- 异常处理：`handling_status` 包括 `OPEN`、`IN_PROGRESS`、`RESOLVED`；`follow_up_note` 是备注，`updated_at` 是源记录更新时间，`resolved_at` 是源异常解决时间。问题处理进度与运输状态、准时结果分别判断。

## 本项目如何使用

Dashboard 从 `shipments` 出发，按 `carrier_id` 关联 `carriers`，统计和比较运输表现。通常不需要关联 `exceptions`；若直接关联一单多条异常，会放大单量、重量、运费等汇总。

准时率和排除规则以活动 spec 为准；初始没有 spec 时先根据需求素材生成并确认。计算整体比例时使用总分子和总分母，不平均承运商百分比。

## Dashboard 统计口径

- 当前筛选范围内的全部运输单计入运输总量。
- 有效分母仅包括 `DELIVERED` 且计划、实际到达时间均完整的运输单；在途、取消和缺失判断时间的记录排除在分母外。
- 实际到达不晚于计划算准时，相等也算；延误量 = 有效单量 − 准时单量，排除量 = 总量 − 有效单量。
- 准时率 = 总准时量 ÷ 总有效单量，不取各承运商百分比的算术平均；零分母显示 N/A。
- 筛选后指标、对比、趋势和明细使用同一范围。空范围明确提示无记录，查询失败显示错误并允许重试，不以旧结果冒充本次查询。

## CSV 和效果稿的用途

仓库统一提供的 `data/` 是培训模拟 CSV，用于理解数据或由讲师准备 Databricks 表。它不是应用直接连接的本地业务数据库，放入仓库不会自动导入 Databricks。

若项目中有 `mockup/`，它只说明目标布局，固定样例不参与业务查询和指标计算。单元测试可以构造数据，应用运行仍按只读 MCP 路径获取结果。

根目录的《Databricks 三张表业务表说明》Word 供客户下载阅读；本文件供当前项目内的 Cursor Agent 和使用者理解数据，不需要跨项目读取 Word 或相邻完成版。
