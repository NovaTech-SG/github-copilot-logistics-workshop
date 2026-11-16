# 完成版复盘提示词

本目录用于只读复盘。先按 [README](../README.md) 运行应用，再在 Copilot Agent 聊天框逐条使用下面的提示词。编码跟练请使用 starter 项目，不把完成版加入 starter 的工作区。

## 理解业务规则

```text
阅读本项目 AGENTS.md、specs/001-carrier-dashboard/spec.md 和 acceptance.md，解释主要业务规则、边界条件，以及页面结果如何核对。只读说明，不修改文件或数据。
```

## 理解数据与调用路径

```text
在当前项目内说明浏览器、本地 Python 后端、Databricks 只读 MCP 的调用关系。解释数据如何传递、错误如何返回，以及凭据和本地状态的边界。不要读取或展示实际 Token，不访问相邻项目。
```

## 对照规格与任务

```text
/speckit-analyze 检查当前活动 spec、plan 与 tasks 的一致性，说明关键要求如何对应任务和验收。只读报告，不执行实现，不把任务勾选当作本次运行证据。
```

## 检查自己的验证记录

```text
对照 docs/validation.md 和当前功能 acceptance.md，列出本次已记录的检查与尚未验证的项目。区分离线检查、实时 MCP、页面操作和远程 CI；没有执行证据的项目保持未验证。不要提交、推送或部署。
```
