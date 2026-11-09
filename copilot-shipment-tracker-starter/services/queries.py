"""仅生成固定的只读SQL；异常作为行，不按运输单去重。"""
import re


def validate_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value):
        raise ValueError("异常编号格式无效。")
    return value


def build_query(prefix, exception_id=None):
    condition = f"WHERE e.exception_id='{validate_id(exception_id)}'" if exception_id is not None else ""
    return f"""WITH records AS (
 SELECT e.exception_id,e.shipment_id,e.exception_type,e.handling_status,
   e.follow_up_note,e.assigned_team,unix_timestamp(e.detected_at) AS detected_epoch,
   s.carrier_id,c.carrier_name,s.origin_city,s.destination_city
 FROM {prefix}.exceptions e
 LEFT JOIN {prefix}.shipments s ON e.shipment_id=s.shipment_id
 LEFT JOIN {prefix}.carriers c ON s.carrier_id=c.carrier_id
 {condition}
), limited AS (SELECT * FROM records ORDER BY exception_id LIMIT 500)
SELECT to_json(named_struct(
 'total_count',(SELECT COUNT(*) FROM records),
 'rows',(SELECT array_sort(collect_list(named_struct(
   'exception_id',exception_id,'shipment_id',shipment_id,'exception_type',exception_type,
   'handling_status',handling_status,'follow_up_note',follow_up_note,'assigned_team',assigned_team,
   'detected_epoch',detected_epoch,'carrier_id',carrier_id,'carrier_name',carrier_name,
   'origin_city',origin_city,'destination_city',destination_city))) FROM limited)
),map('ignoreNullFields','false')) AS tracker_json"""
