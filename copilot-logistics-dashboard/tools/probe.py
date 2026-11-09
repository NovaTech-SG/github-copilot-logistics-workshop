"""只读测试：打印SELECT 1的工具响应，不打印凭据。"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.settings import load_settings
from services.mcp_sql import probe

parser = argparse.ArgumentParser()
parser.add_argument("--vscode-config", type=Path)
args = parser.parse_args()
settings = load_settings(args.vscode_config)
try:
    print(json.dumps(asyncio.run(probe(settings)), ensure_ascii=False).replace(settings.token,"[REDACTED]"))
except Exception as error:
    print(str(error).replace(settings.token,"[REDACTED]"))
    raise SystemExit(1)
