# HTTP与数据合同
- GET /api/dashboard?carrier=CAR002：carrier可空，仅使用固定只读SQL和参数校验。
- P1必须返回summary、carriers、by_carrier和source；已提供解析器要求的daily、shipments等结构参照services/mcp_sql.py和docs/data-contract.md，不私自改变协议。
- P2 page默认1，每页20条；筛选改变回1。扩展使用daily、shipments、page与page_count。
- 各组件范围相同；on_time_rate为0到1的比率或NULL，不直接把百分比当比率。
- source描述查询来源及时间，不含Token；连接或完整性失败返回可识别错误，不能返回固定成功数据。
