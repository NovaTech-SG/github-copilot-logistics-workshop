# 物流承运商Dashboard 运行与验收

GitHub克隆后先执行`uv run --locked python tools/bootstrap_training.py`恢复默认活动功能，再运行课堂检查。已有有效功能选择会保留。


在本项目目录，先运行 `uv sync --locked`。
```powershell
.\tools\speckit.ps1 version
.\tools\speckit.ps1 integration status --json
uv run --locked python tools/check_training.py
uv run --locked python app.py --vscode-config --check
uv run --locked python app.py --vscode-config
```
本目录是完成版，仅用于效果与规格对照。

实现后按spec.md和acceptance.md做业务验收；离线测试使用unittest和node --check static/app.js。
实时凭据由每位使用者在本机配置，不随材料分发。详细步骤见[Spec Kit课堂操作](../../docs/speckit.md)。
