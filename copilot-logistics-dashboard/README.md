# 物流 Dashboard 参考完成版

用于运行完整效果和只读复盘规格、代码与验收；编码跟练使用 starter 项目。

先看 [数据来源](docs/data-source.md)、[业务规格](specs/001-carrier-dashboard/spec.md) 和 [复盘提示词](docs/prompts.md)。本项目独立运行，端口 8766；所有业务数据为培训模拟数据。


## 1 准备环境与依赖

使用 Windows PowerShell，准备 Git、VS Code 与可用的 Copilot Agent、uv、Node.js 22。Python 3.12 由 uv 安装，前端无需 npm install；账号与组织策略需允许 MCP 和 Skills。

第一次获取代码时：

```powershell
git clone https://github.com/NovaTech-SG/github-copilot-logistics-workshop.git
cd github-copilot-logistics-workshop/copilot-logistics-dashboard
```

已经克隆或下载 ZIP 时，直接进入本项目目录。后续所有命令都在这里执行：

```powershell
uv python install 3.12
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
```

bootstrap 恢复 `specs/001-carrier-dashboard` 的本机活动指针，保留已有有效选择；结构检查预期输出 `ready`。

已预装官方 Spec Kit 1.3.2 的 Copilot Skills 和模板，不用安装全局 specify 或重新 init。若需检查工具文件：

```powershell
.\tools\speckit.ps1 integration status --json
```

## 2 配置并验证两条 MCP 连接

从讲师处获取工作区、Catalog、Schema 和个人访问授权。当前代码要求 SQL MCP 提供 `execute_sql_read_only`、`poll_sql_result`；表和计算资源需要相应读取与使用权限。

若已配置用户环境变量，完全退出并重新打开终端和 VS Code 后使用。临时配置可在 VS Code 之外的 PowerShell 中执行，替换示例值：

```powershell
$env:DATABRICKS_HOST = 'https://你的工作区.azuredatabricks.net'
$env:DATABRICKS_HOSTNAME = ([uri]$env:DATABRICKS_HOST).Host
$env:DATABRICKS_CATALOG = 'dev_databricks'
$env:DATABRICKS_SCHEMA = 'default'
$trainingToken = Read-Host '输入个人 Databricks Token' -AsSecureString
try {
    $env:DATABRICKS_TOKEN = [System.Net.NetworkCredential]::new('', $trainingToken).Password
} finally {
    $trainingToken.Dispose()
    Remove-Variable trainingToken
}
```

Host 不带 `/?o=...`；`DATABRICKS_HOSTNAME` 只放域名。Token 不写进聊天、代码或共享配置。临时变量仅供当前窗口及其子进程使用；完全退出已有 VS Code 后，从此窗口打开项目：

```powershell
code --new-window .
```

