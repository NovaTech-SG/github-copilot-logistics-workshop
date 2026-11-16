# 数据模型
- Shipment：shipment_id唯一，carrier_id引用Carrier；status、planned_arrival、actual_arrival参与口径。
- Carrier：carrier_id、carrier_name。默认dev_databricks.default下shipments与carriers。
- Summary：shipment_count、eligible_count、on_time_count、delayed_count、excluded_count、on_time_rate。
- Scope：carrier_id可选；P2 page正整数，每页20条。NULL准时率前端显示N/A。
- 校验：0<=on_time<=eligible<=total；不关联一对多异常放大单量。
