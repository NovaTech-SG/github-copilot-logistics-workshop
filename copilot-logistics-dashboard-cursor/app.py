import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from services.dashboard import get_dashboard
from services.mcp_sql import DataError
from services.settings import load_settings

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
                carrier = params.get("carrier", [""])[0]
                page = int(params.get("page", ["1"])[0])
                data = fetch(settings, carrier, page)
                self.send_json(200, data)
            except ValueError as error:
                self.send_json(400, {"error": str(error).replace(settings.token, "[REDACTED]")})
            except DataError as error:
                self.send_json(502, {"error": str(error).replace(settings.token, "[REDACTED]")})
    return Handler


def main():
    default_config = Path(os.environ.get("APPDATA", Path.home()/"AppData/Roaming"))/"Code/User/mcp.json"
    parser = argparse.ArgumentParser(description="Databricks MCP 物流看板")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--vscode-config", nargs="?", const=default_config, type=Path, help="显式复用本机VS Code的databricksTraining配置；也可指定其他配置路径。")
    parser.add_argument("--check", action="store_true", help="只读查询并输出指标，不启动网页。")
    parser.add_argument("--carrier", default="")
    args = parser.parse_args()
    try:
        settings = load_settings(args.vscode_config)
        if args.check:
            data = get_dashboard(settings, args.carrier)
            print(json.dumps({"summary":data["summary"], "rows":len(data["shipments"]), "source":data["source"]}, ensure_ascii=False))
            return
    except (ValueError, DataError, OSError) as error:
        parser.exit(1, f"启动检查失败：{error}\n")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(settings))
    print(f"物流看板：http://127.0.0.1:{args.port} · 数据来源：Databricks MCP",flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
