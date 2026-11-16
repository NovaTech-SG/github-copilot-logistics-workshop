# Databricks 培训模拟数据

本目录包含物流工作坊的三张业务表数据，用于理解字段和关联关系，以及由讲师准备 Databricks 培训表。全部为培训模拟数据，不代表 Nike 实际运营情况。

## 文件与业务表

文件名与目标表名一致，导入时可以直接对应。以下行数不包含 CSV 表头。

| 文件 | 对应表名 | 中文含义 | 一行代表什么 | 本地数据行数 |
|---|---|---|---|---:|
| [carriers.csv](carriers.csv) | `carriers` | 承运商 | 一个承运商 | 4 |
| [shipments.csv](shipments.csv) | `shipments` | 运输单 | 一张运输单 | 500 |
| [exceptions.csv](exceptions.csv) | `exceptions` | 运输异常 | 一条异常记录 | 169 |

这三份 CSV 是课堂演示数据。目录中没有单独的验收用例数据集。

## 三张表如何关联

- `shipments.carrier_id` 对应 `carriers.carrier_id`：一个承运商可以负责多张运输单。
- `exceptions.shipment_id` 对应 `shipments.shipment_id`：一张运输单可以没有异常，也可以有多条异常。
- `exception_id` 标识一条异常。同一运输单上的不同异常需要分别跟进。

先确认一行代表什么，再决定统计对象。异常记录数与出现异常的运输单数可能不同，关联后计算运输单数量、费用或准时率时，需要检查记录是否重复。

## 建议使用顺序

1. 先读 [三张表业务表说明](<../Databricks 三张表业务表说明.docx?raw=true>)，理解业务对象、主要字段和统计口径。
2. 按 `carriers`、`shipments`、`exceptions` 的顺序查看 CSV，对照关联编号理解记录。
3. 讲师需要准备或重建培训表时，在课堂指定的 Catalog 和 Schema 中分别导入三份 CSV，核对表名、字段类型和行数。到达时间等字段要按课堂表结构处理，注意 CSV 中的 `null` 缺失值。
4. 学员按当前案例 README 连接 Databricks MCP。课程应用通过 MCP 读取源表；把 CSV 放进仓库不会自动创建 Databricks 表，也不会自动变成应用的数据源。

CSV 是静态文件，Databricks 表后续可能更新，实际查询结果以当时的源表为准。

返回 [工作坊资料与下载入口](../README.md)。
