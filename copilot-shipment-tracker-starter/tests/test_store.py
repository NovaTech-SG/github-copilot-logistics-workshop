import copy
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace

from services.store import ConflictError, FollowUpStore
from services.tracker import Tracker


class FollowUpStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'followups.sqlite3'
        self.store = FollowUpStore(self.path)
        self.source = {'exception_id': 'EXC1', 'shipment_id': 'SHP1',
                       'handling_status': 'OPEN', 'follow_up_note': '源备注',
                       'source_updated_epoch': None}

    def snapshot(self):
        with self.store.connect() as db:
            return [dict(row) for row in db.execute('SELECT * FROM followups')]

    def test_transitions_trim_and_complete_overlay(self):
        original = copy.deepcopy(self.source)
        for current, target in [('OPEN', 'OPEN'), ('OPEN', 'IN_PROGRESS'),
                                ('IN_PROGRESS', 'IN_PROGRESS'),
                                ('IN_PROGRESS', 'RESOLVED'), ('RESOLVED', 'RESOLVED')]:
            with self.subTest(current=current, target=target):
                result = self.store.save(self.source, target, '  跟进备注  ', current)
                self.assertEqual(result['handling_status'], target)
                self.assertEqual(result['follow_up_note'], '跟进备注')
                self.assertEqual(result['source_handling_status'], 'OPEN')
                self.assertEqual(result['shipment_id'], 'SHP1')
                self.assertTrue(result['saved_locally'])
                self.assertEqual(datetime.fromisoformat(result['local_updated_at']).utcoffset(), timedelta(0))
                self.assertEqual(len(self.snapshot()), 1)
        self.assertEqual(self.source, original)

    def test_note_boundaries(self):
        for length in (1, 1000):
            result = self.store.save(self.source, 'OPEN', ' ' + '字' * length + ' ', 'OPEN')
            self.assertEqual(result['follow_up_note'], '字' * length)

    def test_invalid_changes_preserve_all_fields(self):
        self.store.save(self.source, 'IN_PROGRESS', '原备注', 'OPEN')
        before = self.snapshot()
        for status, note, expected in [
            ('OPEN', '退回', 'IN_PROGRESS'), ('UNKNOWN', '无效', 'IN_PROGRESS'),
            ('RESOLVED', '', 'IN_PROGRESS'), ('RESOLVED', '  ', 'IN_PROGRESS'),
            ('RESOLVED', '字' * 1001, 'IN_PROGRESS'), ('RESOLVED', None, 'IN_PROGRESS'),
            ('RESOLVED', '缺原状态', None), ('RESOLVED', '无效原状态', 'INVALID'),
        ]:
            with self.subTest(status=status, expected=expected):
                with self.assertRaises(ValueError):
                    self.store.save(self.source, status, note, expected)
                self.assertEqual(self.snapshot(), before)
        with self.assertRaises(ConflictError):
            self.store.save(self.source, 'RESOLVED', '旧页面', 'OPEN')
        self.assertEqual(self.snapshot(), before)

    def test_source_state_fallback_and_skip_rejected_without_insert(self):
        with self.assertRaises(ValueError):
            self.store.save(self.source, 'RESOLVED', '跳级', 'OPEN')
        self.assertEqual(self.snapshot(), [])
        resolved = {**self.source, 'handling_status': 'RESOLVED'}
        self.assertEqual(self.store.save(resolved, 'RESOLVED', '补充', 'RESOLVED')['handling_status'], 'RESOLVED')
        with self.assertRaises(ValueError):
            self.store.save(resolved, 'IN_PROGRESS', '退回', 'RESOLVED')

    def test_parameterized_note_and_same_shipment_isolation(self):
        other = {**self.source, 'exception_id': 'EXC2'}
        note = "承运商说 '已收到'; DROP TABLE followups; --"
        self.store.save(self.source, 'IN_PROGRESS', note, 'OPEN')
        first, second = self.store.overlay([self.source, other])
        self.assertEqual(first['follow_up_note'], note)
        self.assertEqual(second['handling_status'], 'OPEN')
        self.assertEqual(second['follow_up_note'], '源备注')
        self.assertFalse(second['saved_locally'])
        self.assertIsNone(second['local_updated_at'])

    def test_failed_insert_and_update_roll_back(self):
        for operation in ('INSERT', 'UPDATE'):
            with self.subTest(operation=operation):
                if operation == 'UPDATE':
                    self.store.save(self.source, 'OPEN', '已有记录', 'OPEN')
                before = self.snapshot()
                with self.store.connect() as db:
                    db.execute(f"CREATE TRIGGER fail_write AFTER {operation} ON followups BEGIN SELECT RAISE(ABORT, 'test failure'); END")
                with self.assertRaises(sqlite3.Error):
                    self.store.save(self.source, 'IN_PROGRESS', '不应留下', 'OPEN')
                self.assertEqual(self.snapshot(), before)
                with self.store.connect() as db:
                    db.execute('DROP TRIGGER fail_write')

    def test_concurrent_old_status_cannot_overwrite(self):
        barrier = Barrier(2)

        def save(note):
            barrier.wait(timeout=5)
            try:
                self.store.save(self.source, 'IN_PROGRESS', note, 'OPEN')
                return 'saved'
            except ConflictError:
                return 'conflict'

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(save, ['甲', '乙']))
        self.assertCountEqual(outcomes, ['saved', 'conflict'])
        self.assertEqual(len(self.snapshot()), 1)

    def test_reopen_same_file_and_different_file(self):
        saved = self.store.save(self.source, 'IN_PROGRESS', '重启保留', 'OPEN')
        other = {**self.source, 'exception_id': 'EXC2'}

        def reader(settings, exception_id=None):
            return ([self.source, other] if exception_id is None else [self.source]), {'name': 'test'}

        tracker = Tracker(SimpleNamespace(), FollowUpStore(self.path), reader)
        self.assertEqual(tracker.detail('EXC1')['record'], saved)
        rows = tracker.list()['rows']
        self.assertEqual([row['handling_status'] for row in rows], ['IN_PROGRESS', 'OPEN'])
        fresh = FollowUpStore(Path(self.temp.name) / 'another.sqlite3').overlay([self.source])[0]
        self.assertFalse(fresh['saved_locally'])
        self.assertIsNone(fresh['local_updated_at'])
        self.assertIsNone(fresh['source_updated_epoch'])


if __name__ == '__main__':
    unittest.main()
