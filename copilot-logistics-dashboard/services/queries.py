"""固定的只读查询。分页在SQL完成，每次返回一行JSON，减少MCP上下文截断。"""
import re

PAGE_SIZE = 20


def build_query(prefix, carrier="", page=1):
    if carrier and not re.fullmatch(r"CAR\d{3}", carrier):
        raise ValueError("承运商编号格式无效。")
    if isinstance(page, bool) or not isinstance(page, int) or not 1 <= page <= 10000:
        raise ValueError("页码必须为1到10000的整数。")
    condition = f"WHERE carrier_id = '{carrier}'" if carrier else ""
    start = (page - 1) * PAGE_SIZE
    return f"""WITH filtered AS (
  SELECT * FROM {prefix}.shipments {condition}
), tagged AS (
  SELECT *,
    CASE WHEN status='DELIVERED' AND planned_arrival IS NOT NULL AND actual_arrival IS NOT NULL THEN 1 ELSE 0 END AS eligible,
    CASE WHEN status='DELIVERED' AND planned_arrival IS NOT NULL AND actual_arrival IS NOT NULL AND actual_arrival<=planned_arrival THEN 1 ELSE 0 END AS on_time
  FROM filtered
), totals AS (
  SELECT COUNT(*) AS shipment_count,
    COALESCE(SUM(eligible),0) AS eligible_count,
    COALESCE(SUM(on_time),0) AS on_time_count,
    COUNT_IF(status='DELIVERED') AS delivered_count,
    COUNT_IF(status='DELIVERED' AND eligible=0) AS missing_timestamp_count
  FROM tagged
), by_carrier AS (
  SELECT carrier_id, COUNT(*) AS shipment_count, SUM(eligible) AS eligible_count, SUM(on_time) AS on_time_count
  FROM tagged GROUP BY carrier_id
), daily AS (
  SELECT shipment_date, COUNT(*) AS shipment_count FROM filtered GROUP BY shipment_date
), numbered AS (
  SELECT *, ROW_NUMBER() OVER(ORDER BY shipment_date DESC,shipment_id DESC) AS position
  FROM tagged
), page_rows AS (
  SELECT * FROM numbered WHERE position>{start} AND position<={start+PAGE_SIZE}
)
SELECT to_json(named_struct(
  'summary', (SELECT named_struct(
    'shipment_count',shipment_count,'eligible_count',eligible_count,'on_time_count',on_time_count,
    'delayed_count',eligible_count-on_time_count,'excluded_count',shipment_count-eligible_count,
    'delivered_count',delivered_count,'missing_timestamp_count',missing_timestamp_count,
    'on_time_rate',1.0*on_time_count/NULLIF(eligible_count,0)) FROM totals),
  'carriers', (SELECT array_sort(collect_list(named_struct('carrier_id',carrier_id,'carrier_name',carrier_name))) FROM {prefix}.carriers),
  'by_carrier', (SELECT array_sort(collect_list(named_struct(
    'carrier_id',carrier_id,'shipment_count',shipment_count,'eligible_count',eligible_count,'on_time_count',on_time_count,
    'on_time_rate',1.0*on_time_count/NULLIF(eligible_count,0)))) FROM by_carrier),
  'daily', (SELECT array_sort(collect_list(named_struct('date',CAST(shipment_date AS STRING),'count',shipment_count))) FROM daily),
  'shipments', (SELECT array_sort(collect_list(named_struct(
    'position',position,'shipment_id',shipment_id,'carrier_id',carrier_id,'shipment_date',CAST(shipment_date AS STRING),
    'origin_city',origin_city,'destination_city',destination_city,
    'planned_epoch',unix_timestamp(planned_arrival),'actual_epoch',unix_timestamp(actual_arrival),
    'result',CASE WHEN status='CANCELLED' THEN 'CANCELLED' WHEN status='IN_TRANSIT' THEN 'IN_TRANSIT'
      WHEN eligible=0 THEN 'MISSING_TIMESTAMP' WHEN on_time=1 THEN 'ON_TIME' ELSE 'DELAYED' END
  ))) FROM page_rows),
  'snapshot_epoch', (SELECT MAX(unix_timestamp(snapshot_at)) FROM {prefix}.shipments)
),map('ignoreNullFields','false')) AS dashboard_json"""
