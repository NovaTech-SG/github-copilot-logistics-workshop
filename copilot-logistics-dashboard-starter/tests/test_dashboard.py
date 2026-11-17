import copy
import json
import unittest
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from services.dashboard import get_dashboard
from services.mcp_sql import DataError


def example_data():
    summary = dict(total_count=1, eligible_count=1, on_time_count=1,
                   delayed_count=0, excluded_count=0, on_time_rate=100.0)
    return {
        "summary": summary,
        "carriers": [{"carrier_id": "A", "carrier_name": "甲"}],
        "by_carrier": [dict(carrier_id="A", carrier_name="甲", **summary)],
        "daily": [{"shipment_date": "2026-01-01", "total_count": 1}],
        "shipments": [{"shipment_id": "S1", "carrier_id": "A", "carrier_name": "甲",
                       "shipment_date": "2026-01-01", "origin_city": "上海", "destination_city": "北京",
                       "planned_arrival": "2026-01-02T00:00:00.000Z",
                       "actual_arrival": "2026-01-02T00:00:00.000Z", "status": "DELIVERED", "result": "ON_TIME"}],
        "pagination": dict(page=1, page_size=20, total_count=1, total_pages=1),
        "source_snapshot_at": "2026-01-03T00:00:00.000Z",
        "invalid_count": 0,
    }


def envelope(data):
    return {"status": {"state": "SUCCEEDED"}, "manifest": {
        "total_row_count": 1, "total_chunk_count": 1,
        "schema": {"columns": [{"name": "dashboard_json"}]}},
        "result": {"data_array": [[json.dumps(data)]]}}


@asynccontextmanager
async def fake_connect(settings):
    yield object()


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(table_prefix="`dev_databricks`.`default`", token="test-secret-only")

    def fetch(self, data=None, response=None, carrier="", page=1):
        result = response if response is not None else envelope(example_data() if data is None else data)
        with patch("services.dashboard.connect", fake_connect), patch(
            "services.dashboard.execute_read_only", new=AsyncMock(return_value=(result, 0))
        ) as execute:
            value = get_dashboard(self.settings, carrier, page)
            self.assertEqual(execute.await_count, 1)
            return value

    def test_valid_contract_and_completion_time(self):
        result = self.fetch(carrier="A")
        self.assertEqual(result["scope"], {"carrier": "A"})
        self.assertTrue(result["queried_at"].endswith("Z"))
        self.assertNotIn("invalid_count", result)
        self.assertEqual(result["summary"]["on_time_rate"], 100)

    def test_empty_and_zero_denominator(self):
        data = example_data()
        data["summary"] = dict(total_count=0, eligible_count=0, on_time_count=0,
                               delayed_count=0, excluded_count=0, on_time_rate=None)
        data.update(by_carrier=[], daily=[], shipments=[], source_snapshot_at=None,
                    pagination=dict(page=1, page_size=20, total_count=0, total_pages=0))
        self.assertIsNone(self.fetch(data, carrier="NONE")["summary"]["on_time_rate"])
        zero = example_data()
        zero["summary"].update(eligible_count=0, on_time_count=0, excluded_count=1, on_time_rate=None)
        zero["by_carrier"][0].update(zero["summary"])
        zero["shipments"][0].update(status="IN_TRANSIT", result="IN_TRANSIT", actual_arrival=None)
        self.assertIsNone(self.fetch(zero)["by_carrier"][0]["on_time_rate"])

    def test_rejects_damaged_business_results(self):
        changes = [
            lambda d: d["summary"].update(total_count=True),
            lambda d: d["summary"].update(on_time_rate=float("nan")),
            lambda d: d["summary"].update(delayed_count=1),
            lambda d: d["daily"][0].update(total_count=2),
            lambda d: d["shipments"][0].update(result="DELAYED"),
            lambda d: d["pagination"].update(page_size=21),
            lambda d: d.update(source_snapshot_at="2026-01-03 00:00:00"),
            lambda d: d.update(invalid_count=1),
            lambda d: d.update(shipments=[]),
            lambda d: d["by_carrier"][0].update(eligible_count=0),
        ]
        for index, change in enumerate(changes):
            data = copy.deepcopy(example_data())
            change(data)
            with self.subTest(index=index), self.assertRaises(DataError):
                self.fetch(data)
        with self.assertRaises(DataError):
            self.fetch(carrier="B")

    def test_rejects_truncation_chunks_and_invalid_json(self):
        for response in (dict(envelope(example_data()), truncated=True),
                         {**envelope(example_data()), "manifest": {"total_row_count": 2}},
                         {**envelope(example_data()), "result": {"data_array": [["not-json"]]}},
                         {**envelope(example_data()), "manifest": {
                             **envelope(example_data())["manifest"], "total_chunk_count": 2}}):
            with self.subTest(response=response), self.assertRaises(DataError):
                self.fetch(response=response)

    def test_connection_failures_are_safe_data_errors(self):
        for failure in (RuntimeError("connection test-secret-only"),
                        ExceptionGroup("connection", [TimeoutError("test-secret-only")])):
            with patch("services.dashboard.connect", fake_connect), patch(
                "services.dashboard.execute_read_only", new=AsyncMock(side_effect=failure)
            ), self.assertRaises(DataError) as raised:
                get_dashboard(self.settings)
            self.assertNotIn(self.settings.token, str(raised.exception))

    def test_invalid_input_does_not_connect(self):
        with patch("services.dashboard.connect") as connect:
            with self.assertRaises(ValueError):
                get_dashboard(self.settings, "A' OR 1=1")
            connect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
