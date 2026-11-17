# 物流 Dashboard 学员起始项目

本项目由技术骨架和空规格开始，通过需求、mockup 与 Spec Kit 构建运输表现看板。当前课堂已实现 P1 与 P2：四指标、承运商筛选与对比、状态反馈、每日趋势、20 条分页明细及时间说明。当前设计与任务见 [功能目录](specs/001-transport-performance-dashboard/plan.md)。

先看 [数据来源与表关系](docs/data-source.md) 和 [需求提示词](docs/prompts.md)。本项目独立运行，端口 8767；所有业务数据为培训模拟数据。


## 1 安装依赖

使用 Windows PowerShell，准备 Git、VS Code 与可用的 Copilot Agent、uv、Node.js 22。Python 3.12 由 uv 安装，前端无需 npm install；账号与组织策略需允许 MCP 和 Skills。

下载或克隆仓库后，在 VS Code 中只打开 `copilot-logistics-dashboard-starter`，在该目录的终端执行：

```powershell
uv sync
```

项目已包含 `.python-version`（3.12）、`pyproject.toml` 和 `uv.lock`，uv 会自动准备 Python、创建本项目 `.venv` 并安装依赖。Spec Kit Skills 与模板也已提供；首次使用无需运行 bootstrap 或重新 init。后续命令均在当前 starter 目录执行。

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

`--check` 仅执行 SELECT 1，预期 `connection: OK`、`business_verified: false`，不证明业务表可读。启动后打开 <http://127.0.0.1:8767>，页面通过 `/api/dashboard` 查询真实业务数据。参数错误返回 400，源查询或结果校验失败返回 502；失败明确报错并允许重试，不使用固定样例兜底。

Copilot 连接用于开发时了解数据，Python 连接供应用运行；两条连接分别验证。浏览器只访问本地 Python，不持有 Token，也不使用聊天结果代替运行时查询。

### 在 VS Code 中按 F5 调试

1. 完成第 1 节的 `uv sync`，按工作区推荐安装或启用 **Python** 和 **Python Debugger** 扩展；调试配置固定使用本项目 `.venv`。
2. 使用 VS Code 已继承的用户环境变量，或复制 `.env.example` 为本机 `.env` 后填写。`.env` 同名值优先，空 Token 或示例 Host 会覆盖已有配置；只使用用户变量时删掉或注释这些行。
3. 按 `Ctrl+Shift+D` 打开“运行和调试”，选择“看板：启动网页”，按 `F5`，访问 <http://127.0.0.1:8767>。选择“检查连接”则只执行 `--check`。
4. 按 `F9` 设置断点，`Shift+F5` 停止。修改 Python 后重新启动；也可用 `Ctrl+F5` 运行而不调试。

`.vscode/launch.json` 已提供，无需重新生成。`.env` 由此调试配置注入，普通终端启动不会自动读取，也不配置 Copilot MCP；编辑器的 Run Python File 不使用这份启动配置。


## 3 用 Spec Kit 跟练

先读 [数据与口径](docs/data-source.md)，在浏览器打开 [静态效果稿](mockup/index.html)，再复制 [一句话需求](docs/prompts.md) 到 Copilot Agent 聊天。效果稿中的数字仅作示意，控件不可操作。

| 顺序 | 单独发送的聊天消息 | 本步审阅 |
|---|---|---|
| 1 | docs/prompts.md 中的 `/speckit-specify ...` | 业务场景、统计口径、P1 与 P2 验收 |
| 2 | 有歧义时 `/speckit-clarify` | 分母、相等时间、空范围与失败行为 |
| 3 | `/speckit-plan 沿用现有 Python、只读 MCP 和原生前端骨架，P1 后端与前端分轮，P2 单列` | 连接模块的输入输出、接口和实施范围 |
| 4 | `/speckit-tasks`，再单独 `/speckit-analyze` | 依赖、任务分组、必要测试与一致性 |
| 5 | `/speckit-implement 只实现 P1 后端查询、参数校验、指标与必要测试` | SQL、返回结构和边界结果 |
| 6 | `/speckit-implement 只实现 P1 前端指标、筛选、对比图与状态反馈` | mockup 布局与实际 API 数据 |
| 7 | `/speckit-converge 只核对 P1，P2 保留为扩展` | 本次缺口、验收结果与未验证项 |

这些是聊天技能，不是终端命令。每步审阅后继续，规格目录与任务 ID 以实际生成结果为准。初始没有 spec/plan/tasks，由课堂逐步生成；不读取相邻完成版的答案。

