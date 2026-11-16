# copilot-shipment-tracker-starter

运输异常跟进 · 学员起始项目，用于 Nike GC Logistics 的 GitHub Copilot Session 2。全部业务数据为培训模拟数据，不代表 Nike 实际运营情况。

**从这个仓库开始跟练。** 对应完成版目录为 `copilot-shipment-tracker`，留作课后核对；课堂请只打开本案例目录，不让 Agent 读取相邻完成版。课件中的 `shipment-tracker-starter` 是本案例简称。

这是在现有应用上新增功能的练习。异常读取、列表、详情、规则校验与 SQLite 表结构已提供；学员参考 mockup，从空规格生成本机保存与重读确认的需求、方案和任务，再实现两处 TODO。

> [!IMPORTANT]
> 起始版能读取列表，但点保存会提示“课堂练习：请完成……”，保存 API 返回 **501**，属于**预期状态**。实现 P1 后才能进入持久化验收。

## 概览

| 项 | 内容 |
|---|---|
| 课程 | GitHub Copilot Session 2 · Nike GC Logistics |
| 角色 | 学员起始项目（对应完成版：`copilot-shipment-tracker`） |
| 预计用时 | 课前准备约 30 分钟；课堂 15 分钟 |
| 默认地址 | <http://127.0.0.1:8769> |
| 已提供 | MCP 连接、异常查询、列表与详情、规则校验、SQLite 表结构、前端骨架 |
| 需要完成 | `services/store.py` 的 `save`、`static/app.js` 的 submit 处理，以及相应测试 |
| 数据来源 | Databricks SQL MCP 只读；状态与备注只写本机 SQLite |

推荐顺序：先决条件 → 获取代码与依赖 → 快速开始 → 配置 Databricks MCP → 运行与调试 → Spec Kit 跟练 → 验收。

> [!NOTE]
> 没有 Databricks 凭据时，仍可看 mockup、讨论新增需求、生成规格、安装依赖和进行离线检查；页面业务数据及保存后重读验收需要实际 MCP 连接。

## 学习目标

- [ ] 读懂“源数据只读、状态只写本机”的边界，并在页面上区分两者
- [ ] 实现 `save`：带原状态校验、输入校验、事务写入
- [ ] POST 成功后重新 GET 同一异常确认，失败或未确认时不能提示成功
- [ ] 让 `OPEN → IN_PROGRESS → RESOLVED` 的非法跳转被拒绝，且不改变原记录
- [ ] 用 Spec Kit 生成本次新增功能的规格、计划和任务，按实际结果验收

## 本项目文档怎么读

`docs/` 只保留两份：

- [data-source.md](docs/data-source.md)：Databricks MCP、三张业务表、关联字段及数据使用规则。
- [prompts.md](docs/prompts.md)：一条可复制的新增功能需求，后续操作按第 6 节推进。

环境配置、启动、调试和验收均看本 README。功能规格、计划和任务以本项目 `specs/` 中的实际产物为准。

## 目录