**Copilot 开发连接：** 仓库已提供 `.vscode/mcp.json`。在能读取此配置的 Local 会话中，通过 `Chat: Open Customizations` 的 MCP 管理入口或配置文件的 Start/Restart 启用 `databricksTraining`，按提示确认信任与工具使用。新版 Copilot harness 使用不同配置位置时，按 [VS Code 官方说明](https://code.visualstudio.com/docs/agent-customization/mcp-servers)在当前会话配置并验证。

在 Copilot Agent 聊天中发送以下消息；实际 Catalog/Schema 不同则替换：

```text
使用 databricksTraining 的只读工具，查询 dev_databricks.default 下 carriers、shipments 的实际行数；未完成时轮询到结束。展开工具结果核对，不修改文件或数据，不根据预期值回答。
```

培训 CSV 对应的原始快照是 承运商 4、运输单 500。表可能更新，以本次实际查询为准。

**Python 运行连接：** 在同一 PowerShell 中执行：

```powershell
uv run --locked python app.py --check
uv run --locked python app.py
```

`--check` 查询 Dashboard 业务指标并退出；成功后再启动服务，打开 <http://127.0.0.1:8766>。页面应展示指标、筛选、对比、趋势和明细。

Copilot 连接用于开发时了解数据，Python 连接供应用运行；两条连接分别验证。浏览器只访问本地 Python，不持有 Token，也不使用聊天结果代替运行时查询。


## 3 只读复盘

按 [提示词](docs/prompts.md) 理解业务规则、浏览器到 MCP 的调用路径，再对照 [spec](specs/001-carrier-dashboard/spec.md)、[plan](specs/001-carrier-dashboard/plan.md) 和 [tasks](specs/001-carrier-dashboard/tasks.md)。可在 Copilot Agent 聊天逐条调用 `/speckit-analyze` 检查文档一致性；没有变更需求时不执行 implement。

预置规格和任务供参考，任务勾选不代表本次实际运行通过。课堂生成与编码请使用对应 starter，只读复盘完成版放在练习之后。

## 4 验收

```powershell
uv run --locked python tools/check_training.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m compileall -q app.py services tools
node --check static/app.js
```

离线测试使用构造响应，不访问 Databricks。详细场景见 [acceptance.md](specs/001-carrier-dashboard/acceptance.md)。

| 培训快照范围 | 总量 | 有效 | 准时 | 延误 | 准时率 |
|---|---:|---:|---:|---:|---:|
| 全部 | 500 | 380 | 304 | 76 | 80.00% |
| CAR002 | 134 | 104 | 77 | 27 | 74.04% |

清除筛选恢复全部，零分母显示 N/A，查询失败明确反馈。趋势合计等于范围单量；CAR002 共 7 页且末页 14 条，相邻页不重复。快照与查询时间分别标注，桌面和窄屏均检查。

下列命令会访问真实 MCP，第二条要求培训快照未变更：

```powershell
uv run --locked python app.py --check --carrier CAR002
uv run --locked python tools/verify_live.py
```

使用配置文件认证时，两条命令都加同样的 `--vscode-config` 参数。

记录本次离线、实时 MCP、页面操作和未验证项。根目录 CI 只做离线检查，不查询现场数据、不部署；提交前检查 `git diff -- .`。


## 按需调试与排错

<details>
<summary>F5 调试、复用已有配置和启动参数</summary>

```powershell
Copy-Item .env.example .env
```

填写自己的值后，用 `.vscode/launch.json` 的 F5 配置启动；Python 修改后停止再启动。`.env` 只由 F5 注入，普通终端启动不会读取它，也不会配置 Copilot MCP。空的 `DATABRICKS_TOKEN=` 会覆盖已有变量，不使用时注释掉该行。编辑器的 Run Python File 不使用 launch.json。

应用可显式读取已有的工作区 MCP 配置：

```powershell
uv run --locked python app.py --vscode-config .vscode/mcp.json --check
uv run --locked python app.py --vscode-config .vscode/mcp.json
```

也可用 `.\start.ps1` 启动；`--vscode-config` 不指定路径时读取 `%APPDATA%/Code/User/mcp.json`。仅支持 Bearer Token 及 `${env:...}`，不读取 IDE 的 `${input:...}` 或 OAuth 缓存。Catalog/Schema 仍由环境变量设置。

端口占用时停止自己启动的旧服务，或加 `--port 8877` 并访问新地址。

</details>

| 现象 | 处理 |
|---|---|
| 工具找不到、下载失败或脚本被阻止 | 安装后重开终端，核对 PATH、网络代理与组织脚本策略；Python 使用 uv run |
| `/speckit-*` 不显示 | 只打开当前项目，核对会话支持 `.github/skills` 与组织授权，再重载窗口；不重新 init 覆盖材料 |
| MCP 不出现、无法启动或变量为空 | 核对配置所属会话和范围、VS Code 是否继承变量，再查看该服务器输出 |
| 401/403 或查不到表 | 核对 Token、工作区、Catalog/Schema、MCP 及表和计算权限；发现工具不代表能读表 |
| Copilot 可查而 Python 失败 | 核对应用所在进程的环境与配置路径；IDE 登录缓存不代替应用凭据 |
| `feature.json` 缺失或结构检查失败 | 先运行 bootstrap；若已有指针，核对其是否指向本项目对应参考规格，保留原文件再处理 |

遇到 OAuth 注册提示、其他 MCP 地址或结果截断时，核对组织提供的接入方式与实际工具契约，不仅替换 URL。提供脱敏错误和步骤即可，不发送 Token 或完整个人配置。

## 文件位置

- `services/settings.py`、`services/mcp_sql.py`：配置、只读查询、轮询与解析。
- `services/queries.py`、`services/dashboard.py`：业务查询与指标整理。
- `static/`：实际应用页面；`tests/`：离线测试。
- `specs/001-carrier-dashboard/`：参考规格、方案、任务与验收。

`AGENTS.md`、`.github/copilot-instructions.md` 和 `.specify/memory/constitution.md` 已配置项目边界；`.github/skills/` 与 `.specify/templates/` 是工具文件。保留这些文件，日常跟练先读 README 和 docs。第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

参考：[uv 安装](https://docs.astral.sh/uv/getting-started/installation/) · [Spec Kit Copilot Skills](https://github.github.io/spec-kit/integrations/copilot.html) · [VS Code MCP](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
