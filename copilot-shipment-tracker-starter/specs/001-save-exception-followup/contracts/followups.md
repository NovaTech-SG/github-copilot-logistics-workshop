# Follow-up HTTP and UI Contract

作用范围：本机 127.0.0.1 服务与已有页面。保留既有接口，不新增源写入能力。参见[模型](../data-model.md)和[计划](../plan.md)。以下示例仅为契约示意，不是实时业务结果。

## POST /api/exceptions/{exception_id}

Content-Type: application/json。沿用现有 1–16384 字节请求体限制；异常编号遵守既有校验。

```json
{
  "status": "IN_PROGRESS",
  "note": "已联系承运商，等待补充到达时间。",
  "expected_status": "OPEN"
}
```

- 三个字段必填，状态均为三种合法状态之一，note 必须是字符串。
- 服务先沿用只读源查询取得目标异常，再进入本机写事务。有效但过期的 expected_status 拒绝覆盖；相同原状态下继续校验合法推进和规范化备注。
- 成功返回 200，结构沿用 Tracker.update：

```json
{
  "record": {
    "exception_id": "EXC00001",
    "handling_status": "IN_PROGRESS",
    "follow_up_note": "已联系承运商，等待补充到达时间。",
    "source_handling_status": "OPEN",
    "saved_locally": true,
    "local_updated_at": "2026-11-16T13:10:00+00:00"
  },
  "source": {
    "name": "Databricks MCP",
    "tool": "execute_sql_read_only"
  },
  "saved_to": "local"
}
```

示例省略既有运输背景和 source 元数据；实际 record 必须是完整合并记录。来源元数据仍描述本次源读取，不表示该 POST 已经通过前端重读确认。local_updated_at 是服务本机保存时间，不能用前端生成时间替代。

## GET /api/exceptions/{exception_id}

沿用既有 Tracker.detail，返回 200：`{"record": <完整合并记录>, "source": <查询元数据>}`。重新读取只读源，在源记录上叠加该异常的本机跟进记录并返回合并结果；不修改源数据或本机数据库。页面必须在 POST 成功后独立调用此 GET，且使用提交时捕获的异常编号。

核对条件同时满足：

1. record.exception_id 与提交编号相等。
2. record.handling_status 与提交目标状态相等。
3. record.follow_up_note 与提交前去首尾空格后的备注相等。

任一不匹配、缺字段或 GET 失败均不可报保存确认成功。成功后 replaceRecord 更新本机队列中的对应异常，并重算已有筛选、概览及分页；不得从 POST 输入构造假详情。

## GET /api/exceptions

沿用既有全量只读查询及本机 overlay，返回 `rows` 和 `source`。最多 500 条保护保持不变，不新增分页接口。查询行仅为 FR-010 增补 source_updated_epoch（可为 null），不改变其他字段语义。

## 错误响应

沿用 `{"error": "可理解的错误信息"}`，不输出 Token 或 SQL 连接凭据。

| 状态码 | 语义 | 页面行为 |
| --- | --- | --- |
| 400 | 无效编号、请求体、状态、备注或非法推进 | 显示校验失败，不自动重试写入 |
| 404 | 未找到异常或接口 | 提示不可保存或读取该异常 |
| 409 | 原状态已过期 | 拒绝覆盖，提示重新读取后再跟进 |
| 500 | 本机读写失败 | 不宣称成功，提供重新读取入口 |
| 502 | 源查询失败 | 不使用固定数据兜底，提示重新读取 |

当前起始版 501 表示尚未实现；实施后合法请求应进入保存流程。任意非 2xx 不显示成功。500 也可能来自提交完成后的重读失败，不能仅凭该响应断言没有写入；网络中断或响应解析失败同样可能未获提交确认，页面应说明结果未确认。

## 页面交互状态

| 阶段 | 可见反馈及约束 |
| --- | --- |
| 可编辑 | 基于当前 selected 生成原状态与目标选项 |
| 正在保存 | setBusy(true)，冻结编辑、保存和重读，阻止重入 |
| 正在核对 | POST 已成功，独立 GET 同一编号；仍保持 busy |
| 已确认 | 替换真实重读记录后显示“已保存到本机，并重新读取确认” |
| 提交被拒绝 | 明确失败原因，恢复操作，不冒称已保存 |
| 结果未确认 | 有成功响应则说明“已提交但尚未确认”；结果未知则说明“提交结果未确认”；可重新读取核对 |

finally 恢复 setBusy(false)。失败路径保留用户草稿，不用未经确认的 POST 内容修改 records。读取到实际记录但不匹配时可展示真实内容，提示仍为未确认，保留原提交快照供后续核对。手动重读有待确认上下文时重复上述三项匹配，无上下文时只报告读取完成。切换异常及新提交不能复用旧上下文，避免迟到响应确认错对象。

备注长度以后端 Python len(trimmed_note) 为准。原生 textarea 的 maxlength 保持现有行为，不新定义字节长度、富文本或备注历史。
