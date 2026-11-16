# Dashboard HTTP Contract

**Status**: 设计合同，待后续任务实现 | **Spec**: [spec.md](../spec.md) | **Model**: [data-model.md](../data-model.md)

## 1. 浏览器接口

`GET /api/dashboard`，同源本地服务，默认 http://127.0.0.1:8767；接口只读。不接收 Token、SQL、Catalog、Schema 或源服务 URL 参数。

| 参数 | 类型 | 默认 | 规则 |
| --- | --- | --- | --- |
| carrier | string | 空字符串 | 空值表示全部；非空符合 ^[A-Za-z0-9_-]{1,64}$；不修剪、不变更大小写；未知但合法编号为成功空结果 |
| page | integer | 1 | 十进制数字且 1≤page≤2147483647；拒绝空值、负值、零、小数、正号及非数字；P1 仅接受 1，P2 允许其他合法页 |

每个参数最多出现一次，重复参数及未知参数返回 400。输入验证在调用业务源之前完成。scope.carrier 回显规范化筛选；page 的前导零可接受并规范为整数。

## 2. 成功响应（200，P1）

Content-Type: application/json; charset=utf-8，Cache-Control: no-store。下例只说明响应结构，不作为真实业务数据或固定运行结果。

```json
{
  "scope": {"carrier": "CAR_TEST"},
  "summary": {
    "total_count": 6,
    "eligible_count": 3,
    "on_time_count": 2,
    "delayed_count": 1,
    "excluded_count": 3,
    "on_time_rate": 66.67
  },
  "carriers": [
    {"carrier_id": "CAR_TEST", "carrier_name": "验收承运商"}
  ],
  "by_carrier": [
    {
      "carrier_id": "CAR_TEST",
      "carrier_name": "验收承运商",
      "total_count": 6,
      "eligible_count": 3,
      "on_time_count": 2,
      "delayed_count": 1,
      "excluded_count": 3,
      "on_time_rate": 66.67
    }
  ],
  "daily": [],
  "shipments": []
}
```

- scope、summary、carriers、by_carrier、daily、shipments 必填。P1 的 daily、shipments 必须为空数组，前端不展示对应模块。
- 计数均为非负整数；on_time_rate 是 0—100 的百分数，保留两位展示精度，分母为零传 null；禁止 NaN、Infinity 或字符串百分比。
- carriers 为全局可选列表，编号唯一、名称回退已处理、按编号升序。筛选不会缩减选项。
- by_carrier 只含当前范围有运输单的承运商，按编号升序；每项计数不变量与 summary 相同；各项计数加总等于 summary。
- 空范围仍是 200：summary 的所有计数为 0、on_time_rate=null，by_carrier=[]；carriers 仍为全局选项。前端依据 total_count=0 显示无记录，不依靠 HTTP 错误推断空业务范围。

## 3. P2 增量合同

保留 P1 字段并增加 pagination、source_snapshot_at、queried_at；daily 和 shipments 从空数组改为查询结果。P1 页面不依赖这些新增字段。

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| daily[].shipment_date | YYYY-MM-DD string | 当前范围最早至最晚业务日期逐自然日排列 |
| daily[].total_count | nonnegative integer | 当日单量，缺失日为 0 |
| pagination.page | positive integer | 实际返回页；非空范围请求超末页时钳制到末页，空范围为 1 |
| pagination.page_size | integer | 固定 20 |
| pagination.total_count | nonnegative integer | 等于 summary.total_count |
| pagination.total_pages | nonnegative integer | 总量除以 20 向上取整，空范围为 0 |
| source_snapshot_at | UTC ISO 8601 string / null | 当前范围最大非空 snapshot_at |
| queried_at | UTC ISO 8601 string | 本次后端成功解析并验证结果后的完成时刻 |

每个 shipments 条目至少包括：

| 字段 | 类型 | 语义 |
| --- | --- | --- |
| shipment_id | string | 运输单编号 |
| carrier_id / carrier_name | string | 承运商编号及名称回退值 |
| shipment_date | YYYY-MM-DD string | 业务日期 |
| origin_city / destination_city | string / null | 起讫城市，缺失时页面显示“—” |
| planned_arrival / actual_arrival | UTC ISO 8601 string / null | 到达时刻，使用 Z 后缀，缺失显示“—” |
| status | enum | DELIVERED、IN_TRANSIT、CANCELLED |
| result | enum | ON_TIME、DELAYED、IN_TRANSIT、CANCELLED、MISSING_TIMESTAMP，规则见数据模型 |

服务必须验证返回条数不超过 20；同一数据集合按 shipment_date、shipment_id 升序分页且无重复/遗漏。总量为零时 daily=[]、shipments=[]，分页按钮不可用，UI 显示“无记录”，不展示矛盾的页数。翻页保持范围，筛选变化、清除和刷新重置第 1 页。

时间在前端以 Asia/Shanghai 展示，并明确标注“源数据最新快照”和“查询完成时间”。源快照为 null 时不以其他时间填充。业务日期不做时区转换。

## 4. 错误响应

统一结构为 error 字符串；客户端优先展示安全错误文本，响应不是有效 JSON 时显示通用查询失败并允许重试。

```json
{"error": "查询未完成，请稍后重试。"}
```

| HTTP 状态 | 条件 | UI 行为 |
| --- | --- | --- |
| 400 | 参数格式、重复/未知参数或 P1 不支持的 page | 显示输入错误；不当作空范围 |
| 502 | MCP 无法连接、权限不足、执行失败、轮询预算耗尽、结果截断/分块/损坏或合同不符 | 显示查询失败、保留当前筛选、允许重试 |
| 500 | 未预期的内部程序错误 | 显示通用失败，不显示 traceback 或连接细节 |

当前起始骨架的 501 表示业务尚未实现，不属于最终合同；实现后不得用 501 作为正常看板状态。保留 400/502 的已有 Token 遮蔽机制；连接相关异常在服务边界转换为安全 DataError。

## 5. Python 与 MCP 内部合同

- build_query(prefix, carrier="", page=1) 返回一个固定业务形状的 SELECT/WITH 查询字符串；无连接副作用。prefix 必须符合已校验的双层标识符，业务参数按第 1 节规则校验。P1 不计算趋势和明细；P2 同查询扩展。
- get_dashboard(settings, carrier="", page=1) 为同步入口，验证参数后桥接异步 MCP，只读执行并验证结构，返回符合 HTTP 成功结构的字典。输入错误抛 ValueError，数据读取错误抛 DataError。
- 连接模块调用仅为 execute_sql_read_only，异步未完成时调用 poll_sql_result；复用 connect 的初始化与工具发现，不调用写工具。
- SQL 结果必须是一行一列，列名 dashboard_json，内容为包含 summary/carriers/by_carrier/daily/shipments 的 JSON 对象。scope 可由服务附加；P2 queried_at 由服务附加。禁止双重包装为 dashboard 或 data，防止前后端合同漂移。
- extract_dashboard 先检查原始 SQL 信封；业务服务再校验嵌套字段、类型、计数及比例不变量。数组为 []，不是 null；所有时刻保留时区。
- 使用有序聚合或显式排序保证 by_carrier、daily、shipments 的 JSON 数组顺序，不能依赖无序集合聚合的偶然顺序。

## 6. 界面消费约束

请求序号同时保护成功、失败和 finally 更新；只允许最新请求改变页面。发起请求显示加载，成功后同时替换范围与全部结果组件。错误和名称经 textContent 渲染。网络中断、无效响应和源错误均不能显示固定业务数据；重试继续使用当前筛选（P2 翻页失败则保持目标页）。
