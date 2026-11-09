import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import json5


@dataclass(frozen=True)
class Settings:
    url: str
    token: str = field(repr=False)
    catalog: str = "dev_databricks"
    schema: str = "default"

    def __post_init__(self):
        parsed = urlsplit(self.url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("MCP 地址应为不含账号、查询参数的 HTTPS URL。")
        if not self.token or "${" in self.token:
            raise ValueError("尚未提供 Databricks Token，请设置环境变量或显式选择 VS Code 配置。")
        for value in (self.catalog, self.schema):
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                raise ValueError("Catalog 和 Schema 必须为有效标识符。")

    @property
    def table_prefix(self):
        return f"`{self.catalog}`.`{self.schema}`"


def expand_env(value):
    def replace(match):
        name = match.group(1)
        if name.startswith("env:"):
            name = name[4:]
        return os.environ.get(name, match.group(0))
    return re.sub(r"\$\{([^}]+)\}", replace, value)


def load_settings(vscode_config=None):
    catalog = os.environ.get("DATABRICKS_CATALOG", "dev_databricks")
    schema = os.environ.get("DATABRICKS_SCHEMA", "default")
    if vscode_config:
        data = json5.loads(Path(vscode_config).read_text(encoding="utf-8-sig"))
        server = data.get("servers", data.get("mcpServers", {})).get("databricksTraining")
        if not server:
            raise ValueError("所选配置中没有 databricksTraining。")
        url = expand_env(server["url"])
        authorization = next((value for key,value in server.get("headers", {}).items() if key.lower() == "authorization"), "")
        authorization = expand_env(authorization)
        if not authorization.startswith("Bearer "):
            raise ValueError("所选配置需提供 Bearer Token。")
        return Settings(url, authorization[7:].strip(), catalog, schema)
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    url = os.environ.get("DATABRICKS_MCP_URL") or (host + "/api/2.0/mcp/sql" if host else "")
    return Settings(url, os.environ.get("DATABRICKS_TOKEN", ""), catalog, schema)
