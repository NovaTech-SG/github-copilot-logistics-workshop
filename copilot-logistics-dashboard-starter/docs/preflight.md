# 起始项目准备检查

2026-11-06在讲师Windows环境完成以下检查：

- 使用锁定依赖创建独立Python 3.12环境，uv同步成功。
- Python入口与services模块编译通过，JavaScript和PowerShell启动脚本语法检查通过。
- 通过显式指定本机VS Code配置，实际执行MCP只读 `SELECT 1 AS result`，返回SUCCEEDED。
- 起始页返回HTTP 200；业务API返回预期HTTP 501，说明练习尚未实现。
- 完成版仍在独立8766端口可访问，学员项目使用8767。

这份记录只说明讲师环境中的起始项目可启动、MCP连接可用。每位学员仍需用自己的获授权身份完成课前检查；不代表Dashboard业务已完成。业务验收在课堂实现后进行。

分发包仅包含源码、依赖锁和文档，不包含讲师Token、用户级MCP配置、.venv、Git历史、浏览器记录或完成版代码。
