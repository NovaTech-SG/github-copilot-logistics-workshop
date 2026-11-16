# Data Model: 异常跟进

依据：[规格](spec.md)、[研究](research.md)。本设计复用既有结构，不执行建表或迁移。

## 源异常（只读）

| 字段 | 语义与约束 |
| --- | --- |
| exception_id | 单条异常唯一标识；接口沿用 1–64 位字母、数字、下划线或连字符校验 |
| shipment_id | 关联运输单；一张运输单可有多条独立异常 |
| handling_status | 源状态，OPEN / IN_PROGRESS / RESOLVED |
| follow_up_note | 源备注；本机保存不能修改该源字段 |
| updated_at | 文档约定的源更新时间，计划以只读 source_updated_epoch 秒值返回；空值允许 |
| 其他背景字段 | 沿用异常类型、发现时间、团队、承运商与线路，不修改关联或运输单数据 |

未找到目标异常时，由 Tracker.source_record 沿用 NotFoundError 拒绝写入。实时结构尚未查询，updated_at 类型及权限需在后续验收核对。

## 本机 followups（既有 SQLite 表）

| 字段 | 类型 | 约束与用途 |
| --- | --- | --- |
| exception_id | TEXT | PRIMARY KEY；仅对已读取到的源异常写入 |
| handling_status | TEXT | NOT NULL；既有 CHECK 限定三种状态 |
| follow_up_note | TEXT | NOT NULL；validate_change 执行 strip 后必填、最多 1000 个 Python 字符 |
| updated_at | TEXT | NOT NULL；本次合法保存的 UTC ISO 8601 时间 |

每条异常最多一条当前本机记录。重复合法保存覆盖该异常当前状态、备注及时间，不累计历史。没有按 shipment_id 更新，不新增物理跨源外键。

## 状态转移与过期校验

| 当前有效状态 | 可提交目标状态 |
| --- | --- |
| OPEN | OPEN、IN_PROGRESS |
| IN_PROGRESS | IN_PROGRESS、RESOLVED |
| RESOLVED | RESOLVED |

当前有效状态优先为 SQLite 已保存状态，否则使用本次读取的源状态。BEGIN IMMEDIATE 后在同一连接中读取、比较 expected_status、执行 validate_change 并写入。expected_status 缺失或无效在既有接口校验返回 400；有效但过期返回 409。同状态并发备注按后一次合法写入更新，不承诺完整版本冲突检测。失败时原状态、备注及时间一起保留，首次写入失败不留记录。

## 合并详情（既有 overlay）

| 字段 | 来源 |
| --- | --- |
| exception_id、shipment_id、背景字段 | 源记录 |
| handling_status、follow_up_note | 有本机记录时取本机，否则源值 |
| source_handling_status | 合并前源状态 |
| saved_locally | 是否有该异常本机记录 |
| local_updated_at | 本机 updated_at，无记录为 null |
| source_updated_epoch | 只读源更新时间秒值，新增投影后由 overlay 原样保留 |

source.queried_at 是查询完成时间，不能当作源更新时间或本机保存时间。前端继续按上海时区显示；源时间为空时显示“—”。队列、筛选和概览继续根据合并后的 handling_status 计算。

## 提交与确认上下文（仅页面内存）

提交包含 exception_id（URL）、status、note 和 expected_status；note 在提交前规范化并由服务再次校验。页面保存快照而不依赖随后变化的输入框。

待确认上下文保留异常编号、目标状态、规范化备注及是否已收到提交成功响应。详情 GET 返回编号、状态、备注全部精确相等时确认。失败或不匹配不清除待核对信息；普通重读不创建提交上下文。切换异常或新的提交废弃旧上下文。刷新后从服务重建当前显示，不持久化前端待确认提示。

## 不变量

- 本机保存不修改 Databricks 任一源字段，也不影响同单其他异常。
- 一次写入的三个可变字段共同提交或共同回滚。
- 写入响应内部重读和前端独立 GET 分别执行；只有后者核对一致才有页面成功提示。
- 换存储文件是换记录集合；同库重启须保留同一文件。
