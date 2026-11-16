# Dashboard Cursor 迁移前对照版

用于 Session 2 的 Cursor → GitHub Copilot 迁移演示。业务代码、页面、业务规格与验收规则、Python 依赖和 Dashboard 完成版相同，主要对照 Agent 配置；本目录不承担从零编码跟练。

## 安装与运行

在 Cursor 中只打开本目录，执行：

```powershell
uv sync
```

确认 Cursor 已继承个人 Databricks 环境变量。在“运行和调试”中选择“Cursor 对照：启动网页”，按 F5，打开 <http://127.0.0.1:8770>。配置使用本项目 `.venv`，可在 Python 中设置断点；修改后停止并重新启动。

`.env` 可供 F5 注入个人配置，不能代替 Cursor Agent 的 MCP 配置。Agent 使用 `.cursor/mcp.json`，Python 应用使用自己的环境变量，两条连接分别核对。

首次配置 Cursor Agent 的 MCP 时，将示例复制为本地配置：

```powershell
Copy-Item .cursor/mcp.example.json .cursor/mcp.json
```

示例通过 `DATABRICKS_HOST` 和 `DATABRICKS_TOKEN` 环境变量连接；本地 `.cursor/mcp.json` 已加入忽略列表，不提交。

命令行启动时指定对照端口：

```powershell
uv run python app.py --port 8770
```

## 与 Copilot 版本对照什么

| 内容 | 本目录：Cursor | Dashboard 完成版：Copilot |
|---|---|---|
| 全局项目约定 | `AGENTS.md`、`.cursor/rules/workshop.mdc` | `AGENTS.md`、`.github/copilot-instructions.md` |
| Python 路径规则 | `.cursor/rules/python.mdc`，`globs` | 迁移时新增 `.github/instructions/python.instructions.md`，使用 `applyTo` |
| Spec Kit Skills | `.cursor/skills/speckit-*/SKILL.md` | `.github/skills/speckit-*/SKILL.md` |
| 编辑器 MCP | `.cursor/mcp.json`，`mcpServers` | `.vscode/mcp.json`，`servers` |
| 调试启动 | `.vscode/launch.json`，端口 8770 | `.vscode/launch.json`，端口 8766 |
| 业务实现、规格、依赖 | 同一份教学基线 | 同一份教学基线 |

`AGENTS.md` 可在两边复用；不需要迁移 Python、SQL 或页面业务逻辑。每次只用对应编辑器打开一个项目目录，分别检查实际采用的规则、Skills 与工具结果。

## 课堂演示

1. 在 Cursor 查看两份 `.mdc`、Skills 和 MCP 配置，用 [只读提示词](docs/prompts.md)解释规则与调用路径。
2. 在 VS Code 打开 `copilot-logistics-dashboard`，使用同样的只读请求，对照指令文件、上下文和工具结果。
3. 核对两边读取同一 Databricks 培训表，全部范围参考 500 单、参与准时率计算 380 单、准时率 80.00%。结果以实际查询为准。
4. 完成迁移演示后，编码练习打开 `copilot-logistics-dashboard-starter`，从空规格开始。

本目录已装好官方 Spec Kit 1.3.2 的 Cursor Skills，无需重新 init。预置业务代码与规格供对照，不代表 Cursor 在课堂现场生成过这些文件。业务定义见 [data-source.md](docs/data-source.md) 和 `specs/001-carrier-dashboard/`。

## 按需检查

运行应用不需要 bootstrap。核对预置规格与工具时执行前两条；业务测试与语法检查使用后两条：

```powershell
uv run python tools/bootstrap_training.py
uv run python tools/check_training.py
uv run python -m unittest discover -s tests -v
node --check static/app.js
```

如需让 Python 显式读取 Cursor 的 MCP 文件，可执行 `uv run python app.py --vscode-config .cursor/mcp.json --port 8770`；参数名沿用原应用，支持 `mcpServers` 和环境变量占位符。

Token、`.env`、`.venv` 和实际 MCP 配置不提交，仓库仅提供 `.cursor/mcp.example.json`。`.specify/migration-baseline.json` 记录业务文件来源与哈希；工具检查会发现对照代码是否被改动。实际 Cursor 操作、实时 MCP、页面和 CI 结果分别记录。

参考：[Cursor Rules](https://cursor.com/docs/rules) · [Cursor Skills](https://cursor.com/docs/skills) · [Cursor MCP](https://cursor.com/docs/mcp) · [Spec Kit Cursor 集成](https://github.github.com/spec-kit/integrations/cursor-agent.html)
