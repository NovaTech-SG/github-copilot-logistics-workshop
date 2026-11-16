# Tracker 运行与验收

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

起始版 `--check` 只执行连接检查，不证明业务功能或培训表权限已经通过。 常驻服务启动后终端保持占用。

起始页可打开但业务 API 返回 501，表示课堂功能尚未实现。先完成 P1，再核对业务结果。

如需显式复用自己电脑的 VS Code MCP 配置，按 README 添加 `--vscode-config`。该方式不代替个人授权，也不要求客户取得讲师的配置文件。

异常跟进的状态与备注保存在本项目 SQLite。新一轮练习可指定一个尚不存在的 `--db` 路径；保留已有练习数据库。

## 验收

按 [业务规格](spec.md) 和 [验收规则](acceptance.md) 核对本次范围。离线检查按 README 执行，按 [README 验收](<../../README.md#7-验收>) 分别执行 MCP 查询与页面操作，并在课堂笔记或 PR 中记录结果。

完整聊天步骤见 [README 课堂步骤](<../../README.md#6-spec-kit-跟练>) 和 [提示词](../../docs/prompts.md)。
