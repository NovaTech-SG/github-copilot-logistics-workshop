import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, build_opener

from app import make_handler
from services.dashboard import get_dashboard, prepare
from services.mcp_sql import DataError, decode_tool, execute_read_only, extract_dashboard
from services.queries import build_query
from services.settings import Settings


def tool(data=None, text=None, error=False):
    return SimpleNamespace(isError=error, structuredContent=data,
                           content=[] if text is None else [SimpleNamespace(type="text", text=text)])


def payload():
    return {"summary": {"shipment_count": 2, "eligible_count": 1, "on_time_count": 1,
                        "delayed_count": 0, "excluded_count": 1, "on_time_rate": 1.0},
            "carriers": [{"carrier_id": "CAR001", "carrier_name": "模拟承运商A"}],
            "by_carrier": [{"carrier_id": "CAR001", "shipment_count": 2}],
            "daily": [{"date": "2026-11-01", "count": 1}, {"date": "2026-11-03", "count": 1}],
            "shipments": [{"shipment_id": "S1", "carrier_id": "CAR001"},
                          {"shipment_id": "S2", "carrier_id": "CAR001"}]}


def response(data):
    return {"manifest": {"total_row_count": 1, "schema": {"columns": [{"name": "dashboard_json"}]}},
            "result": {"data_typed_array": [{"values": [{"str": json.dumps(data)}]}]}}


class ResultTests(unittest.TestCase):
    def test_sdk_formats_and_text_fallback(self):
        data = payload()
        self.assertEqual(extract_dashboard(response(data)), data)
        raw = response(data)
        raw["result"] = {"data_array": [[json.dumps(data)]]}
        self.assertEqual(extract_dashboard(raw), data)
        self.assertEqual(decode_tool(tool(text=json.dumps(raw))), raw)
        self.assertEqual(decode_tool(tool(data=raw, text="not JSON")), raw)

    def test_rejects_tool_errors_truncation_and_incomplete_result(self):
        with self.assertRaises(DataError):
            decode_tool(tool(text="denied", error=True))
        for change in ({"truncated": True}, {"returned_row_count": 0}, {"result": {}},
                       {"manifest": {"total_row_count": 2}},
                       {"result": {"data_array": [["{}"]]}}):
            with self.subTest(change=change), self.assertRaises(DataError):
                extract_dashboard(response(payload()) | change)

    def test_business_counts_and_date_gaps(self):
        data = prepare(payload(), "CAR001", 1)
        self.assertEqual(data["daily"][1], {"date": "2026-11-02", "count": 0})
        self.assertEqual(data["scope"], "模拟承运商A")
        self.assertEqual(data["shipments"][0]["carrier_name"], "模拟承运商A")
        for field, value in (("on_time_count", 2), ("delayed_count", 1), ("on_time_rate", 0.5)):
            data = payload()
            data["summary"][field] = value
            with self.subTest(field=field), self.assertRaises(DataError):
                prepare(data, "", 1)
        for field in ("daily", "by_carrier", "shipments"):
            data = payload()
            data[field] = []
            with self.subTest(field=field), self.assertRaises(DataError):
                prepare(data, "", 1)
        with self.assertRaises(DataError):
            prepare(payload(), "CAR002", 1)

    def test_zero_denominator_empty_scope_and_last_page(self):
        data = payload()
        data["summary"].update(eligible_count=0, on_time_count=0, excluded_count=2, on_time_rate=None)
        self.assertIsNone(prepare(data, "", 1)["summary"]["on_time_rate"])
        data = payload()
        data["summary"] = {key: None if key == "on_time_rate" else 0 for key in data["summary"]}
        data.update(by_carrier=[], daily=[], shipments=[])
        self.assertEqual(prepare(data, "CAR999", 1)["page_count"], 1)
        data = payload()
        data["shipments"] = []
        self.assertEqual(prepare(data, "", 2)["shipments"], [])

    def test_input_validation_and_secret_redaction(self):
        for carrier, page in (("CAR001' OR 1=1", 1), ("CAR001", 0), ("", True), ("", 10001)):
            with self.subTest(carrier=carrier, page=page), self.assertRaises(ValueError):
                build_query("`demo`.`default`", carrier, page)
        settings = Settings("https://example.test/api/2.0/mcp/sql", "private-test-token")
        self.assertNotIn(settings.token, repr(settings))
        with patch("services.dashboard.fetch_dashboard", AsyncMock(side_effect=RuntimeError(settings.token))):
            with self.assertRaises(DataError) as caught:
                get_dashboard(settings)
        self.assertNotIn(settings.token, str(caught.exception))


class PollTests(unittest.IsolatedAsyncioTestCase):
    async def test_pending_then_success_uses_only_readonly_and_poll(self):
        pending = {"status": {"state": "PENDING"}, "statement_id": "statement-1"}
        success = {"status": {"state": "SUCCEEDED"}, "statement_id": "statement-1"}
        session = SimpleNamespace(call_tool=AsyncMock(side_effect=[tool(pending), tool(success)]))
        with patch("services.mcp_sql.asyncio.sleep", AsyncMock()):
            result, polls = await execute_read_only(session, "SELECT 1")
        self.assertEqual((result, polls), (success, 1))
        self.assertEqual([call.args[0] for call in session.call_tool.call_args_list],
                         ["execute_sql_read_only", "poll_sql_result"])

    async def test_failure_unknown_state_and_timeout(self):
        for status in ("FAILED", "UNKNOWN", "RUNNING"):
            session = SimpleNamespace(call_tool=AsyncMock(return_value=tool(
                {"status": {"state": status}, "statement_id": "s1"})))
            with self.subTest(status=status), self.assertRaises(DataError):
                await execute_read_only(session, "SELECT 1", timeout=0)


class HttpTests(unittest.TestCase):
    def test_invalid_input_and_upstream_error_are_not_success(self):
        settings = Settings("https://example.test/api/2.0/mcp/sql", "private-test-token")

        def fetch(config, carrier, page):
            build_query(config.table_prefix, carrier, page)
            raise DataError("denied " + config.token)

        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(settings, fetch))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        opener = build_opener(ProxyHandler({}))
        try:
            for query, status in (("?page=0", 400), ("?carrier=bad", 400), ("", 502)):
                with self.subTest(query=query), self.assertRaises(HTTPError) as caught:
                    opener.open(f"http://127.0.0.1:{server.server_port}/api/dashboard{query}", timeout=5)
                self.assertEqual(caught.exception.code, status)
                self.assertNotIn(settings.token, caught.exception.read().decode())
                self.assertEqual(caught.exception.headers["Cache-Control"], "no-store")
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
