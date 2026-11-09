# 验证记录

## 备课接入
- Spec Kit 1.3.2官方CLI与Copilot skills已安装。
- 活动功能：specs/001-exception-followup；按官方解析器取得spec模板、运行setup-plan与setup-tasks。
- 功能文档按已确认培训要求准备，未声称在Copilot UI运行过全部命令。
- 业务TODO保留，起始项目不声明通过业务验收。

## 本次执行证据
运行后在此记录命令和结果，至少分开列出：
1. 规格/任务一致性与CLI元数据检查。
2. 应用离线测试与语法检查。
3. 实时MCP与页面操作（未执行时明确写未验证）。
4. 远程CI（本次未触发）。

## 2026-11-09 备课实际检查
- `tools/speckit.ps1 integration status --json`：status=ok，官方受管文件missing=0、modified=0。
- 官方`check-prerequisites.ps1 -Json -RequireSpec -RequireTasks -IncludeTasks`：活动功能与设计文件可解析。
- `uv run --locked python tools/check_training.py`：ready，规格、计划、任务和技能入口一致。
- `node --check static/app.js`：通过。
- `uv run --locked python -m unittest discover -s tests -v`：3项通过；仅验证预置规则和读取准备，保存TODO保留。
- 本轮未执行实时MCP、Copilot聊天技能、浏览器业务操作或远程CI；须在授课环境复核。
