# GitHub Copilot 物流应用实操工作坊

Nike GC Logistics · Session 2 · 90 分钟

[![Workshop CI](https://github.com/NovaTech-SG/github-copilot-logistics-workshop/actions/workflows/ci.yml/badge.svg)](https://github.com/NovaTech-SG/github-copilot-logistics-workshop/actions/workflows/ci.yml)

通过 Spec Kit 把业务需求逐步变成规格、计划、任务和可运行的本地应用。全部业务数据为培训模拟数据，不代表 Nike 实际运营情况。

## 资料与下载

| 资料 | 用途 |
|---|---|
| [Session 2 培训大纲 Word](<Nike GC Logistics Session 2 培训大纲.docx?raw=true>) | 培训目标、90 分钟安排和课前准备 |
| [Databricks 三张表业务表说明 Word](<Databricks 三张表业务表说明.docx?raw=true>) | 业务对象、字段、关联和查询练习 |
| [培训模拟 CSV](data/README.md) | 三张源表的静态示例，供理解数据和准备培训表 |

Word 与 CSV 随代码一起下载。Databricks 培训表由讲师准备，使用者配置自己的访问授权；CSV 不会自动导入，也不作为应用运行时数据源。

## 选择项目

| 项目 | 起点与目标 | 端口 |
|---|---|---:|
| [Dashboard starter](copilot-logistics-dashboard-starter/README.md) | 从技术骨架、空 specs 和 mockup 开始，生成运输表现看板 | 8767 |
| [异常跟进 starter](copilot-shipment-tracker-starter/README.md) | 在已有异常队列上新增 SQLite 保存和重读确认 | 8769 |
| [Dashboard 完成版](copilot-logistics-dashboard/README.md) | 运行完整效果，复盘规格与实现 | 8766 |
| [异常跟进完成版](copilot-shipment-tracker/README.md) | 运行完整效果，复盘保存与确认 | 8768 |

克隆一次后，在 VS Code 中只打开当前案例目录。四个应用各有自己的 `uv.lock` 和 `.venv`，依赖安装、启动和 Spec Kit 命令都在对应目录执行。

```powershell
git clone https://github.com/NovaTech-SG/github-copilot-logistics-workshop.git
cd github-copilot-logistics-workshop/copilot-logistics-dashboard-starter
```

继续按该项目 README 准备环境和连接。开发时只读当前 starter，完成后再对照参考完成版。

## 学员阅读顺序

1. 当前项目 `README.md`：准备环境、课堂步骤与验收。
2. `docs/data-source.md`：Databricks MCP、三张表关系与业务规则。
3. `mockup/index.html`：直接在浏览器查看静态目标效果。
4. `docs/prompts.md`：复制一句话需求到 Copilot Agent，逐步调用 Spec Kit。
5. 课堂生成的 `specs/`：审阅本次 spec、plan、tasks，再按任务实现。

两个 starter 的 `specs/` 初始只有 `.gitkeep`。Spec Kit 技能、模板和项目原则已配置，不必重新 init，也不需要在课堂重建工具文件。`AGENTS.md` 和 `.github/` 供 Agent 使用；第三方来源与许可见各项目 `THIRD_PARTY_NOTICES.md`。

## 课堂路径

| 环节 | 本次范围 |
|---|---|
| 课前准备 | Windows PowerShell、Git、VS Code 与 Copilot Agent、uv、Node.js 22；分别验证 Copilot 和 Python 的 MCP 连接 |
| Dashboard 15 分钟 | 需求 → spec → plan → tasks → P1 查询、四指标、筛选与对比图 |
| 异常跟进 15 分钟 | 新功能 spec → plan → tasks → 本机保存、提交后重读、失败反馈与验证 |
| 复盘与答疑 | 核对业务结果、解释实现、查看 PR 差异和 CI |

Dashboard 的趋势、自然日补零与明细分页属于 P2 扩展；异常跟进的状态校验和失败反馈属于本次保存功能。课程总时长和两个案例的时间安排不变。

业务源表始终经 Databricks 只读 MCP 读取；异常跟进结果只写当前应用本机 SQLite。Token、`.env` 和本机数据库不提交。

## 验证与协作

各项目 README 提供离线检查和实际操作清单。绿色 [CI](.github/workflows/ci.yml) 表示四个独立项目的结构、离线测试及 JavaScript 语法检查通过；它不访问现场 Databricks，也不部署服务器。学员仍需记录实际 MCP、页面操作和未验证项。

完成本次练习后先检查 `git diff -- .`，再按课堂安排提交分支与 PR。
