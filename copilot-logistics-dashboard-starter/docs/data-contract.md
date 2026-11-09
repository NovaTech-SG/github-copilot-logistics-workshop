# 数据返回约定

浏览器只请求本地 `/api/dashboard?carrier=CAR002&page=1`，不直接连接Databricks，也不持有Token。空carrier表示全部。

## 已提供的连接模块

- `Settings.table_prefix`：经过标识符校验并加引号的Catalog/Schema。
- `connect(settings)`：异步上下文，创建MCP会话并确认只读/轮询工具存在。
- `execute_read_only(session, query)`：返回 `(SQL响应, 轮询次数)`；处理成功、等待、失败和超时。
- `extract_dashboard(response)`：可选的现成解析器，接受只有一列 `dashboard_json` 的单行JSON查询结果；拒绝截断和不完整响应。

若使用现成解析器，SQL可用 `to_json(named_struct(...)) AS dashboard_json` 组织一行结果，避免大量明细占满MCP返回。顶层必须含summary、carriers、by_carrier、daily、shipments。基础阶段未实现趋势和明细时，daily、shipments返回空数组，页面不展示这两个模块；扩展后再填充，不宣称空数组代表已查询出零条记录。

## 基础返回字段

| 字段 | 内容 |
|---|---|
| summary.shipment_count | 总运输单量 |
| summary.eligible_count | 有效分母 |
| summary.on_time_count | 准时量 |
| summary.delayed_count | 延误量 |
| summary.excluded_count | 排除量 |
| summary.on_time_rate | 0到1的小数或NULL；显示时转百分比 |
| carriers | 全部可用承运商，每项含carrier_id、carrier_name，用于筛选 |
| by_carrier | 当前范围的承运商汇总，每项含carrier_id、shipment_count、eligible_count、on_time_count、on_time_rate |
| selected_carrier / scope | 当前编号与可读范围名，可由后端补充 |
| source | 查询完成时间、耗时、statement_id等追踪信息，可由后端补充；不能包含Token |

SQL参数仅允许合法承运商编号，页码为正整数且设上限。不要拼接浏览器提供的任意SQL。单元测试可以使用构造数据，运行时不能把测试样例作为数据源。

## 扩展字段

| 字段 | 内容 |
|---|---|
| daily | date（YYYY-MM-DD）与count；后端补齐缺失自然日 |
| shipments | 当前页明细：shipment_id、carrier_id、shipment_date、线路、计划/实际到达时间和运输结果 |
| page / page_size / page_count | 当前页、每页条数与总页数 |
| snapshot_epoch | 数据快照Unix秒数；浏览器按Asia/Shanghai显示 |
| summary.missing_timestamp_count | DELIVERED但缺少计划或实际到达时间的单量 |

使用epoch传输时间可减少SQL会话时区与浏览器时区差异。NULL时间显示空占位，不显示1970年。

完成代码可以采用其他明确的数据契约，但必须同步后端、页面、测试和文档，并保留只读、截断检查和实际MCP结果要求。
