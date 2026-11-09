# Spec Kit 学员操作说明

GitHub克隆后先执行`uv run --locked python tools/bootstrap_training.py`恢复默认活动功能，再运行课堂检查。已有有效功能选择会保留。


## 当前材料是什么
本项目已通过官方`specify-cli==1.3.2`初始化Copilot skills与PowerShell脚本。`.specify/integration.json`记录版本，`.specify/feature.json`选择`specs/001-exception-followup`。功能规格、计划和任务按照官方模板与已确认培训需求准备，是课前检查点；它们不是一段已实际运行的Copilot课堂录像。

本目录保留业务TODO。学员在当前项目使用Spec Kit实施，不读取相邻完成版。

## 课前检查
```powershell
.\tools\speckit.ps1 version
.\tools\speckit.ps1 integration status --json
uv sync --locked
uv run --locked python tools/check_training.py
```
`tools/speckit.ps1`通过uv工具隔离调用固定CLI版本，不升级全局specify，不把Spec Kit加入应用依赖。首次使用需能访问PyPI；课堂前先缓存。
单独用VS Code打开本项目，切换Copilot Agent，确认`/speckit-specify`、`/speckit-plan`等技能出现在斜杠菜单。若未显示，重载窗口并检查Copilot技能支持；不能只凭本地文件存在就声称IDE验证通过。

## 材料分工
| 路径 | 用途 |
|---|---|
| AGENTS.md | 当前项目入口、操作边界 |
| .specify/memory/constitution.md | 项目原则，课前准备一次 |
| specs/001-exception-followup/spec.md | 业务目标、故事、需求和验收 |
| specs/001-exception-followup/plan.md | 技术方案与改动边界 |
| specs/001-exception-followup/tasks.md | 带ID的依赖任务与P1/P2范围 |
| specs/001-exception-followup/acceptance.md | 详细培训样例与核对数值 |
| docs/prompts.md | 可复制的官方技能调用及课堂约束 |

## 90分钟中的位置
第一模块10分钟中展示SDD概念、一次specify/clarify与预置plan/tasks，项目原则及安装不占课堂时间。异常跟进15分钟复用现有spec/plan/tasks，完成保存和GET确认。 Testing/Debugging模块再做一致性、测试、PR与CI；答疑20分钟。

## 教学检查点
1. **规格**：可以从业务描述更新本活动spec；需求改变会影响后续计划，先审阅差异。
2. **计划与任务**：课前已有可恢复结果，不要求现场重新生成所有文档。命令逐条运行，先看结果再继续。
3. **实现**：US1/US2均为P1；只补两处TODO和必要验证。
4. **验收**：离线、实时MCP、页面操作和远程CI分别记录。文档检查不能代替业务验证。

生成了错误规格或计划时，先看文件差异，修正规格再推进；不要删除已有练习或直接复制完成版。课前备份在讲师准备区，学员无需访问。

## 官方来源
- https://github.com/github/spec-kit （MIT许可，当前使用1.3.2官方模板）
- https://github.github.io/spec-kit/integrations/copilot.html
- https://github.github.io/spec-kit/quickstart.html
命令使用1.3.2的Copilot默认skills写法`/speckit-*`；旧版本可能显示点号写法，课堂以本项目已安装版本和IDE实际菜单为准。
