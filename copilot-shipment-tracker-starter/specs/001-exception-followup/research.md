# 技术选择记录

## 决策：沿用现有应用与只读MCP
理由：本课练习需要业务规则、多文件修改和验证，连接模块已准备。
已检查：当前services、static、uv.lock和课堂范围。
备选：CSV、SQL Connector或重建框架会改变数据源或增加课堂工作量，本次不采用。

## 决策：Spec Kit 1.3.2，Copilot skills，PowerShell
理由：官方CLI已安装官方模板和脚本；通过uv工具隔离调用，不改变应用Python 3.12环境。
确认方式：tools/speckit.ps1 version和integration status --json。
不确定项：个人凭据、实时查询和IDE技能显示需课前验证，不能由这些文档保证。
