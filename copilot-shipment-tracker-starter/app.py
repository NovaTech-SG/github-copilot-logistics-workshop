import argparse
import json
import os
import sqlite3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote

from services.mcp_sql import DataError
from services.queries import validate_id
from services.settings import load_settings
from services.store import FollowUpStore, ConflictError, STATES
from services.tracker import Tracker, NotFoundError

ROOT = Path(__file__).resolve().parent


def make_handler(tracker):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT/'static'), **kwargs)

        def send_json(self, status, data):
            raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def exception_id(self):
            path = unquote(urlsplit(self.path).path)
            if not path.startswith('/api/exceptions/'):
                raise NotFoundError('接口不存在。')
            return validate_id(path[len('/api/exceptions/'):])

        def respond(self, action):
            try:
                self.send_json(200, action())
            except (ValueError, TypeError) as error:
                self.send_json(400, {'error': str(error).replace(tracker.settings.token, '[REDACTED]')})
            except NotFoundError as error:
                self.send_json(404, {'error': str(error)})
            except ConflictError as error:
                self.send_json(409, {'error': str(error)})
            except NotImplementedError as error:
                self.send_json(501, {'error': str(error)})
            except DataError as error:
                self.send_json(502, {'error': str(error).replace(tracker.settings.token, '[REDACTED]')})
            except (sqlite3.Error, OSError):
                self.send_json(500, {'error': '本地跟进记录读写失败，请检查目录权限后重新读取。'})

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/api/exceptions':
                return self.respond(tracker.list)
            if path.startswith('/api/'):
                return self.respond(lambda: tracker.detail(self.exception_id()))
            return super().do_GET()

        def do_POST(self):
            def update():
                exception_id = self.exception_id()
                content_type = self.headers.get('Content-Type', '').split(';')[0].strip()
                if content_type != 'application/json':
                    raise ValueError('请使用JSON提交跟进记录。')
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 16384:
                    raise ValueError('提交内容长度无效。')
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError('提交内容必须为JSON对象。')
                if data.get('status') not in STATES or data.get('expected_status') not in STATES or not isinstance(data.get('note'), str):
                    raise ValueError('请提供有效的处理状态、原状态和跟进备注。')
                return tracker.update(exception_id, data.get('status'), data.get('note'), data.get('expected_status'))
            self.respond(update)
    return Handler


def main():
    parser = argparse.ArgumentParser(description='运输异常跟进 · 学员起始项目')
    parser.add_argument('--port', type=int, default=8769)
    parser.add_argument('--db', type=Path, default=ROOT/'data/followups.sqlite3')
    parser.add_argument('--vscode-config', nargs='?', type=Path,
                        const=Path(os.environ.get('APPDATA', Path.home()/'AppData/Roaming'))/'Code/User/mcp.json')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        settings = load_settings(args.vscode_config)
        tracker = Tracker(settings, FollowUpStore(args.db))
        if args.check:
            data = tracker.list()
            counts = {state: sum(r['handling_status'] == state for r in data['rows']) for state in ('OPEN','IN_PROGRESS','RESOLVED')}
            print(json.dumps({'exception_count': len(data['rows']), 'counts': counts, 'source': data['source']}, ensure_ascii=False))
            return
    except (ValueError, DataError, OSError, sqlite3.Error) as error:
        parser.exit(1, f'启动失败：{error}\n')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(tracker))
    print(f'异常跟进学员项目：http://127.0.0.1:{args.port} · 保存功能待完成', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
