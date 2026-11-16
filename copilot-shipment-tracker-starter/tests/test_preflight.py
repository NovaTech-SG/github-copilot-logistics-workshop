import json
import tempfile
import unittest
from pathlib import Path
from services.mcp_sql import extract_records
from services.store import FollowUpStore, validate_change
from services.queries import build_query


class PreparedRulesTests(unittest.TestCase):
    def test_allowed_transition_and_trim(self):
        self.assertEqual(validate_change('OPEN', 'IN_PROGRESS', ' 跟进中 '), '跟进中')

    def test_invalid_rule_inputs(self):
        for status,note in (('RESOLVED','跳过'),('IN_PROGRESS','  '),('IN_PROGRESS','a'*1001)):
            with self.subTest(status=status), self.assertRaises(ValueError):
                validate_change('OPEN',status,note)

    def test_source_time_survives_parsing_and_local_overlay(self):
        for source_time in (None, 1794834000):
            with self.subTest(source_time=source_time), tempfile.TemporaryDirectory() as directory:
                row = {'exception_id': 'EXC1', 'shipment_id': 'SHP1', 'exception_type': 'DELAY',
                       'handling_status': 'OPEN', 'follow_up_note': '', 'source_updated_epoch': source_time}
                response = {'manifest': {'total_row_count': 1, 'schema': {'columns': [{'name': 'tracker_json'}]}},
                            'result': {'data_array': [[json.dumps({'total_count': 1, 'rows': [row]})]]}}
                parsed = extract_records(response)
                store = FollowUpStore(Path(directory) / 'test.sqlite3')
                store.save(parsed[0], 'IN_PROGRESS', '本机备注', 'OPEN')
                merged = store.overlay(parsed)[0]
                self.assertEqual(merged['source_updated_epoch'], source_time)
                self.assertEqual(merged['source_handling_status'], 'OPEN')
                self.assertEqual(merged['handling_status'], 'IN_PROGRESS')
                self.assertTrue(merged['local_updated_at'])
                self.assertEqual(parsed[0], row)

    def test_query_rejects_invalid_id(self):
        with self.assertRaises(ValueError):
            build_query('`catalog`.`schema`', "x' OR 1=1")


if __name__ == '__main__':
    unittest.main()
