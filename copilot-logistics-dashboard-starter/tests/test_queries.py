import asyncio
import os
import unittest
from pathlib import Path

from services.queries import build_query


PREFIX = "`dev_databricks`.`default`"


def fixture_query(carrier="", page=1, scenario="mixed"):
    query = build_query(PREFIX, carrier, page)
    if scenario == "pages":
        shipments = """SELECT concat('S', lpad(cast(id AS STRING), 3, '0')) AS shipment_id,
          'A' AS carrier_id, date'2026-01-01' AS shipment_date,
          '上海' AS origin_city, '北京' AS destination_city,
          timestamp'2026-01-02 00:00:00' AS planned_arrival,
          timestamp'2026-01-02 00:00:00' AS actual_arrival,
          'DELIVERED' AS status, timestamp'2026-01-03 00:00:00' AS snapshot_at
          FROM range(41)"""
    else:
        rows = {
            "mixed": """('S1','A','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-01 23:00:00',date'2026-01-01'),
              ('S2','A','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-02 00:00:00',date'2026-01-01'),
              ('S3','B','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-02 01:00:00',date'2026-01-03'),
              ('S4','B','IN_TRANSIT',timestamp'2026-01-02 00:00:00',NULL,date'2026-01-03'),
              ('S5','B','CANCELLED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-03 00:00:00',date'2026-01-03'),
              ('S6','B','DELIVERED',NULL,timestamp'2026-01-03 00:00:00',date'2026-01-03')""",
            "weighted": """('S1','A','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-02 00:00:00',date'2026-01-01'),
              ('S2','B','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-02 00:00:00',date'2026-01-01'),
              ('S3','B','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-03 00:00:00',date'2026-01-01'),
              ('S4','B','DELIVERED',timestamp'2026-01-02 00:00:00',timestamp'2026-01-03 00:00:00',date'2026-01-01')""",
            "zero": """('S1','UNKNOWN','IN_TRANSIT',NULL,NULL,date'2026-01-01')""",
        }[scenario]
        shipments = f"""SELECT *, '上海' AS origin_city, '北京' AS destination_city,
          timestamp'2026-01-04 00:00:00' AS snapshot_at FROM VALUES {rows}
          AS v(shipment_id, carrier_id, status, planned_arrival, actual_arrival, shipment_date)"""
    carriers = """SELECT * FROM VALUES ('A','甲',true),('A','甲',true),('B','乙',false),('EMPTY','无单',true)
      AS c(carrier_id, carrier_name, is_active)"""
    query = query.replace(f"{PREFIX}.`shipments`", "fixture_shipments")
    query = query.replace(f"{PREFIX}.`carriers`", "fixture_carriers")
    return query.replace("WITH ", f"WITH fixture_shipments AS ({shipments}), fixture_carriers AS ({carriers}), ", 1)


class QueryInputTests(unittest.TestCase):
    def test_rejects_unsafe_or_invalid_parameters(self):
        for carrier in ("A' OR 1=1", " A", "A ", "中文", "A" * 65, None):
            with self.subTest(carrier=carrier), self.assertRaises(ValueError):
                build_query(PREFIX, carrier)
        for page in (0, -1, True, 1.5, "1", 2147483648):
            with self.subTest(page=page), self.assertRaises(ValueError):
                build_query(PREFIX, page=page)
        for prefix in ("dev.default", "`dev`.`default`; DROP TABLE x", "`dev`.`default`.`extra`"):
            with self.subTest(prefix=prefix), self.assertRaises(ValueError):
                build_query(prefix)

    def test_all_filtered_and_paged_queries_are_bounded_read_only(self):
        for carrier, page in (("", 1), ("UNKNOWN", 2147483647), ("A_B-1", 2)):
            query = build_query(PREFIX, carrier, page)
            self.assertTrue(query.startswith("WITH "))
            self.assertIn("dashboard_json", query)
            self.assertNotIn("exceptions", query)
            self.assertNotIn("freight_cost", query)
            self.assertIn("20", query)


@unittest.skipUnless(os.environ.get("DASHBOARD_LIVE_TESTS") == "1", "显式启用只读 Databricks SQL 验证")
class LiveQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from services.settings import load_settings
        config = os.environ.get("DASHBOARD_VSCODE_CONFIG")
        cls.settings = load_settings(Path(config) if config else None)

    def read(self, carrier="", page=1, scenario="mixed"):
        from services.mcp_sql import connect, execute_read_only, extract_dashboard

        async def run():
            async with connect(self.settings) as session:
                response, _ = await execute_read_only(session, fixture_query(carrier, page, scenario))
            return extract_dashboard(response)
        return asyncio.run(run())

    def test_mixed_statuses_equality_duplicates_and_date_gaps(self):
        data = self.read()
        self.assertEqual(data["summary"], dict(total_count=6, eligible_count=3, on_time_count=2,
                                             delayed_count=1, excluded_count=3, on_time_rate=66.67))
        self.assertEqual([day["total_count"] for day in data["daily"]], [2, 0, 4])
        self.assertEqual([row["result"] for row in data["shipments"]],
                         ["ON_TIME", "ON_TIME", "DELAYED", "IN_TRANSIT", "CANCELLED", "MISSING_TIMESTAMP"])
        self.assertTrue(data["source_snapshot_at"].endswith("Z"))

    def test_weighted_rate_and_single_day(self):
        data = self.read(scenario="weighted")
        self.assertEqual(data["summary"]["on_time_rate"], 50.0)
        self.assertEqual(len(data["daily"]), 1)

    def test_filter_unknown_carrier_and_zero_denominator(self):
        data = self.read("B")
        self.assertEqual(data["summary"]["total_count"], 4)
        self.assertEqual([row["carrier_id"] for row in data["by_carrier"]], ["B"])
        self.assertEqual(len(data["carriers"]), 3)
        zero = self.read(scenario="zero")
        self.assertIsNone(zero["summary"]["on_time_rate"])
        self.assertEqual(zero["by_carrier"][0]["carrier_name"], "UNKNOWN")

    def test_empty_range(self):
        data = self.read("MISSING")
        self.assertEqual(data["summary"]["total_count"], 0)
        self.assertIsNone(data["summary"]["on_time_rate"])
        for key in ("by_carrier", "daily", "shipments"):
            self.assertEqual(data[key], [])
        self.assertIsNone(data["source_snapshot_at"])
        self.assertEqual(data["pagination"]["total_pages"], 0)
        self.assertEqual(data["pagination"]["page"], 1)

    def test_pages_stable_order_and_out_of_range(self):
        pages = [self.read(page=page, scenario="pages") for page in (1, 2, 3, 99)]
        self.assertEqual([len(data["shipments"]) for data in pages], [20, 20, 1, 1])
        ids = [row["shipment_id"] for data in pages[:3] for row in data["shipments"]]
        self.assertEqual(len(set(ids)), 41)
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(pages[3]["pagination"]["page"], 3)
        self.assertEqual(pages[3]["shipments"], pages[2]["shipments"])


if __name__ == "__main__":
    unittest.main()
