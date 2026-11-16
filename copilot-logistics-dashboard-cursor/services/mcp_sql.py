import asyncio
import json
import time
from contextlib import asynccontextmanager
from datetime import timedelta

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class DataError(Exception):
    """可展示给用户的数据读取错误。"""


def decode_tool(result):
    if result.isError:
        text = " ".join(block.text for block in result.content if getattr(block, "type", None) == "text")
        raise DataError(text or "MCP 工具执行失败。")
    if result.structuredContent is not None:
        return result.structuredContent
    for block in result.content:
        if getattr(block, "type", None) == "text":
            try:
                return json.loads(block.text)
            except (ValueError, TypeError):
                continue
    raise DataError("MCP 未返回可解析的结构化结果。")


@asynccontextmanager
async def connect(settings):
    async with httpx.AsyncClient(headers={"Authorization": f"Bearer {settings.token}"}, timeout=httpx.Timeout(30,read=120), follow_redirects=False) as http:
        async with streamable_http_client(settings.url, http_client=http) as (read, write, _):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=125)) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = {tool.name for tool in tools.tools}
                if not {"execute_sql_read_only", "poll_sql_result"}.issubset(names):
                    raise DataError("此 MCP 未提供所需的只读 SQL 与轮询工具。")
                yield session


async def probe(settings):
    async with connect(settings) as session:
        result = await session.call_tool("execute_sql_read_only", {"query": "SELECT 1 AS result"})
        return result.model_dump(mode="json", exclude_none=True)


async def execute_read_only(session, query, timeout=90):
    """只调用只读工具；异步SQL由官方轮询工具收尾。"""
    response = decode_tool(await session.call_tool("execute_sql_read_only", {"query": query}))
    deadline = time.monotonic() + timeout
    polls = 0
    while True:
        status = response.get("status", {})
        state = status.get("state") if isinstance(status, dict) else status
        if state == "SUCCEEDED":
            return response, polls
        if state in {"FAILED", "CANCELED", "CLOSED"}:
            detail = status.get("error", {}).get("message", "SQL 未成功完成。") if isinstance(status, dict) else "SQL 未成功完成。"
            raise DataError(detail)
        statement_id = response.get("statement_id")
        if state not in {"PENDING", "RUNNING"} or not statement_id:
            raise DataError("MCP 返回了无法识别的SQL状态。")
        if time.monotonic() >= deadline:
            raise DataError("查询仍未完成，请稍后重新查询。")
        await asyncio.sleep(0.5)
        response = decode_tool(await session.call_tool("poll_sql_result", {"statement_id": statement_id}))
        polls += 1


def extract_dashboard(response):
    """拒绝截断、分块或结构异常的结果，避免展示不完整数据。"""
    manifest = response.get("manifest", {})
    if response.get("truncated") or manifest.get("truncated"):
        raise DataError("MCP 查询结果被截断，未展示不完整的数据。")
    if manifest.get("total_row_count") != 1 or response.get("returned_row_count", 1) != 1:
        raise DataError("预期一行Dashboard结构化结果，实际返回行数不符。")
    columns = manifest.get("schema", {}).get("columns", [])
    if len(columns) != 1 or columns[0].get("name") != "dashboard_json":
        raise DataError("MCP 结果字段与Dashboard数据约定不符。")
    chunk = response.get("result", {})
    if "data_typed_array" in chunk:
        rows = chunk["data_typed_array"]
        if len(rows) != 1 or len(rows[0].get("values", [])) != 1:
            raise DataError("MCP 结果缺少完整的数据单元格。")
        raw = rows[0]["values"][0].get("str")
    else:
        rows = chunk.get("data_array", [])
        raw = rows[0][0] if len(rows) == 1 and len(rows[0]) == 1 else None
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        raise DataError("MCP 返回的Dashboard JSON无效或不完整。") from None
    if not isinstance(data, dict) or not {"summary", "carriers", "by_carrier", "daily", "shipments"}.issubset(data):
        raise DataError("MCP 返回结果缺少Dashboard所需字段。")
    return data
