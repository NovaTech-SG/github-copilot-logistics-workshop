# GitHub Copilot 物流应用实操工作坊

Nike GC Logistics · Session 2 · 90 分钟

本仓库包含学员起始项目、讲师完成版和跟练文档。业务数据全部为培训模拟数据。
通过 SDD / Spec Kit、项目指令和 Databricks MCP，完成 Dashboard 与运输异常跟进两个本地应用。

## 目录与使用对象

| 目录 | 用途 | 端口 |
|---|---|---:|
| [copilot-logistics-dashboard-starter](copilot-logistics-dashboard-starter/README.md) | 学员跟练：Dashboard | 8767 |
| [copilot-logistics-dashboard](copilot-logistics-dashboard/README.md) | 讲师展示：Dashboard 完成版 | 8766 |
| [copilot-shipment-tracker-starter](copilot-shipment-tracker-starter/README.md) | 学员跟练：异常保存与重读 | 8769 |
| [copilot-shipment-tracker](copilot-shipment-tracker/README.md) | 讲师展示：异常跟进完成版 | 8768 |

这是**一个 Git 仓库、四个独立应用目录**。每个案例有自己的依赖锁文件、环境、规格和指令。
克隆一次即可；依赖安装、MCP 配置、Spec Kit 和启动命令应在选定案例目录运行。

## 学员从这里开始

安装 Git、VS Code / Copilot、uv 和 Node.js 22，并准备个人获授权的 Databricks 访问方式。
克隆课程公开仓库后，先选择第一个学员项目：

```powershell
$GitHubOwner = 'YanZhiwei'
git clone "https://github.com/$GitHubOwner/github-copilot-logistics-workshop.git"
cd github-copilot-logistics-workshop/copilot-logistics-dashboard-starter
uv python install 3.12
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
```

接着按该目录 README 配置 MCP、验证工具与业务表，再启动页面。
准备好进程环境变量后，只用 VS Code 打开**当前案例目录**；不要同时把工作坊根目录和完成版加入学员工作区。
课堂按案例 README 的 Spec Kit 流程推进。起始版的 TODO 和 501 提示是预期状态。

第二个案例切换到 `copilot-shipment-tracker-starter`，单独安装依赖并恢复活动功能。
四个案例可使用同一工作区的培训表，但凭据由使用者自行配置；异常操作仅保存至各自本机 SQLite。
本仓库不自动创建 Databricks 培训表，也不包含实际 Token。

## 讲师准备

完成版用于展示和复盘，学员从两个 starter 目录跟练。
课前在实际授课电脑上验证 Copilot Skills、MCP、业务结果和页面交互。

## PR 与 CI

在仓库根目录创建分支和提交 PR；案例内的 `git diff -- .` 可查看当前案例改动。
根目录 [Workshop CI](.github/workflows/ci.yml) 分四个任务运行结构、离线和语法检查，
无 Databricks 凭据依赖，也不部署服务器。每个应用仍使用独立的 uv 环境，无根级 uv workspace。
starter 完成实现后，按其 README 更新课堂检查点，记录真实验收证据。

发布方法见 [GitHub发布说明](GitHub发布说明.md)。第三方 Spec Kit 许可声明保留在各案例目录。
