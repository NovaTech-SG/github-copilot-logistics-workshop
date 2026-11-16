# Dashboard 运行与验收

## 准备

在当前项目目录按 [README](../../README.md) 完成依赖安装和个人凭据配置。终端运行读取进程环境变量；F5 调试按 README 由 `.env` 注入。

```powershell
uv sync
```

只用 Cursor 打开当前目录。F5 使用端口 8770；运行应用无需 bootstrap。核对预置规格和工具时再按 README 的“按需检查”执行。

## 检查连接与启动

```powershell
uv run --locked python app.py --check
uv run --locked python app.py --port 8770
```

完成版 `--check` 的预期业务结果见本项目 README；查询需要个人授权与可用计算。 常驻服务启动后终端保持占用。

本目录是参考完成版，用于运行和结果对照。实际结果仍需在自己的环境中验证。

如需显式复用本项目 Cursor MCP 配置，添加 `--vscode-config .cursor/mcp.json`。该方式仍需自己的环境变量和访问授权。

## 验收

按 [业务规格](spec.md) 和 [验收规则](acceptance.md) 核对本次范围。离线检查与实际 MCP、页面操作分别记录，步骤见 [README](../../README.md)。

迁移对照的课堂步骤见 [README](../../README.md)，只读请求见 [提示词](../../docs/prompts.md)。
