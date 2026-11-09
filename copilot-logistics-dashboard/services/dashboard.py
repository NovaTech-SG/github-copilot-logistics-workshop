import asyncio
import math
import time
from datetime import date, datetime, timedelta, timezone

from .mcp_sql import DataError, connect, execute_read_only, extract_dashboard
from .queries import PAGE_SIZE, build_query


def prepare(data, carrier, page):
    """整理MCP返回数据；不从本地读取任何业务数据。"""
    summary = data["summary"]
    total = summary["shipment_count"]
    eligible = summary["eligible_count"]
    on_time = summary["on_time_count"]
    if not 0 <= on_time <= eligible <= total:
        raise DataError("查询返回的指标不满足分子、分母与总量关系。")
    if summary["delayed_count"] != eligible - on_time or summary["excluded_count"] != total - eligible:
        raise DataError("查询返回的延误量或排除量不一致。")
    expected_rate = on_time / eligible if eligible else None
    actual_rate = summary.get("on_time_rate")
    if (expected_rate is None and actual_rate is not None) or (expected_rate is not None and (actual_rate is None or not math.isclose(float(actual_rate), expected_rate, abs_tol=1e-10))):
        raise DataError("准时率与返回的分子分母不一致。")
    if sum(row["count"] for row in data["daily"]) != total:
        raise DataError("每日趋势合计与运输单量不一致。")
    if sum(row["shipment_count"] for row in data["by_carrier"]) != total:
        raise DataError("承运商汇总与运输单量不一致。")
    expected_rows = min(PAGE_SIZE, max(0, total - (page-1)*PAGE_SIZE))
    if len(data["shipments"]) != expected_rows:
        raise DataError("当前页运输明细不完整。")
    if carrier and any(row["carrier_id"] != carrier for row in data["shipments"]):
        raise DataError("明细与承运商筛选范围不一致。")
    days = {row["date"]: row["count"] for row in data["daily"]}
    if days:
        day, end = date.fromisoformat(min(days)), date.fromisoformat(max(days))
        while day <= end:
            days.setdefault(day.isoformat(), 0)
            day += timedelta(days=1)
    names = {row["carrier_id"]: row["carrier_name"] for row in data["carriers"]}
    for row in data["by_carrier"] + data["shipments"]:
        row["carrier_name"] = names.get(row["carrier_id"], row["carrier_id"])
    data.update({
        "scope": names.get(carrier, carrier) if carrier else "全部承运商",
        "selected_carrier": carrier,
        "page": page,
        "page_size": PAGE_SIZE,
        "page_count": max(1, math.ceil(total/PAGE_SIZE)),
        "daily": [{"date": day, "count": count} for day, count in sorted(days.items())],
    })
    return data


async def fetch_dashboard(settings, carrier="", page=1):
    query = build_query(settings.table_prefix, carrier, page)
    start = time.monotonic()
    async with connect(settings) as session:
        response, polls = await execute_read_only(session, query)
    data = prepare(extract_dashboard(response), carrier, page)
    data["source"] = {
        "name": "Databricks MCP",
        "tool": "execute_sql_read_only",
        "statement_id": response.get("statement_id"),
        "poll_count": polls,
        "queried_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": round((time.monotonic()-start)*1000),
    }
    return data


def get_dashboard(settings, carrier="", page=1):
    build_query(settings.table_prefix, carrier, page)
    try:
        return asyncio.run(fetch_dashboard(settings, carrier, page))
    except Exception as error:
        def messages(exc):
            if isinstance(exc, BaseExceptionGroup):
                return [message for nested in exc.exceptions for message in messages(nested)]
            return [str(exc)]
        text = "；".join(dict.fromkeys(messages(error))).replace(settings.token, "[REDACTED]")
        raise DataError(text or "Databricks MCP 查询失败。") from None
