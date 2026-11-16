import copy
import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app import make_handler
from services.mcp_sql import DataError
from services.store import FollowUpStore
from services.tracker import Tracker


class FollowUpApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = FollowUpStore(Path(self.temp.name) / 'api.sqlite3')
        self.rows = [{'exception_id': 'EXC1', 'shipment_id': 'SHP1',
                      'handling_status': 'OPEN', 'follow_up_note': '源备注',
                      'source_updated_epoch': 1794834000}]
        self.source_error = False

        def reader(settings, exception_id=None):
            if self.source_error:
                raise DataError('test source failure')
            return copy.deepcopy([r for r in self.rows if exception_id is None or r['exception_id'] == exception_id]), {'name': 'test'}

        self.tracker = Tracker(SimpleNamespace(token='test-secret'), self.store, reader)
        handler = make_handler(self.tracker)
        handler.log_message = lambda *args: None
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def request(self, method='POST', path='/api/exceptions/EXC1', body=None, content_type='application/json'):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            raw = body if isinstance(body, str) else json.dumps(body or {'status': 'IN_PROGRESS', 'note': '  跟进  ', 'expected_status': 'OPEN'})
            connection.request(method, path, body=raw.encode('utf-8') if method == 'POST' else None,
                               headers={'Content-Type': content_type})
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_post_then_get_and_source_unchanged(self):
        original = copy.deepcopy(self.rows)
        status, posted = self.request()
        self.assertEqual(status, 200)
        self.assertEqual(posted['saved_to'], 'local')
        self.assertEqual(posted['record']['follow_up_note'], '跟进')
        self.assertTrue(posted['record']['local_updated_at'])
        status, detail = self.request('GET')
        self.assertEqual(status, 200)
        self.assertEqual(detail['record'], posted['record'])
        self.assertEqual(detail['record']['source_handling_status'], 'OPEN')
        self.assertEqual(self.rows, original)

    def test_bad_requests_and_not_found_do_not_write(self):
        invalid_bodies = [
            {'status': 'IN_PROGRESS', 'note': 'x'},
            {'status': 'INVALID', 'note': 'x', 'expected_status': 'OPEN'},
            {'status': 'RESOLVED', 'note': '跳级', 'expected_status': 'OPEN'},
            {'status': 'IN_PROGRESS', 'note': ' ', 'expected_status': 'OPEN'},
            {'status': 'IN_PROGRESS', 'note': '字' * 1001, 'expected_status': 'OPEN'},
            {'status': 'IN_PROGRESS', 'note': None, 'expected_status': 'OPEN'},
            '[]', '{', 'x' * 16385,
        ]
        for body in invalid_bodies:
            with self.subTest(body_type=type(body).__name__):
                self.assertEqual(self.request(body=body)[0], 400)
        self.assertEqual(self.request(content_type='text/plain')[0], 400)
        for suffix in ('bad%27id', 'a' * 65):
            self.assertEqual(self.request(path='/api/exceptions/' + suffix)[0], 400)
        self.assertEqual(self.request(path='/api/exceptions/UNKNOWN')[0], 404)
        self.assertFalse(self.store.overlay(self.rows)[0]['saved_locally'])

    def test_stale_status_and_failures(self):
        self.assertEqual(self.request()[0], 200)
        before = self.store.overlay(self.rows)
        self.assertEqual(self.request()[0], 409)
        self.assertEqual(self.store.overlay(self.rows), before)
        with patch.object(self.store, 'save', side_effect=sqlite3.OperationalError('test-secret')):
            status, data = self.request()
            self.assertEqual(status, 500)
            self.assertNotIn('test-secret', data['error'])
        self.source_error = True
        status, data = self.request()
        self.assertEqual(status, 502)
        self.assertNotIn('record', data)
        self.assertEqual(self.store.overlay(self.rows), before)

    def test_commit_then_read_failure_is_recoverable(self):
        with patch.object(self.store, 'overlay', side_effect=sqlite3.OperationalError('test read failure')):
            self.assertEqual(self.request()[0], 500)
        status, data = self.request('GET')
        self.assertEqual(status, 200)
        self.assertEqual(data['record']['handling_status'], 'IN_PROGRESS')


if __name__ == '__main__':
    unittest.main()
