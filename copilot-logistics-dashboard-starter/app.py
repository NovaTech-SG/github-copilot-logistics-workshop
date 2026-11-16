import argparse
import asyncio
import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from services.dashboard import get_dashboard
from services.mcp_sql import DataError, connect, execute_read_only
from services.settings import load_settings
from services.queries import validate_params

ROOT = Path(__file__).resolve().parent


def make_handler(settings, fetch=get_dashboard):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT/"static"), **kwargs)

        def send_json(self, status, data):
            raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path != "/api/dashboard":
                return super().do_GET()
            params = parse_qs(parsed.query, keep_blank_values=True)
            try:
                if set(params) - {"carrier", "page"} or any(len(values) != 1 for values in params.values()):
                    raise ValueError("仅接受单个 carrier 和 page 参数。")
                carrier = params.get("carrier", [""])[0]
                page_text = params.get("page", ["1"])[0]
                if not re.fullmatch(r"[0-9]+", page_text) or len(page_text.lstrip("0") or "0") > 10:
                    raise ValueError("页码必须为 1—2147483647 的整数。")
                page = int(page_text.lstrip("0") or "0")
                validate_params(carrier, page)
            except ValueError as error:
                self.send_json(400, {"error": str(error).replace(settings.token, "[REDACTED]")})
                return
            try:
                self.send_json(200, fetch(settings, carrier, page))
            except DataError as error:
                self.send_json(502, {"error": str(error).replace(settings.token, "[REDACTED]")})
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                return
            except Exception:
                self.send_json(500, {"error": "服务暂时无法完成查询，请稍后重试。"})
    return Handler


def main():
    default_config = Path(os.environ.get("APPDATA", Path.home()/"AppData/Roaming"))/"Code/User/mcp.json"
    parser = argparse.ArgumentParser(description="Databricks MCP 物流运输表现看板")
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--vscode-config", nargs="?", const=default_config, type=Path, help="显式复用本机VS Code的databricksTraining配置；也可指定其他配置路径。")
    parser.add_argument("--check", action="store_true", help="仅执行SELECT 1检查MCP连接，不验收Dashboard业务。")
    parser.add_argument("--carrier", default="")
    args = parser.parse_args()
    try:
        settings = load_settings(args.vscode_config)
        if args.check:
            async def check_connection():
                async with connect(settings) as session:
                    response, polls = await execute_read_only(session, "SELECT 1 AS result")
                return {"connection": "OK", "sql_state": response["status"]["state"], "poll_count": polls, "business_verified": False}
            print(json.dumps(asyncio.run(check_connection()), ensure_ascii=False))
            return
    except Exception as error:
        def messages(exc):
            if isinstance(exc, BaseExceptionGroup):
                return [item for nested in exc.exceptions for item in messages(nested)]
            return [str(exc)]
        detail = "；".join(dict.fromkeys(messages(error)))
        if "settings" in locals():
            detail = detail.replace(settings.token, "[REDACTED]")
        parser.exit(1, f"启动检查失败：{detail}\n")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(settings))
    print(f"运输表现看板：http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
