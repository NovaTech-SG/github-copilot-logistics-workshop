import json
import tempfile
import threading
import unittest
from copy import deepcopy
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.error import HTTPError
from urllib.request import Request, ProxyHandler, build_opener

from app import make_handler
from services.mcp_sql import DataError, execute_read_only, extract_records
from services.queries import build_query
from services.settings import Settings
from services.store import FollowUpStore, ConflictError
from services.tracker import Tracker, NotFoundError, read_source


def source_rows():
    return [{'exception_id': 'EX001', 'shipment_id': 'SHP001', 'handling_status': 'OPEN',
             'exception_type': 'DELAY', 'follow_up_note': '', 'assigned_team': '物流团队'},
            {'exception_id': 'EX002', 'shipment_id': 'SHP001', 'handling_status': 'IN_PROGRESS',
             'exception_type': 'MISSING_TIMESTAMP', 'follow_up_note': '等待确认'}]


def response(rows):
    return {'manifest': {'total_row_count': 1, 'schema': {'columns': [{'name': 'tracker_json'}]}},
            'result': {'data_typed_array': [{'values': [{'str': json.dumps({'total_count': len(rows), 'rows': rows})}]}]}}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'followups.sqlite3'
        self.store = FollowUpStore(self.path)
        self.source = source_rows()[0]

    def tearDown(self):
        self.temp.cleanup()

    def test_save_reopen_persist_and_source_remains_unchanged(self):
        original = deepcopy(self.source)
        self.store.save(self.source, 'IN_PROGRESS', ' 已联系承运商 ', 'OPEN')
        row = FollowUpStore(self.path).overlay([self.source])[0]
        self.assertEqual((row['handling_status'], row['follow_up_note']), ('IN_PROGRESS', '已联系承运商'))
        self.assertEqual(row['source_handling_status'], 'OPEN')
        self.assertTrue(row['saved_locally'])
        self.assertEqual(self.source, original)
        self.assertTrue(row['local_updated_at'])

    def test_invalid_changes_do_not_persist(self):
        for state, note in (('RESOLVED', '跳过处理中'), ('BAD', '无效'), ('IN_PROGRESS', '  '), ('IN_PROGRESS', 'a'*1001)):
            with self.subTest(state=state, note_length=len(note)), self.assertRaises(ValueError):
                self.store.save(self.source, state, note, 'OPEN')
        self.assertFalse(self.store.overlay([self.source])[0]['saved_locally'])

    def test_sequence_conflict_same_state_note_and_terminal(self):
        self.store.save(self.source, 'IN_PROGRESS', '正在处理', 'OPEN')
        with self.assertRaises(ConflictError):
            self.store.save(self.source, 'IN_PROGRESS', '过期窗口', 'OPEN')
        self.store.save(self.source, 'IN_PROGRESS', '追加备注', 'IN_PROGRESS')
        self.store.save(self.source, 'RESOLVED', '已解决', 'IN_PROGRESS')
        with self.assertRaises(ValueError):
            self.store.save(self.source, 'OPEN', '退回', 'RESOLVED')

    def test_two_exceptions_on_same_shipment_remain_independent(self):
        self.store.save(self.source, 'IN_PROGRESS', '单独跟进', 'OPEN')
        rows = self.store.overlay(source_rows())
        self.assertEqual(len(rows), 2)
        self.assertFalse(rows[1]['saved_locally'])
        self.assertEqual(rows[1]['follow_up_note'], '等待确认')


