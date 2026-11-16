# 运输异常跟进 学员起始项目

在已有异常队列上新增本机 SQLite 保存和前端重读确认。列表、搜索筛选、分页、详情与源查询已提供。

先看 [数据来源与表关系](docs/data-source.md) 和 [需求提示词](docs/prompts.md)。本项目独立运行，端口 8769；所有业务数据为培训模拟数据。


## 1 准备环境与依赖

使用 Windows PowerShell，准备 Git、VS Code 与可用的 Copilot Agent、uv、Node.js 22。Python 3.12 由 uv 安装，前端无需 npm install；账号与组织策略需允许 MCP 和 Skills。

第一次获取代码时：

```powershell
git clone https://github.com/NovaTech-SG/github-copilot-logistics-workshop.git
cd github-copilot-logistics-workshop/copilot-shipment-tracker-starter
```

已经克隆或下载 ZIP 时，直接进入本项目目录。后续所有命令都在这里执行：

```powershell
uv python install 3.12
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
```

初始 bootstrap 输出 `awaiting_specification`，检查输出 `ready` 和 `stage: requirements`。不会生成预写规格。有有效选择时保留；新克隆只有一份已写好的 spec 时，仅恢复本机活动指针，输出 `restored_selection`；多份未选择时提示人工选择，不猜测。

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
使用 databricksTraining 的只读工具，查询 dev_databricks.default 下 carriers、shipments、exceptions 的实际行数；未完成时轮询到结束。展开工具结果核对，不修改文件或数据，不根据预期值回答。
```

培训 CSV 对应的原始快照是 承运商 4、运输单 500、异常 169。表可能更新，以本次实际查询为准。

**Python 运行连接：** 在同一 PowerShell 中执行：

```powershell
uv run --locked python app.py --check
uv run --locked python app.py
```

打开 <http://127.0.0.1:8769>。`--check` 查询异常并合并本机记录，不执行保存；空本机库的原始培训快照为 169 条，状态分布 40 / 69 / 60。已有本机记录会改变合并后的分布。

状态与备注只存当前项目 `data/followups.sqlite3`，按 `exception_id` 区分，不回写 Databricks。新练习可加 `--db data/practice-02.sqlite3` 使用尚不存在的文件；重启验证必须使用同一文件，不删除旧记录。源查询超出 500 条或截断时会报错。

起始版可读列表和详情；保存按钮提示练习未完成，保存 API 返回 501，属于正常起点。

Copilot 连接用于开发时了解数据，Python 连接供应用运行；两条连接分别验证。浏览器只访问本地 Python，不持有 Token，也不使用聊天结果代替运行时查询。


## 3 用 Spec Kit 跟练

先读 [数据与规则](docs/data-source.md)，查看 [新增功能效果稿](mockup/index.html)，再复制 [一句话需求](docs/prompts.md) 到 Copilot Agent 聊天。

| 顺序 | 单独发送的聊天消息 | 本步审阅 |
|---|---|---|
| 1 | docs/prompts.md 中的 `/speckit-specify ...` | 已有基础、新增保存与确认的验收 |
| 2 | 有歧义时 `/speckit-clarify` | 状态、备注、过期提交和重读失败 |
| 3 | `/speckit-plan` | 复用已有读取、校验、事务与 overlay |
| 4 | `/speckit-tasks`，再单独 `/speckit-analyze` | 后端、前端、必要测试与依赖 |
| 5 | `/speckit-implement 只实现后端保存与必要测试` | 原状态校验、参数化写入与事务 |
| 6 | `/speckit-implement 只实现前端提交与确认` | POST 后 GET 核对，失败与防重复提交 |
| 7 | `/speckit-converge` | 保存恢复、错误边界与已有功能无回归 |

这些是聊天技能，不是终端命令。每步审阅后继续，目录与任务 ID 以实际生成结果为准。初始没有 spec/plan/tasks，由课堂逐步生成；不读取相邻完成版答案。

课堂 15 分钟只补 `FollowUpStore.save`、前端 submit 和必要测试。保留已有队列、搜索筛选、分页、详情、源查询、校验和 SQLite 结构。效果稿只展示目标，不参与查询或保存。

## 4 验收

离线检查不需要 Databricks 凭据：

```powershell
uv run --locked python tools/check_training.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m compileall -q app.py services tools
node --check static/app.js
```

起始测试覆盖已有输入校验和 SDD 阶段；实施时补保存、重读、非法输入、过期状态与失败不写入的测试。`ready` 不表示保存功能已完成。

使用实际 MCP 和页面核对：

1. 用空本机练习库读取培训快照：169 条，OPEN / IN_PROGRESS / RESOLVED 为 40 / 69 / 60。
2. 选择 OPEN 异常，记下编号，改为 IN_PROGRESS 并填备注，保存后重新 GET 同一异常核对，确认后再显示成功。
3. 刷新，再停止服务，用同一 `--db` 文件重启，状态与备注仍保留，概览同步更新；源状态单独显示。
4. 空白或超长备注、跳过或退回状态、过期原状态均拒绝，失败不改变已有记录；同一运输单的另一条异常不受影响。
5. 提交失败与已提交但未确认分别反馈，未确认时不显示成功；保存期间不能重复提交。

状态按 OPEN → IN_PROGRESS → RESOLVED 推进，可同状态补备注；备注去首尾空格后必填且最多 1000 字。这些是教学规则，不代表 Nike 生产流程。

起始版保存尚未实现，先完成第 3 节再验收持久化。记录实际执行和未验证项；提交前检查 `git diff -- .`。根目录 CI 仅离线检查，不连接 Databricks、不部署。


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

端口占用时停止自己启动的旧服务，或加 `--port 8877` 并访问新地址。切换练习库使用 `--db data/practice-02.sqlite3`。

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
- `services/queries.py`、`services/tracker.py`：已有异常查询；`services/store.py`：本机存储。
- `static/`：实际应用页面；`tests/`：离线测试。
- `mockup/`：静态目标；`specs/`：初始为空，跟练时生成规格、计划和任务。

`AGENTS.md`、`.github/copilot-instructions.md` 和 `.specify/memory/constitution.md` 已配置项目边界；`.github/skills/` 与 `.specify/templates/` 是工具文件。保留这些文件，日常跟练先读 README 和 docs。第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

参考：[uv 安装](https://docs.astral.sh/uv/getting-started/installation/) · [Spec Kit Copilot Skills](https://github.github.io/spec-kit/integrations/copilot.html) · [VS Code MCP](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
