# Spec Kit 学员操作说明

当前目录是起始项目，保留本次需要完成的业务 TODO。只在本项目内实施，不读取相邻完成版。

## 先准备项目

按 [README](../README.md) 安装依赖与配置个人授权。首次克隆后执行下面的 bootstrap；已有有效的活动功能会保留。

```powershell
uv run --locked python tools/bootstrap_training.py
.\tools\speckit.ps1 version
.\tools\speckit.ps1 integration status --json
uv run --locked python tools/check_training.py
```

本项目使用 Spec Kit 1.3.2、Copilot skills 和 PowerShell 脚本。只用 VS Code 打开当前项目，在 Copilot Agent 聊天的斜杠菜单中确认 `/speckit-*` 技能可用。首次调用固定 CLI 版本需要网络；技能未显示时按 README 排查。

## 文档分别做什么

| 文件 | 用途 |
|---|---|
| `AGENTS.md` | Agent 的操作入口与范围 |
| `.specify/memory/constitution.md` | 项目原则 |
| `specs/001-exception-followup/spec.md` | 业务目标、需求与验收条件 |
| `specs/001-exception-followup/plan.md` | 技术方案与边界 |
| `specs/001-exception-followup/tasks.md` | 任务编号、依赖与本次范围 |
| `specs/001-exception-followup/acceptance.md` | 培训样例和预期计算结果 |
| `docs/prompts.md` | 可复制的分步聊天提示词 |
| `docs/validation.md` | 使用者自己的验证记录 |

活动功能由 `.specify/feature.json` 选择。`docs/spec.md` 和 `docs/tasks.md` 是指向活动功能的入口。

## 按步骤使用

1. 阅读现有业务规格，确认输入输出与验收条件；有新需求时再用 `/speckit-specify` 更新。
2. 有未确定的边界时使用 `/speckit-clarify`；规则已完整时直接继续。
3. 阅读现有 plan 和 tasks。需求改变时再更新计划与任务，并先检查文件差异。
4. 用 `/speckit-implement` 实现当前 P1，按实际执行更新任务。
5. 用 `/speckit-analyze` 核对文档一致性，用 `/speckit-converge` 检查本次范围的缺口。

异常跟进的 P1 为保存、页面提交与重读确认，并验证非法输入和过期状态；复用已有读取与规则校验。

运行后在 [验证记录](validation.md) 分开记录结构检查、离线测试、真实 MCP 与页面操作。任务勾选表示记录了对应执行，不自动证明所有业务验收均已通过。修改前保留自己的练习，不用完成版覆盖起始项目。

## 官方参考

- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [Copilot 集成说明](https://github.github.io/spec-kit/integrations/copilot.html)
- [Spec Kit 快速开始](https://github.github.io/spec-kit/quickstart.html)

本文使用本项目已安装的 `/speckit-*` 写法。IDE 菜单或版本不一致时，以项目版本和实际菜单为准。