class McpTests(unittest.TestCase):
    def test_blank_transport_error_is_identified_and_credentials_redacted(self):
        settings = Settings('https://example.test/api/2.0/mcp/sql', 'test-private-token')
        for error, expected in ((TimeoutError(), 'TimeoutError'), (RuntimeError(settings.token), '[REDACTED]')):
            with self.subTest(expected=expected), patch('services.tracker.fetch_source', AsyncMock(side_effect=error)):
                with self.assertRaises(DataError) as caught:
                    read_source(settings)
                self.assertIn(expected, str(caught.exception))
                self.assertNotIn(settings.token, str(caught.exception))

    def test_typed_and_text_array_results(self):
        rows = source_rows()
        self.assertEqual(extract_records(response(rows)), rows)
        alternate = response(rows)
        alternate['result'] = {'data_array': [[json.dumps({'total_count': 2, 'rows': rows})]]}
        self.assertEqual(extract_records(alternate), rows)
        self.assertEqual(extract_records(response([])), [])

    def test_truncation_missing_cell_duplicate_and_bad_state(self):
        duplicate = source_rows()+[source_rows()[0]]
        bad_state = source_rows(); bad_state[0]['handling_status'] = 'BAD'
        for raw in (response(source_rows())|{'truncated': True}, response(source_rows())|{'result': {}}, response(duplicate), response(bad_state)):
            with self.subTest(raw=raw), self.assertRaises(DataError):
                extract_records(raw)
        raw = response(source_rows()); raw['result'] = {'data_array': [[json.dumps({'total_count': 3, 'rows': source_rows()})]]}
        with self.assertRaises(DataError):
            extract_records(raw)

    def test_query_rejects_sql_injection(self):
        with self.assertRaises(ValueError):
            build_query('`catalog`.`schema`', "EX001' OR 1=1")
        self.assertIn('LEFT JOIN', build_query('`catalog`.`schema`', 'EX001'))


class PollTests(unittest.IsolatedAsyncioTestCase):
    async def test_pending_uses_only_readonly_and_poll(self):
        def tool(state):
            return SimpleNamespace(isError=False, structuredContent={'status': {'state': state}, 'statement_id': 's1'}, content=[])
        session = SimpleNamespace(call_tool=AsyncMock(side_effect=[tool('PENDING'), tool('SUCCEEDED')]))
        with patch('services.mcp_sql.asyncio.sleep', AsyncMock()):
            _, polls = await execute_read_only(session, 'SELECT 1')
        self.assertEqual(polls, 1)
        self.assertEqual([c.args[0] for c in session.call_tool.call_args_list], ['execute_sql_read_only', 'poll_sql_result'])


class HttpTests(unittest.TestCase):
    def test_http_save_readback_validation_and_no_cloud_write(self):
        with tempfile.TemporaryDirectory() as temp:
            def reader(settings, exception_id=None):
                rows = [r for r in source_rows() if exception_id is None or r['exception_id'] == exception_id]
                return rows, {'name': 'Databricks MCP'}
            tracker = Tracker(Settings('https://example.test/api/2.0/mcp/sql', 'test-private-token'), FollowUpStore(Path(temp)/'db.sqlite3'), reader)
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(tracker))
            thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
            opener = build_opener(ProxyHandler({})); base = f'http://127.0.0.1:{server.server_port}'
            def call(path, body=None):
                request = Request(base+path, data=None if body is None else json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
                return json.load(opener.open(request, timeout=5))
            try:
                data = call('/api/exceptions/EX001', {'status': 'IN_PROGRESS', 'note': '保存验证', 'expected_status': 'OPEN'})
                self.assertEqual(data['saved_to'], 'local')
                self.assertEqual(call('/api/exceptions/EX001')['record']['follow_up_note'], '保存验证')
                self.assertEqual(call('/api/exceptions')['rows'][1]['saved_locally'], False)
                for path, body, status in (('/api/exceptions/EX001', {}, 400),
                        ('/api/exceptions/EX001', {'status':'IN_PROGRESS','note':'过期','expected_status':'OPEN'}, 409),
                        ('/api/exceptions/MISSING', None, 404)):
                    with self.subTest(status=status), self.assertRaises(HTTPError) as caught:
                        call(path, body)
                    self.assertEqual(caught.exception.code, status)
                    self.assertNotIn(tracker.settings.token, caught.exception.read().decode())
            finally:
                server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
