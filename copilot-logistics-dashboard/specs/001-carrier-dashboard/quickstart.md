# Dashboard 运行与验收

## 准备

在当前项目目录按 [README](../../README.md) 完成依赖安装和个人凭据配置。终端运行读取进程环境变量；F5 调试按 README 由 `.env` 注入。

```powershell
uv sync --locked --python 3.12
uv run --locked python tools/bootstrap_training.py
uv run --locked python tools/check_training.py
```

已有有效的活动功能选择会保留。只用 VS Code 打开当前应用目录。

## 检查连接与启动

```powershell
uv run --locked python app.py --check
uv run --locked python app.py
```

完成版 `--check` 的预期业务结果见本项目 README；查询需要个人授权与可用计算。 常驻服务启动后终端保持占用。

本目录是参考完成版，用于运行和结果对照。实际结果仍需在自己的环境中验证。

如需显式复用自己电脑的 VS Code MCP 配置，按 README 添加 `--vscode-config`。该方式不代替个人授权，也不要求客户取得讲师的配置文件。

## 验收

按 [业务规格](spec.md) 和 [验收规则](acceptance.md) 核对本次范围。离线检查按 README 执行，实际 MCP 查询与页面操作分别记录到 [验证记录](../../docs/validation.md)。

完整聊天步骤见 [Spec Kit 操作说明](../../docs/speckit.md) 和 [提示词](../../docs/prompts.md)。
