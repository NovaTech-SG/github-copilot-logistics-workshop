# copilot-shipment-tracker

运输异常跟进 · 讲师完成版，用于 Nike GC Logistics 的 GitHub Copilot Session 2。全部业务数据为培训模拟数据，不代表 Nike 实际运营情况。

**这个仓库用于先看效果、讲师演示和课后复盘。** 学员编码请打开同一工作坊下的 `copilot-shipment-tracker-starter`。课件中的 `shipment-tracker` 是本案例简称。完成版直接运行即可，不需要再执行 `/speckit-implement` 改写业务。

按顺序完成：环境 → 克隆与依赖 → MCP → 本地启动 → Spec Kit 复盘 → 验收。默认地址 **<http://127.0.0.1:8768>**。准备工作请在课前完成，课堂为本案例预留 15 分钟。

没有 Databricks 凭据时，仍可阅读规格、完成依赖安装和离线检查；页面业务数据及保存后重读验收需要实际 MCP 连接。


## 1. 准备电脑和账号

本文使用 **Windows + PowerShell**。仓库中的 Spec Kit 包装脚本为 `.ps1`，建议在 VS Code 的 PowerShell 终端操作。macOS/Linux 可运行 Python 应用，但本文不提供对应的完整课堂脚本。

| 准备项 | 要求及用途 |
|---|---|
| [Git](https://git-scm.com/downloads) | 克隆仓库、查看改动、提交 PR |
| [VS Code](https://code.visualstudio.com/) | 单独打开当前案例目录，登录有 Copilot 使用权限的 GitHub 账号，确认 Agent 聊天可用；按 IDE 提示启用 GitHub Copilot |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | 管理 Python 3.12 和本案例目录独立的 `.venv`，按 `uv.lock` 安装依赖 |
| [Node.js 22](https://nodejs.org/en/download) | 执行前端 JavaScript 语法检查；应用前端不需要 `npm install` |
| Databricks 账号及网络 | 能访问讲师指定工作区、SQL MCP 和培训表；具备对应 SQL Warehouse 使用权限 |
| 网络下载条件 | 首次准备需要下载 Python、PyPI 依赖和固定版本的 Spec Kit CLI；请在课前完成 |

安装工具后重新打开 PowerShell，检查：

```powershell
git --version
uv --version
node --version
```

Python 由下一步的 uv 安装，无需先配全局 Python、激活虚拟环境或单独安装 pip。无需 Docker、前端构建服务或本机 Databricks。Copilot Agent、MCP 和 Skills 还需组织策略允许使用；只登录 GitHub 不代表这些能力均已开放。

## 2. 克隆仓库，安装依赖并恢复课堂功能

下方命令使用本课程的公开仓库；使用 ZIP 时直接进入解压后的本案例目录目录，跳过 clone 和 cd。不要在工作坊根目录执行依赖安装。

```powershell
$GitHubOwner = 'NovaTech-SG'
git clone "https://github.com/$GitHubOwner/github-copilot-logistics-workshop.git"
cd github-copilot-logistics-workshop/copilot-shipment-tracker

uv python install 3.12
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
.\tools\speckit.ps1 integration status --json
```

首次 bootstrap 应输出 `restored`，再次运行输出 `preserved`；课堂检查应输出 `ready`；Spec Kit 完整性结果应为 `status: ok`，无缺失或被改写的官方文件。它们均不验证 MCP 或页面业务。

仓库已预装 **官方 Spec Kit 1.3.2** 的 Copilot Skills 和模板。`.\tools\speckit.ps1` 通过 uv 调用固定 CLI，首次可能需要下载；不用额外安装全局 `specify`，也不要重新执行 `specify init --force`。

当前功能为 `specs/001-exception-followup`。Spec Kit 忽略本机活动指针 `.specify/feature.json`，bootstrap 依据已提交的 `.specify/training.json` 恢复它，并保留已有有效选择。`uv sync --locked` 生成本案例目录自己的 `.venv`；后续命令都在本案例目录内运行。


## 3. 配置 Databricks MCP

### 3.1 先确认培训数据和权限

从讲师处获取工作区 Host、Catalog、Schema、已授权的访问方式及可用的 SQL MCP 地址。**克隆本案例目录不会创建 Databricks 表，也不附带讲师 Token 或共享账号。** 表名与字段约定见当前功能的 `spec.md`、`data-model.md` 和 `contracts/api.md`。

| 表 | 原始培训快照行数 |
|---|---:|
| `shipments` | 500 |
| `carriers` | 4 |
| `exceptions` | 169 |

表须为讲师已准备好的业务类型表，不使用 `*_raw` 表。若使用别的数据集，下文的固定验收数值不再适用。身份需具备对应 Catalog/Schema 使用权、表的读取权限以及可用的查询计算权限，由讲师或管理员分配。

本课使用 `/api/2.0/mcp/sql` 工作区端点，以及 `execute_sql_read_only`、`poll_sql_result` 工具。若工作区允许 PAT，可在个人设置的 Developer → Access tokens 生成短期令牌，选择 Other APIs 下的 `sql` 作用域，并以管理员要求为准。API 作用域不授予表权限，也不等于强制只读。应用仅调用只读工具，课堂身份也应限制为所需的读取权限。

Databricks 另有 Unity Gateway 的 `system.ai.dbsql` 入口；它的启用条件、权限和工具契约需另外核对。不要仅替换 URL 就假定与当前代码兼容。工作区只有其他入口或仅允许交互式 OAuth 时，先由讲师确认课程适配方式；当前 Python 应用不会自动完成浏览器 OAuth 登录或刷新令牌。

### 3.2 首次使用：环境变量方式

下面配置同时供 Python 应用与仓库中的 [.vscode/mcp.json](.vscode/mcp.json) 使用。请在 VS Code 之外单独打开 Windows PowerShell，先进入当前案例目录，再在**这个窗口**运行配置与启动命令；不要使用随后要关闭的 VS Code 集成终端。将 Host 换成自己的工作区根地址，不带 `/?o=...` 或末尾 `/`：

```powershell
$env:DATABRICKS_HOST = 'https://你的工作区.azuredatabricks.net'
$env:DATABRICKS_MCP_URL = "$env:DATABRICKS_HOST/api/2.0/mcp/sql"
$env:DATABRICKS_CATALOG = 'dev_databricks'
$env:DATABRICKS_SCHEMA = 'default'

$trainingSecureToken = Read-Host '输入个人 Databricks Token（隐藏输入）' -AsSecureString
try {
    $env:DATABRICKS_TOKEN = [System.Net.NetworkCredential]::new('', $trainingSecureToken).Password
} finally {
    $trainingSecureToken.Dispose()
    Remove-Variable trainingSecureToken
}
```

Catalog/Schema 换成培训实际位置。隐藏输入避免 Token 出现在命令文本中；应用仍需在本机进程内使用 Token。不要把凭据写入 README、聊天、前端或 Git。本项目不自动加载 `.env`。

环境变量只对当前终端及其后启动的子进程生效。Python 命令可以直接在本窗口运行；如需 VS Code 继承这些变量，保存工作后完全退出已有 VS Code 进程，再从此窗口打开仓库：

```powershell
code --new-window .
```

若 `code` 命令不可用，先按 VS Code 安装说明配置命令行入口；重新从桌面打开的 VS Code 不会自动继承另一个 PowerShell 窗口的临时变量。关闭本窗口后再次操作，需要重新设置地址和 Token。

仓库已提供以下兼容 VS Code Local 会话的配置，无需把实际 Token 填进去：

```json
{
  "servers": {
    "databricksTraining": {
      "type": "http",
      "url": "${env:DATABRICKS_HOST}/api/2.0/mcp/sql",
      "headers": {
        "Authorization": "Bearer ${env:DATABRICKS_TOKEN}"
      }
    }
  }
}
```

新版 VS Code 可能区分 Copilot 与 Local harness，以及 Global、用户和工作区配置。此仓库使用 `.vscode/mcp.json` 的 `servers` 格式；请在能读取该配置的 Local 会话中操作。如果 IDE 提示迁移配置，按[官方配置说明](https://code.visualstudio.com/docs/agent-customization/mcp-servers)选择对应会话和配置位置，再验证工具调用；不要仅因文件存在就认为 MCP 可用。

### 3.3 在 Copilot 中验证工具和表读取

单独打开当前案例目录，按组织要求信任工作区。通过命令面板的 `MCP: Add Server` 或 `Chat: Open Customizations` 中的 MCP 管理入口查看配置；已有的 `databricksTraining` 无需再次添加。也可打开 `.vscode/mcp.json`，使用可用的 Start/Restart 控件。核对信任及工具调用提示后，在 Agent 的工具列表中启用只读查询和轮询工具。不同 VS Code 版本入口可能不同。

在 **Copilot Agent 聊天框**发送以下内容，不是在 PowerShell 中执行；Catalog/Schema 不同则同步替换：

```text
请使用 databricksTraining 的 execute_sql_read_only 执行下面的只读 SQL。
如果仍在运行，用 poll_sql_result 等待查询完成，再报告实际结果。
不要修改文件，不调用写入工具，不凭预期值回答。
SELECT 'shipments' AS table_name, COUNT(*) AS row_count FROM dev_databricks.default.shipments
UNION ALL
SELECT 'carriers', COUNT(*) FROM dev_databricks.default.carriers
UNION ALL
SELECT 'exceptions', COUNT(*) FROM dev_databricks.default.exceptions;
```

展开聊天中的工具调用，确认执行的是该 MCP 的工具，且返回的实际计数与第 3.1 节一致。“Discovered tools”只说明发现了工具，浏览器登录也不代替应用的 Bearer Token。“浏览资源”灰色不影响仅提供 tools 的服务。

### 3.4 已有个人 MCP 配置：可选复用方式

如果你已在自己的 VS Code 配置中验证过 `databricksTraining`，可复用它，不必再配一份。Python 默认**不自动读取** VS Code 配置；使用 `--vscode-config` 才会读取：

```powershell
# Windows 普通 VS Code 用户配置的默认位置
uv run --locked python app.py --vscode-config --check
uv run --locked python app.py --vscode-config

# 如果使用工作区配置、其他 Profile 或其他配置位置，显式传入文件路径
uv run --locked python app.py --vscode-config .vscode/mcp.json --check
```

省略路径时，默认文件为 `%APPDATA%/Code/User/mcp.json`，不是工作区文件或 Copilot Global 配置。其他路径需自己指定；支持 JSON/JSONC，以及 `servers` 或 `mcpServers` 下名为 `databricksTraining` 的配置，认证头须为 `Bearer ...`。

Python 可展开 `${env:变量名}`，**不能读取 VS Code 的 `${input:...}` 或 IDE 中缓存的 OAuth 登录状态**。遇到这两种配置，按第 3.2 节为应用单独提供环境变量；不要把实际 Token 贴到配置里。`DATABRICKS_CATALOG` 和 `DATABRICKS_SCHEMA` 始终由应用进程的环境变量设置，与 MCP 配置文件分开。

**两条连接分别验证：** Copilot → MCP 用于开发时了解数据；浏览器 → 本地 Python → MCP 用于应用运行。前者成功不代表后者已配置好。页面必须读取运行时查询结果，不能把 Copilot 聊天返回值写死在代码中。

## 4. 检查连接并启动本地应用

完成第 3.2 节环境变量配置后，在**同一个 PowerShell 窗口**执行：

```powershell
uv run --locked python app.py --check
uv run --locked python app.py
```

第一条成功后再执行第二条；服务运行时终端会保持占用。打开 <http://127.0.0.1:8768>，保持终端开启；修改 Python 后 Ctrl+C 停止并重新启动，修改静态页面后刷新浏览器。

`--check` 会查询源异常并合并本地跟进记录，输出 `exception_count`、`counts` 和来源。首次使用空本地库时，培训快照为 169 条，OPEN 40、IN_PROGRESS 69、RESOLVED 60；保存过本机记录后，合并状态分布会改变。该检查不执行保存操作。

另一个便捷入口是 `.\start.ps1`：先设置 Host/Catalog/Schema，它会同步依赖并在缺少 Token 时隐藏提示输入；或者用 `.\start.ps1 -UseVSCodeConfig` 复用默认用户配置。两种入口不要混用配置来源；第 3.4 节的显式命令更适合排查路径问题。

**保存位置：** 源数据始终从 MCP 读取；状态与备注只存到本案例目录 `data/followups.sqlite3`，不会回写 Databricks。不同异常按 `exception_id` 区分，同一运输单的多条异常互不覆盖。该应用不是多人共享的云端工单系统。

想开新一轮练习而不影响已有记录，可指定新文件；验证重启恢复时必须使用同一个文件：

```powershell
uv run --locked python app.py --db data/practice-02.sqlite3
```

新练习首次请选择尚不存在的文件名，不要删除旧库。源查询最多返回 500 条异常；超限或截断会报错，不展示不完整列表。


## 5. 使用 Spec Kit 复盘

SDD（Specification-Driven Development，规格驱动开发）先把需求、边界和验收写清楚，再据此计划、拆任务、实现和验证。Spec Kit 提供相应模板与 Agent Skills；它不会替你判断业务口径，也不以文档齐全或任务勾选代替运行验收。

| 先读的文件 | 用途 |
|---|---|
| [AGENTS.md](AGENTS.md) | Agent 的项目范围、凭据与数据边界 |
| [constitution](.specify/memory/constitution.md) | 项目原则 |
| [spec.md](specs/001-exception-followup/spec.md) | 要做什么、业务规则与验收条件 |
| [plan.md](specs/001-exception-followup/plan.md) | 怎样实现、沿用哪些组件 |
| [tasks.md](specs/001-exception-followup/tasks.md) | 按依赖推进的任务与课堂范围 |
| [完整课堂提示词](docs/prompts.md) | 可逐条复制到 Copilot 的技能调用 |
| [Spec Kit 操作说明](docs/speckit.md) | 版本、检查点及课前准备说明 |

这些规格、计划和任务是课前准备的检查点，不是已执行成功的 Copilot 对话记录。学员不需要在 15 分钟内从零重建全部材料。

在 VS Code 的 Copilot Agent 聊天中输入 `/`，确认能选择 `/speckit-specify`、`/speckit-plan`、`/speckit-tasks`、`/speckit-implement` 等。此项目的技能需手动调用；**下面的斜杠命令是聊天消息，不是终端命令**。CLI 的 `integration status` 通过也不能证明 IDE 已发现技能。

建议先按第 6 节运行验收，再阅读代码对应的任务，最后在 Agent 中做只读复盘：

```text
请先读 AGENTS.md、constitution 和 specs/001-exception-followup 中的 spec、plan、tasks。
只读解释当前实现分别满足哪些验收条件，并指出还需要哪些实际运行证据。
不要运行 implement，不修改文件，不读取或输出 Token，不提交、推送或部署。
```

`/speckit-analyze` 可用于只读检查 spec/plan/tasks 的一致性。真正的生成与实现练习在 `copilot-shipment-tracker-starter` 进行，按它的 README 与课堂提示词操作；不要在完成版重新跑 implement 或盲目重建规格。


## 6. 验收：区分离线检查与实际效果

### 离线检查（不需要 Databricks 凭据）

```powershell
uv run --locked python tools/check_training.py
uv run --locked python -m unittest discover -s tests -v
node --check static/app.js
```

完成版当前有 10 项离线测试。它们使用构造的 MCP 响应和临时数据库，不连接真实 Databricks。

### 实际业务验收（需要 MCP 和培训快照）

1. 在空本地练习库下读取列表，确认 169 条及初始分布 40 / 69 / 60。
2. 选择一条 OPEN 异常，记下 `exception_id`，改为 IN_PROGRESS，填写非空备注并保存。
3. 确认页面提示“已保存到本机，并重新读取确认”，重新打开相同编号核对状态与备注；源状态仍单独显示。
4. 刷新页面，再 Ctrl+C 停服务，用**相同 `--db` 文件路径**重启，确认记录保留。跟进状态变化后概览不应继续固定为初始分布。
5. 验证空白/超长备注、跳过或退回状态、过期原状态会被拒绝，失败不改变原记录；另一条异常不受影响。

教学规则：`OPEN → IN_PROGRESS → RESOLVED`，可在同状态更新备注；去掉首尾空格后备注必填、最多 1000 字。它们是本练习的规则，不是 Nike 生产流程定义。

把实际执行、结果和未验证项写入 [docs/validation.md](docs/validation.md)。详细场景见 [acceptance.md](specs/001-exception-followup/acceptance.md)。`ready`、离线测试通过、MCP 成功和页面验收是不同证据，分别记录。

### PR 与 CI

完成跟练后先 `git diff -- .` 审查改动、凭据和业务范围，再按讲师安排提交分支与 PR。工作坊根目录的 [CI](../.github/workflows/ci.yml) 在 push/PR 时恢复活动功能、检查课堂结构、运行离线检查及 JavaScript 语法检查。它不使用 Databricks Token、不查询现场数据、不部署服务器；绿色 CI 不能代替真实 MCP 和浏览器验收。


## 7. 常见问题

| 现象 | 处理方法 |
|---|---|
| `uv`、`git`、`node` 找不到 | 安装后重开终端，检查 PATH；Python 用 `uv run`，不用系统 `python` 代替 |
| uv 下载失败或证书错误 | 检查公司代理、PyPI 与 Python 下载访问；按组织证书方案配置，不关闭 TLS 验证 |
| PowerShell 拒绝 `.ps1` | 若是 ZIP 解压文件，检查文件阻止属性；按公司批准的脚本执行策略处理，受管电脑请联系 IT。Python 的 bootstrap/check 命令可先单独执行 |
| `feature.json` 不存在 | 运行 `uv run --locked python tools/bootstrap_training.py`；它恢复当前课堂功能，不覆盖有效选择 |
| `check_training.py` 不通过 | 先看报错中的文件或功能目录。它检查本课堂预置结构和范围；主动切换了其他功能时，不能据此判断新功能有问题 |
| `/speckit-*` 不显示 | 确认只打开本案例目录、当前会话支持 `.github/skills`、Copilot 可用且组织允许；重载窗口并检查 IDE 的技能发现能力。不要重跑 init 覆盖材料 |
| 缺少 Token 或提示未展开变量 | 核对运行应用的终端是否已设环境变量；`${input:...}` 只能由 IDE 处理，Python 不支持。项目不会自动读 `.env` |
| MCP 返回 401/403 | 检查 Token 过期、工作区、`sql` 作用域、MCP 开放条件与表/计算权限；能列工具不等于能读表 |
| 弹出 OAuth 客户端注册或 `invalid_request` | 说明当前会话走了交互式 OAuth；它与本文 Bearer Token 路径不同。请讲师核对所选配置和组织认证方式，不把 PAT 填到 OAuth client ID |
| service 不存在或无权访问 | 确认完整 MCP 地址，勿混用 `/api/2.0/mcp/sql` 与 `system.ai.dbsql`；按实际服务检查启用条件及权限 |
| Copilot 能查，Python 查不到 | 区分 IDE 登录缓存与应用凭据，核对默认/显式配置路径、环境变量是否继承；IDE 工具无需常驻来代理 Python 请求 |
| 查不到表、字段类型错误或数值不符 | 核对 Catalog/Schema、业务类型表与培训快照；不要改成 `_raw` 表或用固定值掩盖查询问题 |
| 端口已占用 | Ctrl+C 停止自己启动的旧进程，或用 `uv run --locked python app.py --port 8877` 并打开对应地址 |
| 页面一直加载、502 或结果被截断 | 查看应用终端及 MCP 实际错误；检查网络、查询计算与结果完整性。修复后重试，不以固定数据兜底 |

排查时可提供脱敏后的错误类型、表名和执行步骤；不要发送 Token 或完整的个人配置文件。

## 8. 文件导航与参考

| 路径 | 用途 |
|---|---|
| `app.py` / `start.ps1` | 本地服务、命令行参数与启动脚本 |
| `services/settings.py` | 环境变量和显式 MCP 配置读取 |
| `services/mcp_sql.py` | 只读查询、轮询与结果解析 |
| `services/queries.py` | 业务 SQL |
| `services/tracker.py / services/store.py` | 业务调用、状态校验和本地持久化 |
| `static/` | 原生 HTML/CSS/JavaScript |
| `specs/001-exception-followup/` | 当前功能的规格、计划、任务、数据模型与验收 |
| `docs/spec.md` / `docs/tasks.md` | 指向当前功能文件的兼容入口 |
| `tools/bootstrap_training.py` / `tools/check_training.py` | 首次克隆准备与课堂结构检查 |

各案例独立安装依赖、运行与保存练习结果。`.venv`、实际凭据、`data/` 与本机活动指针不提交到 Git。第三方 Spec Kit 材料的来源和许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

官方参考（2026-11-09 核对；本课固定 Spec Kit 1.3.2，IDE 界面可能随版本调整）：

- [uv 安装](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code MCP 配置与首次工具验证](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [Spec Kit 的 Copilot Skills 集成](https://github.github.io/spec-kit/integrations/copilot.html)
- [Databricks 工作区 MCP 端点与 Unity Gateway 的区别](https://learn.microsoft.com/en-us/azure/databricks/agents/mcp-tools/built-in-mcp-services)
- [Databricks PAT 与作用域](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat)
