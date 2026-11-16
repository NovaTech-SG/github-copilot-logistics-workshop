"""固定只读查询：指标、同范围趋势与查询侧分页。"""

import re


PAGE_SIZE = 20
MAX_PAGE = 2147483647


def validate_params(carrier="", page=1):
    if not isinstance(carrier, str) or (carrier and not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", carrier)):
        raise ValueError("承运商编号只能包含 1—64 个字母、数字、下划线或短横线。")
    if type(page) is not int or not 1 <= page <= MAX_PAGE:
        raise ValueError("页码必须为 1—2147483647 的整数。")
    return carrier, page


def _metrics(alias):
    return f"""'total_count', {alias}.total_count,
        'eligible_count', {alias}.eligible_count, 'on_time_count', {alias}.on_time_count,
        'delayed_count', {alias}.eligible_count - {alias}.on_time_count,
        'excluded_count', {alias}.total_count - {alias}.eligible_count,
        'on_time_rate', CASE WHEN {alias}.eligible_count > 0
          THEN round(100.0 * {alias}.on_time_count / {alias}.eligible_count, 2) ELSE NULL END"""


def _utc(column):
    return f"date_format(to_utc_timestamp({column}, current_timezone()), 'yyyy-MM-dd\\'T\\'HH:mm:ss.SSS\\'Z\\'')"


def build_query(prefix, carrier="", page=1):
    validate_params(carrier, page)
    if not isinstance(prefix, str) or not re.fullmatch(r"`[A-Za-z_][A-Za-z0-9_]*`\.`[A-Za-z_][A-Za-z0-9_]*`", prefix):
        raise ValueError("表名前缀必须是经校验的 Catalog 和 Schema。")
    predicate = f"carrier_id = '{carrier}'" if carrier else "TRUE"
    return f"""WITH source_shipments AS (
      SELECT shipment_id, carrier_id, shipment_date, origin_city, destination_city,
        planned_arrival, actual_arrival, status, snapshot_at
      FROM {prefix}.`shipments`
    ), carrier_names AS (
      SELECT carrier_id, coalesce(min(nullif(trim(carrier_name), '')), carrier_id) AS carrier_name
      FROM {prefix}.`carriers` WHERE carrier_id IS NOT NULL GROUP BY carrier_id
    ), carrier_ids AS (
      SELECT carrier_id FROM carrier_names UNION
      SELECT carrier_id FROM source_shipments WHERE carrier_id IS NOT NULL
    ), carrier_options AS (
      SELECT i.carrier_id, coalesce(n.carrier_name, i.carrier_id) AS carrier_name
      FROM carrier_ids i LEFT JOIN carrier_names n ON i.carrier_id = n.carrier_id
    ), scoped AS (
      SELECT *, status = 'DELIVERED' AND planned_arrival IS NOT NULL
        AND actual_arrival IS NOT NULL AS eligible,
        status = 'DELIVERED' AND planned_arrival IS NOT NULL AND actual_arrival IS NOT NULL
        AND actual_arrival <= planned_arrival AS on_time
      FROM source_shipments WHERE {predicate}
    ), totals AS (
      SELECT count(*) AS total_count, count_if(eligible) AS eligible_count,
        count_if(on_time) AS on_time_count, max(snapshot_at) AS source_snapshot_at,
        count_if(shipment_id IS NULL OR carrier_id IS NULL OR shipment_date IS NULL
          OR status IS NULL OR status NOT IN ('DELIVERED','IN_TRANSIT','CANCELLED'))
          + count(*) - count(DISTINCT shipment_id) AS invalid_count
      FROM scoped
    ), carrier_totals AS (
      SELECT carrier_id, count(*) AS total_count, count_if(eligible) AS eligible_count,
        count_if(on_time) AS on_time_count FROM scoped GROUP BY carrier_id
    ), comparison AS (
      SELECT sort_array(collect_list(named_struct('carrier_id', t.carrier_id,
        'carrier_name', coalesce(n.carrier_name, t.carrier_id), {_metrics('t')}))) AS rows
      FROM carrier_totals t LEFT JOIN carrier_names n ON t.carrier_id = n.carrier_id
    ), options AS (
      SELECT sort_array(collect_list(named_struct('carrier_id', carrier_id,
        'carrier_name', carrier_name))) AS rows FROM carrier_options
    ), daily_counts AS (
      SELECT shipment_date, count(*) AS total_count FROM scoped GROUP BY shipment_date
    ), date_bounds AS (
      SELECT min(shipment_date) AS first_date, max(shipment_date) AS last_date FROM scoped
    ), calendar AS (
      SELECT explode(CASE WHEN first_date IS NULL THEN cast(array() AS ARRAY<DATE>)
        ELSE sequence(first_date, last_date, INTERVAL 1 DAY) END) AS shipment_date FROM date_bounds
    ), daily AS (
      SELECT sort_array(collect_list(named_struct('shipment_date', cast(c.shipment_date AS STRING),
        'total_count', coalesce(d.total_count, 0)))) AS rows
      FROM calendar c LEFT JOIN daily_counts d ON c.shipment_date = d.shipment_date
    ), pagination AS (
      SELECT CASE WHEN total_count = 0 THEN 1 ELSE least({page},
        cast(ceil(total_count / {PAGE_SIZE}.0) AS BIGINT)) END AS page,
        cast(ceil(total_count / {PAGE_SIZE}.0) AS BIGINT) AS total_pages FROM totals
    ), ranked AS (
      SELECT *, row_number() OVER (ORDER BY shipment_date, shipment_id) AS row_num FROM scoped
    ), page_rows AS (
      SELECT r.* FROM ranked r CROSS JOIN pagination p
      WHERE r.row_num > (p.page - 1) * {PAGE_SIZE} AND r.row_num <= p.page * {PAGE_SIZE}
    ), details AS (
      SELECT sort_array(collect_list(named_struct('shipment_date', cast(r.shipment_date AS STRING),
        'shipment_id', r.shipment_id, 'carrier_id', r.carrier_id,
        'carrier_name', coalesce(n.carrier_name, r.carrier_id),
        'origin_city', r.origin_city, 'destination_city', r.destination_city,
        'planned_arrival', {_utc('r.planned_arrival')},
        'actual_arrival', {_utc('r.actual_arrival')}, 'status', r.status,
        'result', CASE WHEN r.status = 'IN_TRANSIT' THEN 'IN_TRANSIT'
          WHEN r.status = 'CANCELLED' THEN 'CANCELLED'
          WHEN NOT r.eligible THEN 'MISSING_TIMESTAMP'
          WHEN r.on_time THEN 'ON_TIME' ELSE 'DELAYED' END))) AS rows
      FROM page_rows r LEFT JOIN carrier_names n ON r.carrier_id = n.carrier_id
    )
    SELECT to_json(named_struct('summary', named_struct({_metrics('t')}),
      'carriers', o.rows, 'by_carrier', c.rows, 'daily', d.rows, 'shipments', s.rows,
      'pagination', named_struct('page', p.page, 'page_size', {PAGE_SIZE},
        'total_count', t.total_count, 'total_pages', p.total_pages),
      'source_snapshot_at', {_utc('t.source_snapshot_at')},
      'invalid_count', t.invalid_count), map('ignoreNullFields','false')) AS dashboard_json
    FROM totals t CROSS JOIN comparison c CROSS JOIN options o CROSS JOIN daily d
      CROSS JOIN pagination p CROSS JOIN details s"""
