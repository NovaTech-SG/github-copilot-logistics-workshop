# GitHub Copilot 物流应用实操工作坊

Nike GC Logistics · Session 2 · 90 分钟

[![Workshop CI](https://github.com/NovaTech-SG/github-copilot-logistics-workshop/actions/workflows/ci.yml/badge.svg)](https://github.com/NovaTech-SG/github-copilot-logistics-workshop/actions/workflows/ci.yml)

本仓库包含学员起始项目、参考完成版、培训模拟 CSV 和跟练文档。通过 SDD / Spec Kit、项目指令和 Databricks MCP，完成 Dashboard 与运输异常跟进两个本地应用。

> [!NOTE]
> 全部业务数据为培训模拟数据，不代表 Nike 实际运营情况。仓库不包含实际 Token，也不自动创建 Databricks 培训表。

## 客户资料与下载

客户版 Word 直接保存在仓库根目录，随代码一起克隆或下载 ZIP 即可取得，也可以从下面的链接单独下载。

| 资料 | 用途 | 获取方式 |
|---|---|---|
| Session 2 培训大纲 | 了解培训对象、90 分钟安排、两个案例和课前准备 | [下载 Word](<Nike GC Logistics Session 2 培训大纲.docx?raw=true>) |
| Databricks 三张表业务表说明 | 理解三张表的业务对象、主要字段和关联，通过简化示例与只读查询完成练习 | [下载 Word](<Databricks 三张表业务表说明.docx?raw=true>) |
| Databricks 培训模拟数据 | 查看承运商、运输单和运输异常三份 CSV，理解源表或准备导入数据 | [文件说明与 CSV](data/README.md) |
| Dashboard 学员操作说明 | 安装依赖、配置 MCP、运行调试和完成第一个案例 | [在线阅读](copilot-logistics-dashboard-starter/README.md) |
| 异常跟进学员操作说明 | 运行第二个案例、保存状态与备注、重读核对 | [在线阅读](copilot-shipment-tracker-starter/README.md) |

建议先读培训大纲和三张表业务表说明，再进入选定学员项目的 README。学习笔记包含关系图、主要字段、状态与准时率说明，以及不附答案的查询练习。跟练时查该项目 `docs/prompts.md`；核对业务规则时查 `specs/` 下的 `spec.md` 和 `acceptance.md`。

Word 用于课程概览和数据理解；具体环境命令、功能范围和验收以当前项目 README 与活动规格为准。[data/](data/README.md) 中附有三份培训模拟 CSV，培训源表由讲师在 Databricks 中准备，个人授权由使用者自行配置。课程应用通过 Databricks MCP 读取源表。

三张表 Word 在仓库根目录统一维护，供客户下载。各应用的 `docs/data-source.md` 提供本项目内可读的数据来源与表关系，单独打开案例时，Copilot 先读这份说明。

## Markdown 文档阅读顺序

| 你现在要做什么 | 阅读位置 | 阅读重点 |
|---|---|---|
| 第一次开始 | 本页、选定学员项目的 `README.md` | 环境、个人授权、运行方式与当前练习起点 |
| 理解课堂步骤 | 当前项目的 `docs/prompts.md` | Dashboard starter 从需求与 mockup 生成规格；逐步推进本次范围 |
| 核对业务含义 | 当前功能的 `specs/`；Dashboard 初始先读 `docs/data-source.md`、`docs/prompts.md` 和 `mockup/` | 需求、数据字段、指标和状态规则；功能文档在课堂生成 |
| 理解实现方案 | 同一功能下的 `plan.md`、`tasks.md`、`research.md`、`contracts/api.md` | 技术选择、任务顺序和接口约定 |
| 验证自己的结果 | 当前项目 README 的验收章节 | 执行检查，在课堂笔记或 PR 中记录结果与未验证项 |
| 对照完成效果 | 两个参考完成版的 README | 运行和只读复盘；在 starter 中编码时不读取相邻完成版 |

`AGENTS.md`、`.github/copilot-instructions.md`、`.specify/memory/constitution.md` 是项目和 Agent 的规则。`.github/skills/`、`.specify/templates/` 是已配置的 Spec Kit 技能和模板；保留这些文件才能按文档继续跟练。`THIRD_PARTY_NOTICES.md` 保留第三方来源与许可。普通阅读先从上表开始，不需要逐一阅读所有工具文件。

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
| [copilot-logistics-dashboard-starter](copilot-logistics-dashboard-starter/README.md) | 从空规格、需求与 mockup 开始生成 Dashboard | 8767 |
| [copilot-logistics-dashboard](copilot-logistics-dashboard/README.md) | 结果参考：Dashboard 完成版 | 8766 |
| [copilot-shipment-tracker-starter](copilot-shipment-tracker-starter/README.md) | 学员跟练：异常保存与重读 | 8769 |
| [copilot-shipment-tracker](copilot-shipment-tracker/README.md) | 结果参考：异常跟进完成版 | 8768 |

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

课堂按案例 README 的 Spec Kit 流程推进。Dashboard starter 的 specs 初始为空，bootstrap 不生成规格；先看需求与静态效果稿，再通过 specify、plan、tasks 逐步形成学员产物。起始版的 TODO 和 501 提示是预期状态。

第二个案例切换到 `copilot-shipment-tracker-starter`，单独安装依赖并恢复活动功能。四个案例可使用同一工作区的培训表，但凭据由使用者自行配置；异常操作仅保存至各自本机 SQLite。

## 课堂路径

1. **环境与依赖**（课前完成）：装工具、克隆、`uv sync`、bootstrap 与课堂检查。
2. **Dashboard 案例**（课堂 15 分钟）：在起始版看 mockup、讨论需求，再逐步生成 spec/plan/tasks，并按本次 P1 范围实现查询、指标、筛选与对比图。
3. **异常跟进案例**（课堂 15 分钟）：在起始版补 `save` 与前端 submit，验证状态流转与保存后重读。
4. **复盘与验收**（其余时间）：只读解读 spec/plan/tasks，按各案例「验收」清单记录证据。

> [!IMPORTANT]
> 两个案例的 15 分钟范围只覆盖 P1。趋势、分页、扩展校验等属于 P2，完成版包含但课堂不要求照搬。

## 开始前的自查

在自己的电脑和账号下完成以下检查，再进入课堂跟练：

- Git、uv、Node.js 可用，VS Code 中的 Copilot Agent 已获授权。
- 只打开当前学员项目，按该项目 README 安装依赖并运行 bootstrap 与课堂结构检查。
- 在聊天斜杠菜单中确认本项目的 `/speckit-*` 技能可用。
- 用自己的 Databricks 授权分别验证 Copilot MCP 和 Python 应用；成功连接后继续核对培训表权限。
- 起始版的业务 TODO 和 501 提示是练习起点；实现后再按验收清单检查结果。

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
- [uv 安装](https://docs.astral.sh/uv/getting-started/installation/)
- [VS Code MCP 配置与首次工具验证](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
- [Spec Kit 的 Copilot Skills 集成](https://github.github.io/spec-kit/integrations/copilot.html)

第三方 Spec Kit 材料的来源与许可见各案例目录的 `THIRD_PARTY_NOTICES.md`。客户版 Word 保存在仓库根目录，可从本页的下载入口获取。
