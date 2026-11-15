# GitHub Copilot 物流应用实操工作坊

Nike GC Logistics · Session 2 · 90 分钟

[![Workshop CI](https://github.com/NovaTech-SG/github-copilot-logistics-workshop/actions/workflows/ci.yml/badge.svg)](https://github.com/NovaTech-SG/github-copilot-logistics-workshop/actions/workflows/ci.yml)

本仓库包含学员起始项目、讲师完成版和跟练文档。通过 SDD / Spec Kit、项目指令和 Databricks MCP，完成 Dashboard 与运输异常跟进两个本地应用。

> [!NOTE]
> 全部业务数据为培训模拟数据，不代表 Nike 实际运营情况。仓库不包含实际 Token，也不自动创建 Databricks 培训表。

## 概览

| 项 | 内容 |
|---|---|
| 课程 | GitHub Copilot Session 2 · Nike GC Logistics |
| 时长 | 90 分钟（课前准备约 30 分钟，另计） |
| 形式 | 讲师演示 + 学员跟练 + 只读复盘 |
| 案例 | 2 个应用 × 2 个版本（学员起始版、讲师完成版） |
| 技术栈 | Python 3.12、uv、原生 HTML/CSS/JavaScript、Spec Kit 1.3.2 |
| 数据来源 | Databricks SQL MCP，只读 `execute_sql_read_only` + `poll_sql_result` |
| 本地状态 | 异常跟进的状态与备注只写各自本机 SQLite |

## 你将构建

| 应用 | 做什么 | 端口 |
|---|---|---:|
| Dashboard | 从 MCP 拉取运输单，算准时率，支持承运商筛选、对比图、趋势与分页明细 | 8767 / 8766 |
| 异常跟进 | 读取运输异常，维护 `OPEN → IN_PROGRESS → RESOLVED` 跟进状态与备注，保存后重读确认 | 8769 / 8768 |

每个应用都有学员起始版（端口较大）和讲师完成版（端口较小），代码与规格完全独立。

## 学习目标

- [ ] 用 Spec Kit 把业务描述变成可执行的 `spec.md` → `plan.md` → `tasks.md` → 实现
- [ ] 通过 Databricks MCP 读取真实查询结果，并在应用里区分“源数据”与“本机记录”
- [ ] 识别 Agent 越界：读取相邻完成版、扩大范围、用固定值兜底
- [ ] 用离线检查、MCP 实测、页面验收三类证据区分“看起来完成”与“确实完成”
- [ ] 在起始检查点与完成状态之间正确切换，并如实记录未验证项

## 仓库结构

| 目录 | 用途 | 端口 |
|---|---|---:|
| [copilot-logistics-dashboard-starter](copilot-logistics-dashboard-starter/README.md) | 学员跟练：Dashboard | 8767 |
| [copilot-logistics-dashboard](copilot-logistics-dashboard/README.md) | 讲师展示：Dashboard 完成版 | 8766 |
| [copilot-shipment-tracker-starter](copilot-shipment-tracker-starter/README.md) | 学员跟练：异常保存与重读 | 8769 |
| [copilot-shipment-tracker](copilot-shipment-tracker/README.md) | 讲师展示：异常跟进完成版 | 8768 |

这是**一个 Git 仓库、四个独立应用目录**。每个案例有自己的依赖锁文件、环境、规格和指令。克隆一次即可；依赖安装、MCP 配置、Spec Kit 和启动命令都在选定案例目录内运行。

## 先决条件

| 准备项 | 要求 |
|---|---|
| Git | 克隆仓库、查看改动 |
| VS Code + GitHub Copilot | 能使用 Agent 聊天；组织策略允许 MCP 与 Skills |
| uv | 管理 Python 3.12 和各案例独立的 `.venv` |
| Node.js 22 | 前端 JavaScript 语法检查，无需 `npm install` |
| Databricks 访问 | 讲师指定工作区、SQL MCP、培训表，以及 `sql` 作用域的凭据 |

```powershell
git --version
uv --version
node --version
```

> [!TIP]
> 各案例 README 的「1. 先决条件」有更完整的检查清单与组织策略说明。

## 从这里开始

装好工具、拿到个人的 Databricks 访问方式后，克隆课程公开仓库并先选第一个学员项目：

```powershell
$GitHubOwner = 'NovaTech-SG'
git clone "https://github.com/$GitHubOwner/github-copilot-logistics-workshop.git"
cd github-copilot-logistics-workshop/copilot-logistics-dashboard-starter

uv python install 3.12
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
```

接着按该目录 README 配置 MCP、验证工具与业务表，再启动页面。准备好进程环境变量后，只用 VS Code 打开**当前案例目录**；不要同时把工作坊根目录和完成版加入学员工作区。

课堂按案例 README 的 Spec Kit 流程推进。起始版的 TODO 和 501 提示是预期状态。

第二个案例切换到 `copilot-shipment-tracker-starter`，单独安装依赖并恢复活动功能。四个案例可使用同一工作区的培训表，但凭据由使用者自行配置；异常操作仅保存至各自本机 SQLite。

## 课堂路径

1. **环境与依赖**（课前完成）：装工具、克隆、`uv sync`、bootstrap 与课堂检查。
2. **Dashboard 案例**（课堂 15 分钟）：先看完成版效果，再在起始版按 P1 范围实现查询、指标、筛选与对比图。
3. **异常跟进案例**（课堂 15 分钟）：在起始版补 `save` 与前端 submit，验证状态流转与保存后重读。
4. **复盘与验收**（其余时间）：只读解读 spec/plan/tasks，按各案例「验收」清单记录证据。

> [!IMPORTANT]
> 两个案例的 15 分钟范围只覆盖 P1。趋势、分页、扩展校验等属于 P2，完成版包含但课堂不要求照搬。

## 讲师准备

完成版用于展示和复盘，学员从两个 starter 目录跟练。课前在实际授课电脑上验证：

- [ ] Copilot Skills 能被发现（`/` 能看到 `/speckit-*`）
- [ ] `databricksTraining` 能启动并返回 3 个工具
- [ ] 两个完成版的 `--check` 数值与文档一致
- [ ] 页面筛选、保存、重读与重启恢复正常
- [ ] 起始版的 501 / “课堂练习：请完成……”提示符合预期

## 故障排查

| 现象 | 处理方法 |
|---|---|
| `uv`、`git`、`node` 找不到 | 安装后重开终端检查 PATH；Python 用 `uv run`，不用系统 `python` |
| MCP 服务器无法启动或显示灰点 | 工作区需已信任；VS Code 必须从设好 `DATABRICKS_HOSTNAME` 的终端启动；服务器需手动 Start |
| 页面能开但数据接口报错 | 检查应用所在终端的环境变量与 Token；IDE 里的 Copilot 连接不代替应用凭据 |
| 起始版页面提示未实现或 501 | 起始检查点的预期状态，实现 P1 后消失 |

各案例 README 的「故障排查」章节有完整清单（Token、OAuth、表权限、端口占用、结果截断等）。

## PR 与 CI

在仓库根目录创建分支和提交 PR；案例内的 `git diff -- .` 可查看当前案例改动。

根目录 [Workshop CI](.github/workflows/ci.yml) 用矩阵对四个项目分别运行结构、离线和语法检查，无 Databricks 凭据依赖，也不部署服务器。每个应用仍使用独立的 uv 环境，无根级 uv workspace。

starter 完成实现后，按其 README 更新课堂检查点，记录真实验收证据。

## 参考

- 案例文档：[Dashboard 完成版](copilot-logistics-dashboard/README.md) · [Dashboard 学员版](copilot-logistics-dashboard-starter/README.md) · [异常跟进完成版](copilot-shipment-tracker/README.md) · [异常跟进学员版](copilot-shipment-tracker-starter/README.md)
- 仓库维护与发布：[GitHub发布说明](GitHub发布说明.md)
- [uv 安装](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code MCP 配置与首次工具验证](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [Spec Kit 的 Copilot Skills 集成](https://github.github.io/spec-kit/integrations/copilot.html)

第三方 Spec Kit 材料的来源与许可见各案例目录的 `THIRD_PARTY_NOTICES.md`。PPT 在仓库外单独保存。
