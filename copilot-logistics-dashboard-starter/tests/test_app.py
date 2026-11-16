import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import Mock
from urllib.error import HTTPError
from urllib.request import urlopen

from app import make_handler
from services.mcp_sql import DataError


class HttpContractTests(unittest.TestCase):
    def setUp(self):
        self.fetch = Mock(return_value={"scope": {"carrier": "A"}})
        settings = SimpleNamespace(token="test-secret-only")
        handler = make_handler(settings, self.fetch)
        handler.log_message = lambda *args: None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, query):
        try:
            response = urlopen(self.base + "/api/dashboard" + query, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, json.loads(response.read())

    def test_default_filtered_and_paged_requests(self):
        for query, carrier, page in (("", "", 1), ("?carrier=A&page=02", "A", 2),
                                     ("?carrier=&page=2147483647", "", 2147483647)):
            status, headers, data = self.request(query)
            self.assertEqual(status, 200)
            self.assertEqual(headers["Cache-Control"], "no-store")
            self.assertIn("utf-8", headers["Content-Type"])
            self.fetch.assert_called_with(unittest.mock.ANY, carrier, page)

    def test_bad_parameters_rejected_before_fetch(self):
        for query in ("?carrier=A&carrier=B", "?page=1&page=2", "?unknown=1", "?page=",
                      "?page=-1", "?page=0", "?page=1.2", "?page=%2B1", "?page=2147483648",
                      "?carrier=%27", "?page=" + "9" * 100):
            self.fetch.reset_mock()
            with self.subTest(query=query):
                self.assertEqual(self.request(query)[0], 400)
                self.fetch.assert_not_called()

    def test_errors_are_json_and_redacted(self):
        for error, expected in ((DataError("failure test-secret-only"), 502),
                                (RuntimeError("traceback test-secret-only"), 500)):
            self.fetch.side_effect = error
            status, headers, data = self.request("")
            self.assertEqual(status, expected)
            self.assertIsInstance(data["error"], str)
            self.assertNotIn("test-secret-only", data["error"])
            self.assertNotIn("traceback", data["error"])
            self.assertEqual(headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