| 章节 | 内容 | 用时 |
|---|---|---|
| [1. 先决条件](#1-先决条件) | 工具、账号与网络 | 首次约 10 分钟 |
| [2. 获取代码与依赖](#2-获取代码与依赖) | 克隆、`uv sync`、增量起点检查 | 约 10 分钟 |
| [3. 快速开始](#3-快速开始) | 确认起始状态正常 | 约 2 分钟 |
| [4. 配置 Databricks MCP](#4-配置-databricks-mcp) | 数据权限、凭据、Copilot 验证 | 约 10 分钟 |
| [5. 运行与调试](#5-运行与调试) | 终端、`start.ps1`、F5 断点、本地库 | 约 2 分钟 |
| [6. Spec Kit 跟练](#6-spec-kit-跟练) | 课堂四步与 `implement` 提示词 | 约 5 分钟 |
| [7. 验收](#7-验收) | 离线检查、状态流转、保存与确认 | 约 8 分钟 |
| [8. 故障排查](#8-故障排查) | 常见现象与处理 | 按需 |
| [9. 目录结构与参考](#9-目录结构与参考) | 文件导航与官方链接 | 参考 |

## 1. 先决条件

本文使用 **Windows + PowerShell**。仓库中的 Spec Kit 包装脚本为 `.ps1`，建议在 VS Code 的 PowerShell 终端操作。macOS/Linux 可运行 Python 应用，但本文不提供对应的完整课堂脚本。

| 准备项 | 要求及用途 |
|---|---|
| [Git](https://git-scm.com/downloads) | 克隆仓库、查看改动、提交 PR |
| [VS Code](https://code.visualstudio.com/) | 单独打开当前案例目录，登录有 Copilot 使用权限的 GitHub 账号，确认 Agent 聊天可用；按 IDE 提示启用 GitHub Copilot |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | 管理 Python 3.12 和本案例目录独立的 `.venv`，按 `uv.lock` 安装依赖 |
| [Node.js 22](https://nodejs.org/en/download) | 执行前端 JavaScript 语法检查；应用前端不需要 `npm install` |
| Databricks 账号及网络 | 能访问讲师指定工作区、SQL MCP 和培训表；具备对应 SQL Warehouse 使用权限 |
| 网络下载条件 | 首次准备需要下载 Python、PyPI 依赖和固定版本的 Spec Kit CLI；请在课前完成 |

安装工具后重新打开 PowerShell，确认命令可用：

```powershell
git --version
uv --version
node --version
```

> [!NOTE]
> Python 由下一步的 uv 安装，无需先配全局 Python、激活虚拟环境或单独安装 pip。无需 Docker、前端构建服务或本机 Databricks。Copilot Agent、MCP 和 Skills 还需组织策略允许使用；只登录 GitHub 不代表这些能力均已开放。

## 2. 获取代码与依赖

下方命令使用本课程的公开仓库；使用 ZIP 时直接进入解压后的本案例目录，跳过 clone 和 cd。不要在工作坊根目录执行依赖安装。

```powershell
$GitHubOwner = 'NovaTech-SG'
git clone "https://github.com/$GitHubOwner/github-copilot-logistics-workshop.git"
cd github-copilot-logistics-workshop/copilot-shipment-tracker-starter

uv python install 3.12
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
.\tools\speckit.ps1 integration status --json
```

| 命令 | 预期输出 |
|---|---|
| `bootstrap_training.py` | 未生成规格时 `awaiting_specification`；有有效活动规格时 `preserved` |
| `check_training.py` | `ready`，初始 `stage: requirements` |
| `speckit.ps1 integration status --json` | `status: ok`，无缺失或被改写的官方文件 |

这三项都**不验证** MCP 连接或页面业务。

> [!NOTE]
> 仓库已预装 **官方 Spec Kit 1.3.2** 的 Copilot Skills 和模板。`.\tools\speckit.ps1` 通过 uv 调用固定 CLI，首次可能需要下载；不用额外安装全局 `specify`，也不要重新执行 `specify init --force`。

初始 `specs/` 只有 `.gitkeep`，没有预置规格和活动指针。bootstrap 不生成或恢复旧规格；课堂 specify 创建新功能目录与 `.specify/feature.json`。示例名称为 `specs/001-exception-followup`，已有有效选择会保留。`uv sync --locked` 生成本案例目录自己的 `.venv`；后续命令都在本案例目录内运行。

## 3. 快速开始

先在浏览器直接打开 [新增功能效果稿](mockup/index.html)，对照已有队列理解保存后的目标状态。它不需要服务或凭据，也不会执行真实查询或保存。

前提：已完成第 1、2 节。以下命令都在本案例目录内执行。

**1）提供凭据**（最小集，来源说明见 [4.2](#42-提供凭据)）

```powershell
$env:DATABRICKS_HOST     = 'https://你的工作区.azuredatabricks.net'
$env:DATABRICKS_HOSTNAME = '你的工作区.azuredatabricks.net'
$env:DATABRICKS_TOKEN    = 'dapi...'
$env:DATABRICKS_CATALOG  = 'dev_databricks'
$env:DATABRICKS_SCHEMA   = 'default'
```

**2）验证查询**——会合并源异常与本机记录，约 10～30 秒

```powershell
uv run --locked python app.py --check
```

空本地库时应输出 `exception_count 169`，`counts` 为 `OPEN 40 / IN_PROGRESS 69 / RESOLVED 60`。

**3）启动页面**

```powershell
uv run --locked python app.py
```

打开 <http://127.0.0.1:8769>，应能读取异常列表、搜索筛选、查看详情。

> [!IMPORTANT]
> 点击保存会显示“课堂练习：请完成……”，后端保存接口返回 **501**。这是起始检查点的正常表现，实现 P1 前不要期待记录被保存。

> [!TIP]
> 想少敲命令就用 F5 打断点运行，见 [5.2](#52-在-vs-code-中运行或调试)。

## 4. 配置 Databricks MCP

### 4.1 确认培训数据与权限

从讲师处获取工作区 Host、Catalog、Schema、已授权的访问方式及可用的 SQL MCP 地址。**克隆本案例目录不会创建 Databricks 表，也不附带讲师 Token 或共享账号。** 表名与字段约定见当前功能的 `spec.md`、`data-model.md` 和 `contracts/api.md`。

| 表 | 原始培训快照行数 |
|---|---:|
| `shipments` | 500 |
| `carriers` | 4 |
| `exceptions` | 169 |

表须为讲师已准备好的业务类型表，不使用 `*_raw` 表。若使用别的数据集，下文的固定验收数值不再适用。身份需具备对应 Catalog/Schema 使用权、表的读取权限以及可用的查询计算权限，由讲师或管理员分配。

本课使用 `/api/2.0/mcp/sql` 工作区端点，以及 `execute_sql_read_only`、`poll_sql_result` 工具。若工作区允许 PAT，可在个人设置的 Developer → Access tokens 生成短期令牌，选择 Other APIs 下的 `sql` 作用域，并以管理员要求为准。API 作用域不授予表权限，也不等于强制只读。应用仅调用只读工具，课堂身份也应限制为所需的读取权限。

Databricks 另有 Unity Gateway 的 `system.ai.dbsql` 入口；它的启用条件、权限和工具契约需另外核对。不要仅替换 URL 就假定与当前代码兼容。工作区只有其他入口或仅允许交互式 OAuth 时，先由讲师确认课程适配方式；当前 Python 应用不会自动完成浏览器 OAuth 登录或刷新令牌。

### 4.2 提供凭据

凭据有两个消费者，读取来源不同：

| 消费者 | 读取方式 |
|---|---|
| Python 应用（终端运行、F5 调试） | 进程环境变量；F5 时由 `.env` 注入 |
| `.vscode/mcp.json`（Copilot 的 MCP 连接） | VS Code 进程环境里的 `${env:...}` |

两个 Host 变量名不同是有原因的：Python 应用需要完整的 `https://...` 地址；而 `mcp.json` 的 `url` 必须以**字面** `https://` 开头，完整地址放进变量会触发“URL 必须以 http:// 或 https:// 开头”的提示。所以只把域名放进 `DATABRICKS_HOSTNAME`。都不带 `/?o=...` 或末尾 `/`。

#### 方式 A：终端环境变量（推荐）

请在 VS Code 之外单独打开 Windows PowerShell，进入当前案例目录，在**这个窗口**设置并启动；不要使用随后要关闭的 VS Code 集成终端：

```powershell
$env:DATABRICKS_HOST = 'https://你的工作区.azuredatabricks.net'
$env:DATABRICKS_HOSTNAME = '你的工作区.azuredatabricks.net'
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

`DATABRICKS_MCP_URL` 可选，用于覆盖应用默认拼接的端点。Catalog/Schema 换成培训实际位置。隐藏输入避免 Token 出现在命令文本中。不要把凭据写入 README、聊天、前端或 Git。

环境变量只对当前终端及其后启动的子进程生效。Python 命令可以直接在本窗口运行；如需 VS Code 继承这些变量，**完全退出**已有 VS Code 进程，再从此窗口打开仓库：

```powershell
code --new-window .
```

> [!WARNING]
> 重新从桌面打开的 VS Code 不会继承另一个 PowerShell 窗口的临时变量；关闭本窗口后再次操作需要重新设置。这是 MCP 显示“无法启动”最常见的原因。

#### 方式 B：用 `.env` 管 F5 调试

不想每次启动都依赖终端变量时，复制模板并填自己的值：

```powershell
Copy-Item .env.example .env
```

`.env` 已被 `.gitignore` 忽略，只在 F5 时通过 `envFile` 注入；应用进程本身不读它。注意两点：

- `DATABRICKS_TOKEN=` 留空会**覆盖**终端里的同名变量。不用就填值，或把整行注释掉。
- `.env` 不会让 Copilot 的 MCP 生效。`DATABRICKS_HOSTNAME` 仍必须在 VS Code 进程环境里。

#### Copilot 侧的 MCP 配置

上面两种方式只解决 Python 应用怎么拿到凭据。Copilot 的连接由 `.vscode/mcp.json` 决定，与选哪种方式无关，仓库已提供且无需填入实际 Token：

```json
{
  "servers": {
    "databricksTraining": {
      "type": "http",
      "url": "https://${env:DATABRICKS_HOSTNAME}/api/2.0/mcp/sql",
      "headers": {
        "Authorization": "Bearer ${env:DATABRICKS_TOKEN}"
      }
    }
  }
}
```

> [!NOTE]
> 新版 VS Code 可能区分 Copilot 与 Local harness，以及 Global、用户和工作区配置。此仓库使用 `.vscode/mcp.json` 的 `servers` 格式；请在能读取该配置的 Local 会话中操作。如果 IDE 提示迁移配置，按[官方配置说明](https://code.visualstudio.com/docs/agent-customization/mcp-servers)选择对应会话和配置位置，再验证工具调用；不要仅因文件存在就认为 MCP 可用。

### 4.3 在 Copilot 中验证工具和表读取

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

展开聊天中的工具调用，确认执行的是该 MCP 的工具，且返回的实际计数与 [4.1](#41-确认培训数据与权限) 一致。“Discovered tools”只说明发现了工具，浏览器登录也不代替应用的 Bearer Token。“浏览资源”灰色不影响仅提供 tools 的服务。

### 4.4 复用已有 MCP 配置

如果你已在自己的 VS Code 配置中验证过 `databricksTraining`，可复用它，不必再配一份。Python 默认**不自动读取** VS Code 配置；使用 `--vscode-config` 才会读取：

```powershell
# Windows 普通 VS Code 用户配置的默认位置
uv run --locked python app.py --vscode-config --check
uv run --locked python app.py --vscode-config

# 如果使用工作区配置、其他 Profile 或其他配置位置，显式传入文件路径
uv run --locked python app.py --vscode-config .vscode/mcp.json --check
```

省略路径时，默认文件为 `%APPDATA%/Code/User/mcp.json`，不是工作区文件或 Copilot Global 配置。其他路径需自己指定；支持 JSON/JSONC，以及 `servers` 或 `mcpServers` 下名为 `databricksTraining` 的配置，认证头须为 `Bearer ...`。

Python 可展开 `${env:变量名}`，**不能读取 VS Code 的 `${input:...}` 或 IDE 中缓存的 OAuth 登录状态**。遇到这两种配置，按 [4.2](#42-提供凭据) 为应用单独提供环境变量；不要把实际 Token 贴到配置里。`DATABRICKS_CATALOG` 和 `DATABRICKS_SCHEMA` 始终由应用进程的环境变量设置，与 MCP 配置文件分开。

> [!IMPORTANT]
> **两条连接分别验证：** Copilot → MCP 用于开发时了解数据；浏览器 → 本地 Python → MCP 用于应用运行。前者成功不代表后者已配置好。页面必须读取运行时查询结果，不能把 Copilot 聊天返回值写死在代码中。

## 5. 运行与调试

### 5.1 终端启动

完成 [4.2](#42-提供凭据) 后，在**同一个 PowerShell 窗口**执行：

```powershell
uv run --locked python app.py --check
uv run --locked python app.py
```

第一条成功后再执行第二条；服务运行时终端会保持占用。打开 <http://127.0.0.1:8769>，保持终端开启；修改 Python 后 `Ctrl+C` 停止并重新启动，修改静态页面后刷新浏览器。

`--check` 会查询源异常并合并本地跟进记录，输出 `exception_count`、`counts` 和来源。首次使用空本地库时，培训快照为 169 条，OPEN 40、IN_PROGRESS 69、RESOLVED 60；保存过本机记录后，合并状态分布会改变。该检查不执行保存操作。

页面应能读取异常列表、搜索筛选并查看详情。点击保存显示“课堂练习：请完成……”是起始状态；后端保存接口直接调用时返回 501。实现后再进行 [7.2](#72-实际业务验收) 的持久化验收。

**保存位置：** 源数据始终从 MCP 读取；状态与备注只存到本案例目录 `data/followups.sqlite3`，不会回写 Databricks。不同异常按 `exception_id` 区分，同一运输单的多条异常互不覆盖。该应用不是多人共享的云端工单系统。

想开新一轮练习而不影响已有记录，可指定新文件；验证重启恢复时必须使用同一个文件：

```powershell
uv run --locked python app.py --db data/practice-02.sqlite3
```

新练习首次请选择尚不存在的文件名，不要删除旧库。源查询最多返回 500 条异常；超限或截断会报错，不展示不完整列表。

### 5.2 在 VS Code 中运行或调试

仓库带了 `.vscode/launch.json`，可以不开终端直接按 F5。先按 [4.2 方式 B](#方式-b用-env-管-f5-调试) 准备好 `.env`。

| 配置 | 行为 |
|---|---|
| 异常跟进：启动网页（读 .env，127.0.0.1:8769） | 常驻服务，F5 后打开 <http://127.0.0.1:8769> |
| 异常跟进：检查数据（读 .env，--check） | 查一次、打印异常单量与状态分布、退出 |
| 异常跟进：启动网页（提示输入 Host + Token） | 没有 `.env` 时的兜底，弹框输入 |

在行号左侧点一下即可打断点。实现 P1 时建议在 `services/store.py` 的 `save` 与 `static/app.js` 的 submit 流程各停一次：先确认原状态校验，再看写入与重读。请求进入后停在断点上，**浏览器会一直转圈**（该请求线程被挂起），按 F5 继续才返回。改完 Python 代码要 `Shift+F5` 停止再启动，没有热重载。

本地库默认写到 `data/followups.sqlite3`；调试不同练习库时，在 `args` 里加 `"--db", "data/practice-02.sqlite3"`。

> [!WARNING]
> 编辑器右上角的 ▷「Run Python File」**不走** `launch.json`，拿不到环境变量，会报 URL 或 Token 相关错误。请用 F5，或在左侧「运行和调试」面板选择上面的配置。

### 5.3 三种入口对照

选一个即可，不要混用凭据来源：

| 入口 | 凭据来源 | 适用场景 |
|---|---|---|
| `uv run --locked python app.py` | 当前终端的环境变量 | 命令行操作、排查配置路径 |
| `.\start.ps1` | 自动同步依赖；缺 Token 时隐藏输入，或加 `-UseVSCodeConfig` 复用默认用户配置 | 干净的一键启动 |
| F5（`.vscode/launch.json`） | `.env`，或弹框输入 | 需要打断点调试 |

[4.4](#44-复用已有-mcp-配置) 的显式 `--vscode-config` 命令更适合核对配置路径与来源。

## 6. Spec Kit 跟练

先看 [数据来源与表关系](docs/data-source.md)、[新增功能效果稿](mockup/index.html) 和 [一句话需求](docs/prompts.md)。这次是在已有队列上新增本机保存，不重写应用。

| 步骤 | Copilot Agent 聊天操作 | 本步核对 |
|---|---|---|
| 1 | `/speckit-specify` | 从新增需求与 mockup 生成 spec，明确已有与新增范围 |
| 2 | 必要时 `/speckit-clarify` | 状态、备注、原状态过期与重读确认 |
| 3 | `/speckit-plan` | 复用读取基础，确定保存与前端确认方案 |
| 4 | `/speckit-tasks`、`/speckit-analyze` | 任务依赖、必要测试和一致性 |
| 5 | `/speckit-implement 只实现后端保存与必要测试` | 后端 save、校验与事务保存 |
| 6 | `/speckit-implement 只实现前端提交与确认` | 前端 POST 后 GET 核对与反馈 |
| 7 | `/speckit-converge` | 保存、恢复和失败场景，确认已有功能无回归 |

命令逐条发到聊天，每步审阅后再继续。初始没有 spec/plan/tasks；功能目录和活动指针由官方 specify 技能创建，后续以实际生成的任务 ID 为准。

**课堂 15 分钟范围不变：** 补 `FollowUpStore.save`、前端 submit 和相应测试。复用已有查询、列表、详情、校验和 SQLite 结构；源只读、跟进只写本机。mockup 不参与实际查询或保存。

## 7. 验收

### 7.1 离线检查

不需要 Databricks 凭据：

```powershell
uv run --locked python -m unittest discover -s tests -v
node --check static/app.js
```

起始版包含 3 项规则与查询输入检查，以及 10 项空规格和阶段推进检查。它们不证明保存功能已完成；实施新增功能时再补保存、重读、非法输入和失败不写入等测试。

### 7.2 实际业务验收

需要 MCP 和培训快照：

1. 在空本地练习库下读取列表，确认 169 条及初始分布 40 / 69 / 60。
2. 选择一条 OPEN 异常，记下 `exception_id`，改为 IN_PROGRESS，填写非空备注并保存。
3. 确认页面提示“已保存到本机，并重新读取确认”，重新打开相同编号核对状态与备注；源状态仍单独显示。
4. 刷新页面，再 `Ctrl+C` 停服务，用**相同 `--db` 文件路径**重启，确认记录保留。跟进状态变化后概览不应继续固定为初始分布。
5. 验证空白/超长备注、跳过或退回状态、过期原状态会被拒绝，失败不改变原记录；另一条异常不受影响。

> [!IMPORTANT]
> 教学规则：`OPEN → IN_PROGRESS → RESOLVED`，可在同状态更新备注；去掉首尾空格后备注必填、最多 1000 字。它们是本练习的规则，不是 Nike 生产流程定义。

> [!WARNING]
> 起始版在第 2 步会提示保存练习未完成；先完成 Spec Kit P1 实现再继续验收，**不要**通过修改界面提示来绕过保存。

按上面的清单核对，在本次课堂笔记或 PR 说明中记录实际执行、结果和未验证项。详细场景以本次生成并确认的 spec 为准。`ready`、离线测试通过、MCP 成功和页面验收是不同证据，分别记录。

### 7.3 检查新增功能的当前阶段

```powershell
uv run --locked python tools/check_training.py
```

检查识别 `requirements → specified → planned → tasks-generated`，允许空规格及中间阶段，不会生成文档或覆盖已有选择。它不证明保存已通过，也不要求在业务完成后手工改 checkpoint 或保留旧 TODO。

实现后仍需分别核对离线测试、实际 MCP、页面保存和同库重启恢复。

### 7.4 PR 与 CI

完成跟练后先 `git diff -- .` 审查改动、凭据和业务范围，再按讲师安排提交分支与 PR。工作坊根目录的 [CI](../.github/workflows/ci.yml) 在 push/PR 时检查当前课堂阶段、运行离线测试及 JavaScript 语法检查，不生成或恢复旧规格。它不使用 Databricks Token、不查询现场数据、不部署服务器；绿色 CI 不能代替真实 MCP 和浏览器验收。

## 8. 故障排查

| 现象 | 处理方法 |
|---|---|
| `uv`、`git`、`node` 找不到 | 安装后重开终端，检查 PATH；Python 用 `uv run`，不用系统 `python` 代替 |
| uv 下载失败或证书错误 | 检查公司代理、PyPI 与 Python 下载访问；按组织证书方案配置，不关闭 TLS 验证 |
| PowerShell 拒绝 `.ps1` | 若是 ZIP 解压文件，检查文件阻止属性；按公司批准的脚本执行策略处理，受管电脑请联系 IT。Python 的 bootstrap/check 命令可先单独执行 |
| `feature.json` 不存在 | 初始正常，课堂 specify 后由技能创建；若已有 spec，则核对活动选择，不覆盖学员成果 |
| `check_training.py` 不通过 | 核对当前阶段的 spec、plan、tasks 与活动指针，按 [7.3](#73-检查新增功能的当前阶段) 检查；不需要手工改 checkpoint |
| 保存按钮提示“课堂练习：请完成……” / 保存 API 501 | 起始版的预期状态，实现 `FollowUpStore.save` 与前端 submit 后才可用 |
| `/speckit-*` 不显示 | 确认只打开本案例目录、当前会话支持 `.github/skills`、Copilot 可用且组织允许；重载窗口并检查 IDE 的技能发现能力。不要重跑 init 覆盖材料 |
| 缺少 Token 或提示未展开变量 | 应用本身不读 `.env`：终端启动看环境变量，F5 由 `.vscode/launch.json` 的 `envFile` 注入。`${input:...}` 只能由 IDE 展开，Python 不支持 |
| F5 报“尚未提供 Databricks Token” | `.env` 里 `DATABRICKS_TOKEN=` 是**空值**，会覆盖终端里的同名变量；要么填入 Token，要么把该行注释掉后从终端继承 |
| `databricksTraining` 无法启动或显示灰点 | 工作区需已信任；VS Code 必须从设好 `DATABRICKS_HOSTNAME` 的终端启动；MCP 服务器不会自动运行，需手动 Start，首次还要确认信任提示 |
| `mcp.json` 里 `url` 提示“必须以 http:// 或 https:// 开头” | 该字段要求以**字面** `https://` 开头，所以只把域名放进 `DATABRICKS_HOSTNAME`，不要放完整地址 |
| MCP 返回 401/403 | 检查 Token 过期、工作区、`sql` 作用域、MCP 开放条件与表/计算权限；能列工具不等于能读表 |
| 弹出 OAuth 客户端注册或 `invalid_request` | 说明当前会话走了交互式 OAuth；它与本文 Bearer Token 路径不同。请讲师核对所选配置和组织认证方式，不把 PAT 填到 OAuth client ID |
| service 不存在或无权访问 | 确认完整 MCP 地址，勿混用 `/api/2.0/mcp/sql` 与 `system.ai.dbsql`；按实际服务检查启用条件及权限 |
| Copilot 能查，Python 查不到 | 区分 IDE 登录缓存与应用凭据，核对默认/显式配置路径、环境变量是否继承；IDE 工具无需常驻来代理 Python 请求 |
| 查不到表、字段类型错误或数值不符 | 核对 Catalog/Schema、业务类型表与培训快照；不要改成 `_raw` 表或用固定值掩盖查询问题 |
| 状态分布与预期 40 / 69 / 60 不符 | 本机库已有记录时会合并显示；换 `--db` 新文件再看初始分布，不要删旧库 |
| 保存后重读不一致或丢失 | 检查是否用了不同 `--db` 路径；保存必须走服务端重新读取，失败时不能显示成功 |
| 端口已占用 | `Ctrl+C` 停止自己启动的旧进程，或用 `uv run --locked python app.py --port 8877` 并打开对应地址 |
| 页面一直加载、502 或结果被截断 | 查看应用终端及 MCP 实际错误；检查网络、查询计算与结果完整性。修复后重试，不以固定数据兜底 |

排查时可提供脱敏后的错误类型、表名和执行步骤；不要发送 Token 或完整的个人配置文件。

## 9. 目录结构与参考

| 路径 | 用途 |
|---|---|
| `app.py` / `start.ps1` | 本地服务、命令行参数与启动脚本 |
| `.vscode/mcp.json` | MCP 服务器配置；`url` 只放域名变量，避免 schema 误报 |
| `.vscode/launch.json` | F5 调试配置；通过 `envFile` 读取 `.env` |
| `.env.example` | 本地凭据模板，复制为 `.env` 后填写；`.env` 不提交 |
| `services/settings.py` | 环境变量和显式 MCP 配置读取 |
| `services/mcp_sql.py` | 只读查询、轮询与结果解析 |
| `services/queries.py` | 业务 SQL |
| `services/tracker.py` | 业务调用与状态校验（已提供） |
| `services/store.py` | 本地 SQLite 持久化（**`save` 待实现**） |
| `static/` | 原生 HTML/CSS/JavaScript（**submit 待实现**） |
| `specs/` | 初始只有 `.gitkeep`，课堂生成新增功能规格、计划和任务 |
| `mockup/` | 只展示新增保存与确认目标的静态效果稿 |
| `data/followups.sqlite3` | 本机跟进记录，不提交 |
| `tools/bootstrap_training.py` / `tools/check_training.py` | 首次克隆准备与课堂结构检查 |

各案例独立安装依赖、运行与保存练习结果。`.venv`、实际凭据、`data/` 与本机活动指针不提交到 Git。第三方 Spec Kit 材料的来源和许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

官方参考（2026-11-09 核对；本课固定 Spec Kit 1.3.2，IDE 界面可能随版本调整）：

- [uv 安装](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code MCP 配置与首次工具验证](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [Spec Kit 的 Copilot Skills 集成](https://github.github.io/spec-kit/integrations/copilot.html)
- [Databricks 工作区 MCP 端点与 Unity Gateway 的区别](https://learn.microsoft.com/en-us/azure/databricks/agents/mcp-tools/built-in-mcp-services)
- [Databricks PAT 与作用域](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth/pat)
