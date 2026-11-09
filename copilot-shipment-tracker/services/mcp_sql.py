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


def extract_records(response):
    manifest = response.get('manifest', {})
    if response.get('truncated') or manifest.get('truncated'):
        raise DataError('MCP结果被截断，请缩小演示数据范围。')
    columns = manifest.get('schema', {}).get('columns', [])
    if manifest.get('total_row_count') != 1 or response.get('returned_row_count', 1) != 1 or len(columns) != 1 or columns[0].get('name') != 'tracker_json':
        raise DataError('MCP结果与异常列表数据约定不符。')
    chunk = response.get('result', {})
    typed = chunk.get('data_typed_array')
    raw = None
    if typed is not None:
        if len(typed) == 1 and len(typed[0].get('values', [])) == 1:
            raw = typed[0]['values'][0].get('str')
    else:
        rows = chunk.get('data_array', [])
        if len(rows) == 1 and len(rows[0]) == 1:
            raw = rows[0][0]
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        raise DataError('MCP异常列表JSON无效。') from None
    if not isinstance(data, dict) or not isinstance(data.get('rows'), list) or data.get('total_count') != len(data['rows']):
        raise DataError('异常列表不完整，未展示部分结果。')
    rows = data['rows']
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or not {'exception_id','shipment_id','handling_status','exception_type'}.issubset(row):
            raise DataError('异常记录缺少必要字段。')
        if row['exception_id'] in seen or row['handling_status'] not in {'OPEN','IN_PROGRESS','RESOLVED'}:
            raise DataError('异常编号重复或源处理状态无效。')
        seen.add(row['exception_id'])
    return rows
