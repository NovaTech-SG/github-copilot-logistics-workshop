"""读取完整只读结果，在交给浏览器前验证业务合同。"""

import asyncio
import math
import re
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from services.mcp_sql import DataError, connect, execute_read_only, extract_dashboard
from services.queries import PAGE_SIZE, build_query, validate_params


COUNTS = ("total_count", "eligible_count", "on_time_count", "delayed_count", "excluded_count")


def _require(condition):
    if not condition:
        raise DataError("查询结果不符合看板数据约定，请重新查询。")


def _integer(value):
    _require(type(value) is int and value >= 0)
    return value


def _day(value):
    _require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    return date.fromisoformat(value)


def _instant(value, nullable=True):
    if value is None and nullable:
        return None
    _require(isinstance(value, str) and value.endswith("Z"))
    parsed = datetime.fromisoformat(value)
    _require(parsed.utcoffset() == timedelta(0))
    return parsed


def _metrics(item):
    _require(isinstance(item, dict))
    total, eligible, on_time, delayed, excluded = [_integer(item[key]) for key in COUNTS]
    _require(on_time <= eligible <= total and delayed == eligible - on_time and excluded == total - eligible)
    rate = item["on_time_rate"]
    if eligible == 0:
        _require(rate is None)
    else:
        _require(type(rate) in (int, float) and math.isfinite(rate) and 0 <= rate <= 100)
        expected = float((Decimal(on_time) * 100 / eligible).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        _require(abs(rate - expected) < 0.000001)


def _carrier(item):
    _require(isinstance(item, dict))
    identifier = item["carrier_id"]
    _require(isinstance(identifier, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", identifier))
    _require(isinstance(item["carrier_name"], str) and bool(item["carrier_name"].strip()))
    return identifier


def _validate(data, carrier, requested_page):
    _require(isinstance(data, dict) and _integer(data.get("invalid_count", 0)) == 0)
    summary = data["summary"]
    _metrics(summary)
    for key in ("carriers", "by_carrier", "daily", "shipments"):
        _require(isinstance(data[key], list))
    carrier_ids = [_carrier(item) for item in data["carriers"]]
    _require(carrier_ids == sorted(set(carrier_ids)))
    comparison_ids = []
    for item in data["by_carrier"]:
        identifier = _carrier(item)
        comparison_ids.append(identifier)
        _metrics(item)
        _require(item["total_count"] > 0 and identifier in carrier_ids and (not carrier or identifier == carrier))
    _require(comparison_ids == sorted(set(comparison_ids)))
    for key in COUNTS:
        _require(sum(item[key] for item in data["by_carrier"]) == summary[key])

    previous_day = None
    for item in data["daily"]:
        _require(isinstance(item, dict))
        current_day = _day(item["shipment_date"])
        _require(previous_day is None or current_day == previous_day + timedelta(days=1))
        _integer(item["total_count"])
        previous_day = current_day
    _require(sum(item["total_count"] for item in data["daily"]) == summary["total_count"])
    if data["daily"]:
        _require(data["daily"][0]["total_count"] > 0 and data["daily"][-1]["total_count"] > 0)
    else:
        _require(summary["total_count"] == 0)

    pagination = data["pagination"]
    _require(isinstance(pagination, dict))
    for key in ("page", "page_size", "total_count", "total_pages"):
        _integer(pagination[key])
    total = summary["total_count"]
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    page = min(requested_page, total_pages) if total_pages else 1
    _require(pagination == dict(page=page, page_size=PAGE_SIZE, total_count=total, total_pages=total_pages))
    _require(len(data["shipments"]) == min(PAGE_SIZE, max(0, total - (page - 1) * PAGE_SIZE)))

    identifiers = []
    ordering = []
    for item in data["shipments"]:
        identifier = _carrier(item)
        _require(identifier in comparison_ids and (not carrier or identifier == carrier))
        shipment_id = item["shipment_id"]
        _require(isinstance(shipment_id, str) and bool(shipment_id))
        identifiers.append(shipment_id)
        business_day = _day(item["shipment_date"])
        ordering.append((business_day, shipment_id))
        _require(data["daily"][0]["shipment_date"] <= item["shipment_date"] <= data["daily"][-1]["shipment_date"])
        for key in ("origin_city", "destination_city"):
            _require(item[key] is None or isinstance(item[key], str))
        planned = _instant(item["planned_arrival"])
        actual = _instant(item["actual_arrival"])
        status = item["status"]
        _require(status in {"DELIVERED", "IN_TRANSIT", "CANCELLED"})
        if status in {"IN_TRANSIT", "CANCELLED"}:
            expected_result = status
        elif planned is None or actual is None:
            expected_result = "MISSING_TIMESTAMP"
        else:
            expected_result = "ON_TIME" if actual <= planned else "DELAYED"
        _require(item["result"] == expected_result)
    _require(ordering == sorted(ordering) and len(set(identifiers)) == len(identifiers))
    _instant(data["source_snapshot_at"])
    if total == 0:
        _require(data["source_snapshot_at"] is None)
    data.pop("invalid_count", None)
    data["scope"] = {"carrier": carrier}
    data["queried_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return data


def get_dashboard(settings, carrier="", page=1):
    validate_params(carrier, page)
    query = build_query(settings.table_prefix, carrier, page)

    async def read():
        async with connect(settings) as session:
            response, _ = await execute_read_only(session, query)
        _require(response.get("manifest", {}).get("total_chunk_count", 1) == 1)
        return _validate(extract_dashboard(response), carrier, page)

    try:
        return asyncio.run(read())
    except Exception as error:
        raise DataError("数据查询失败或结果不完整，请检查连接、权限或稍后重试。") from error
