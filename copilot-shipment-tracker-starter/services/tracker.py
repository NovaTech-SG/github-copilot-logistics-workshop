import asyncio
import time
from datetime import datetime, timezone

from .mcp_sql import DataError, connect, execute_read_only, extract_records
from .queries import build_query


class NotFoundError(Exception):
    pass


async def fetch_source(settings, exception_id=None):
    query = build_query(settings.table_prefix, exception_id)
    start = time.monotonic()
    async with connect(settings) as session:
        response, polls = await execute_read_only(session, query)
    rows = extract_records(response)
    return rows, {'name': 'Databricks MCP', 'tool': 'execute_sql_read_only',
                  'statement_id': response.get('statement_id'), 'poll_count': polls,
                  'queried_at': datetime.now(timezone.utc).isoformat(),
                  'duration_ms': round((time.monotonic()-start)*1000)}


def read_source(settings, exception_id=None):
    build_query(settings.table_prefix, exception_id)
    try:
        return asyncio.run(fetch_source(settings, exception_id))
    except Exception as error:
        def messages(exc):
            if isinstance(exc, BaseExceptionGroup):
                return [part for nested in exc.exceptions for part in messages(nested)]
            return [str(exc) or type(exc).__name__]
        raise DataError('；'.join(dict.fromkeys(messages(error))).replace(settings.token, '[REDACTED]') or 'MCP查询失败。') from None


class Tracker:
    def __init__(self, settings, store, reader=read_source):
        self.settings, self.store, self.reader = settings, store, reader

    def list(self):
        rows, source = self.reader(self.settings)
        return {'rows': self.store.overlay(rows), 'source': source}

    def source_record(self, exception_id):
        rows, source = self.reader(self.settings, exception_id)
        if len(rows) != 1:
            raise NotFoundError('未找到这条异常记录。')
        return rows[0], source

    def detail(self, exception_id):
        row, source = self.source_record(exception_id)
        return {'record': self.store.overlay([row])[0], 'source': source}

    def update(self, exception_id, status, note, expected_status):
        row, source = self.source_record(exception_id)
        saved = self.store.save(row, status, note, expected_status)
        return {'record': saved, 'source': source, 'saved_to': 'local'}
