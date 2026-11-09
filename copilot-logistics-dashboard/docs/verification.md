# 本地验证记录

日期：2026-11-06（上海时间）。验证环境为 Windows、Python 3.12.14、uv 0.7.13、MCP Python SDK 1.30.0。

## 真实 Databricks MCP

使用本机已配置的 `databricksTraining` Bearer Token，经显式 `--vscode-config` 读取；未复制凭据到项目。通过 `execute_sql_read_only` 查询已有培训表，未写入业务数据。

运行：`uv run --locked python tools/verify_live.py --vscode-config`，全部检查通过。

| 检查 | 实际结果 |
|---|---|
| 整体 | 500单、有效380、准时304、延误76、排除120、准时率80% |
| 已送达缺少到达时间 | 整体20单，CAR002为6单 |
| CAR002 | 134单、有效104、准时77、延误27、准时率74.04% |
| CAR002最后一页 | 第7页，14条；与第1页无重复 |
| CAR999空范围 | 0单，准时率NULL，空明细 |
| 每日趋势 | 65个自然日，缺失日补零 |
| 数据快照 | 2026-11-05 12:00，Asia/Shanghai |

本轮复核的 Statement ID（依次为全部、CAR002第1页、CAR002第7页、空范围）：

```text
01f1d9b0-df5a-1374-8078-2c0e30477c8f
01f1d9b0-e216-1b65-8921-a387dd14e8bd
01f1d9b0-e49f-10ac-b20b-b639dfa7bece
01f1d9b0-e7b7-147b-afbf-5b6eadb2caad
```

## 离线检查

- `uv run --locked python -m unittest discover -s tests -v`：8项测试通过。
- `node --check static/app.js`：通过。
- PowerShell Parser检查 `start.ps1`：无语法错误；脚本的交互输入分支未另行手动演练。
- 已检查项目文本文件：未包含本机实际Token。浏览器只请求本地API，认证头由Python服务端发送。

## 浏览器检查

Chrome / Playwright，使用正在运行的本地服务和真实MCP结果：

- 全部范围500单、380有效、80.00%，4个承运商、65天趋势及20条明细。
- 切换CAR002后134单、74.04%，明细承运商一致。
- 下一页仍为CAR002，与第1页无重复；清除筛选恢复全部范围第1页。
- 390px视口下无页面整体横向溢出；表格在自身容器内滚动。
- 拦截一次API响应为502，确认错误提示出现且旧结果隐藏；解除拦截后点击重试，成功恢复真实MCP结果。控制台的该条502为主动故障验证，无其他JavaScript错误。
- 已目视检查桌面及移动页面截图，保存在git忽略的 `output/playwright/` 下。

## 尚未验证

GitHub Actions只已配置，未推送、未触发远程CI、未创建PR。当前仓库已初始化本地Git，没有提交或远程仓库。Copilot现场增量开发步骤已写入演示文档，本轮未代替学员在Copilot中执行该增量需求。