课堂 15 分钟先做 P1：四指标、承运商筛选和清除、重新查询、准时率对比，以及加载、空结果、N/A 和失败重试。之后如需达到完整 mockup，再调用 `/speckit-implement 只实现 P2 任务`，补趋势、自然日补零、20 条分页和时间说明，并按全部范围 converge。

## 4 验收

离线检查不需要 Databricks 凭据：

```powershell
uv run --locked python tools/check_training.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m compileall -q app.py services tools
node --check static/app.js
```

测试包含课堂阶段/文件保护，以及参数校验、HTTP 合同、MCP 编排、失败响应、指标不变量和分页数据校验。默认离线测试跳过需要明确启用的 5 项真实 SQL 测试。结构检查识别 `requirements → specified → planned → tasks-generated`，`ready` 不表示业务已完成。

要验证生成 SQL 的真实业务语义，可在本机连接配置已就绪后显式启用只读测试。它们将构造的 `VALUES`/CTE 集合作为查询输入，不写入业务表，也不作为应用数据源：

```powershell
$env:DASHBOARD_LIVE_TESTS = '1'
$env:DASHBOARD_VSCODE_CONFIG = '.vscode\mcp.json'
uv run --locked python -m unittest discover -s tests -p 'test_queries.py' -v
Remove-Item Env:DASHBOARD_LIVE_TESTS
Remove-Item Env:DASHBOARD_VSCODE_CONFIG
```

这些测试覆盖恰好到达、有效分母、整体加权比例、重复承运商资料、未知名称、缺日补零、空范围以及 41 单的稳定分页；运行时仍只读取配置的 Databricks 业务源。详细步骤见 [验收指南](specs/001-transport-performance-dashboard/quickstart.md)。

使用未变更的培训快照，通过实际 MCP 和页面核对：

| 操作 | P1 预期 |
|---|---|
| 全部 | 总量 500、有效 380、准时 304、延误 76、排除 120、准时率 80.00% |
| 筛选 CAR002 | 总量 134、有效 104、准时 77、延误 27、准时率 74.04%；指标与对比范围同步 |
| 清除 | 恢复全部范围 |
| 空范围、零分母、查询失败 | 分别提示无记录、N/A、错误并允许重试；可用离线用例补边界验证 |

P2 验收：趋势合计等于范围单量、缺失自然日补零；全部 25 页，CAR002 共 7 页且末页 14 条，相邻页无重复，换筛选回第 1 页；快照与查询完成时间分别显示为 Asia/Shanghai。桌面与窄屏均可使用。

记录实际执行与未验证项。提交前检查 `git diff -- .`；根目录 CI 仅运行离线检查，不连接 Databricks、不部署。


## 按需调试与排错

<details>
<summary>检查 Spec Kit 或恢复已有规格（可选）</summary>

核对预装工具状态：

```powershell
.\tools\speckit.ps1 integration status --json
```

重新下载已有学习成果，且只有一份 spec、缺少活动选择时，可恢复本机指针：

```powershell
uv run python tools/bootstrap_training.py
```

初始空 `specs/` 无需执行此步骤；bootstrap 不生成规格，已有有效选择会保留，多份未选择时需人工选择。结构检查与测试见第 4 节。

</details>

<details>
<summary>复用已有 MCP 配置和启动参数</summary>

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
| `feature.json` 缺失或结构检查失败 | 空 specs 时正常；已有唯一 spec 先运行 bootstrap；多份 spec 需在 `.specify/feature.json` 选择本项目目录。按 spec → plan → tasks 顺序核对，保留已有成果 |

遇到 OAuth 注册提示、其他 MCP 地址或结果截断时，核对组织提供的接入方式与实际工具契约，不仅替换 URL。提供脱敏错误和步骤即可，不发送 Token 或完整个人配置。

## 文件位置

- `services/settings.py`、`services/mcp_sql.py`：配置、只读查询、轮询与解析。
- `services/queries.py`、`services/dashboard.py`：业务查询与指标整理。
- `static/`：实际应用页面；`tests/`：离线测试。
- `mockup/`：静态目标；`specs/`：初始为空，跟练时生成规格、计划和任务。

`AGENTS.md`、`.github/copilot-instructions.md` 和 `.specify/memory/constitution.md` 已配置项目边界；`.github/skills/` 与 `.specify/templates/` 是工具文件。保留这些文件，日常跟练先读 README 和 docs。第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

参考：[uv 安装](https://docs.astral.sh/uv/getting-started/installation/) · [Spec Kit Copilot Skills](https://github.github.io/spec-kit/integrations/copilot.html) · [VS Code MCP](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
