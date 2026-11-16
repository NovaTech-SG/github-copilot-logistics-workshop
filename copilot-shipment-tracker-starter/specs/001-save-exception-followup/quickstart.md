# Quickstart: 保存与确认验收

本指南列出可重复的验收步骤，末节记录 2026-11-16 本次实现的实际结果。保存与前端确认已实现。完整准备步骤沿用[项目 README](../../README.md)，字段及错误语义见[契约](contracts/followups.md)和[模型](data-model.md)。

## 前提

- 在 VS Code 仅打开当前 starter 应用，终端位置为本应用目录。
- 使用项目独立 Python 3.12、uv 环境和 Node.js 22；沿用现有锁文件及依赖。尚未准备环境时按 README 执行 uv sync。
- 实时验证需要已在本机安全配置的 MCP 凭据、Catalog/Schema 和读取权限；不在聊天或验证记录中粘贴 Token，不读取完整本机凭据配置作为证据。
- 使用明确的练习库路径，例如 data/practice-save-confirm.sqlite3。首次验证需尚不存在的练习文件；若已有文件则另取新文件名，不删除原库。重启时必须使用同一文件。

## 1. 离线验证

聚焦保存、HTTP 和提交流程可运行以下用例，无需改变 tests 包结构：

```powershell
uv run --locked python -m unittest discover -s tests -p "test_store.py" -v
uv run --locked python -m unittest discover -s tests -p "test_followup_api.py" -v
node --test tests\test_followup_submit.js
```

实施完成后按 README 运行项目离线验收：

```powershell
uv run --locked python tools/check_training.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m compileall -q app.py services tools
node --check static/app.js
node --test tests\test_followup_submit.js
```

预期：命令退出码为 0。结构检查允许只有 spec 和 plan，不要求 tasks；ready 不表示业务完成。离线测试仅使用临时数据库及假源，临时资源随测试关闭清理，不连接真实 MCP。

后端用例至少覆盖：首次插入、两种推进、三个状态下同状态更新、trim、1/1000/1001 字边界、无效与过期输入、同单异常隔离、重开同文件恢复、写入失败回滚。状态推进竞争可用两个连接验证旧 expected_status 被拒绝。HTTP 用例使用本机临时端口与假 reader，关闭服务并回收线程。

前端用例覆盖：POST 后 GET 顺序、编号/状态/备注任一不匹配、POST 拒绝、POST 结果未知、POST 成功但 GET 失败、手动重读再次核对、防重复与 finally 恢复操作。node --check 只证明语法，不能替代这些行为验证。

## 2. 两条真实 MCP 连接

开发连接通过已配置的 Databricks 只读 MCP 核对当前 Catalog/Schema 的三张表及 exceptions.updated_at 类型；只调用 execute_sql_read_only 和必要的 poll_sql_result。记录实际结果，不将培训快照视为必然值，不回写源表。

运行连接在现有安全环境中执行：

```powershell
uv run --locked python app.py --db data/practice-save-confirm.sqlite3 --check
uv run --locked python app.py --db data/practice-save-confirm.sqlite3
```

访问 http://127.0.0.1:8769。记录异常总数、状态分布和查询时间。169 条、40/69/60 仅是 README 的原始培训快照；以本次实际只读结果为准。Copilot 开发查询成功不能代替 Python 运行连接成功。

## 3. 保存与页面确认

1. 选择一条 OPEN 异常，记下真实 exception_id、shipment_id、源状态及可用源更新时间。同单有其他异常时一并记下其编号和当前结果。
2. 改为 IN_PROGRESS，输入带首尾空格的有效备注保存。观察按钮及编辑控件在保存和核对期间禁用，连续点击不产生第二个 POST。
3. 在浏览器网络面板确认 POST 对应目标编号，请求带 status、note、expected_status；随后 GET 同一编号，编号、状态、规范化备注匹配后才显示成功。
4. 核对本机保存时间与源更新时间分开，源状态仍为原值；概览、状态筛选与队列反映本机状态。总数保持本次实际值，同单其他异常保持原结果。
5. 验证保持状态更新备注，以及 IN_PROGRESS → RESOLVED，记录结果。不要将效果稿编号或静态统计作为证据。

## 4. 刷新与同库重启

1. 刷新或关闭后重新打开页面，重新选择目标异常，核对保存的状态、备注及时间。
2. 在启动该服务的终端按 Ctrl+C 正常停止；不停止其他进程，不删除数据库。
3. 使用第 2 节同一 --db 参数重新启动，重新读取目标，核对持久结果、源状态区别及概览。
4. 记录使用的库路径、目标编号、保存值与恢复后的值；不提交本机数据库。

## 5. 拒绝、冲突与未确认

- 空白、超长、跳级、退回、未知状态、缺原状态、不存在异常应按契约拒绝。UI 无法构造的无效值由离线 HTTP 用例覆盖，不绕过页面规则假称正常操作。
- 两个页面读取同一 OPEN 异常，其中一页推进后另一页使用旧原状态提交，应收到 409；重新读取后基于当前状态继续。
- 写入失败的“无部分更新”在临时库中用离线故障注入验证，不破坏真实练习库。
- 在可控测试中让 POST 成功而后续详情 GET 失败或返回不匹配内容，应提示已提交但尚未确认，不显示成功；恢复读取后仅在匹配时确认。
- 网络中断导致提交结果未知时提示未确认，引导读取；不可断言肯定未写入。每条失败流程结束后应恢复控件且保留必要草稿或待确认信息。

## 6. 记录实际证据

每次验收须分别记录命令、退出码或页面观察；未执行的分支明确写“未验证”，不预填通过。

## 7. 本次实际执行结果（2026-11-16）

用户在本次 implement 中明确选择“本轮同时实现后端和前端，并完成可执行的验收”。未执行 converge、提交、推送或部署。

### 离线验证

| 检查 | 实际结果 |
| --- | --- |
| 新增用例在起始版先运行 | 保存用例遇到 NotImplementedError、HTTP 合法保存返回 501、前端仍为练习提示，按预期失败 |
| tools/check_training.py | 退出 0；25 个任务、requirements_review_pending=false。工具固定输出 business_verified=false，不将其当业务结论 |
| unittest discover -s tests -v | 退出 0；28 项 Python 测试通过，包含原有阶段检查与新增保存/API/恢复用例 |
| compileall -q app.py services tools | 退出 0 |
| node --check static/app.js | 退出 0 |
| node --test tests/test_followup_submit.js | 退出 0；16 项前端行为测试通过 |
| git diff --check -- 当前应用 | 退出 0；README 有 CRLF 转 LF 提示，无空白错误 |
| VS Code 问题检查 | 修改的保存、查询、前端文件无报告错误 |

实际离线命令使用 uv run --locked --no-sync 加本项目 .venv/Scripts/python.exe 和上述参数；不下载依赖，Node 测试未新增 npm 包。最初源时间解析夹具漏了既有 manifest 契约，补齐夹具后通过，未修改解析器来迁就测试。

### 两条实时 MCP 连接

- Copilot 开发连接：execute_sql_read_only 查询 dev_databricks.default 三表，实际 carriers=4、shipments=500、exceptions=169；statement_id 为 01f1e1c1-e982-1111-8f2a-71f8782dd5b2。
- DESCRIBE exceptions 实际返回 updated_at 为 timestamp；statement_id 为 01f1e1c1-f421-1f63-a2f5-1b658e044210。
- Python 运行连接：使用 app.py --vscode-config .vscode/mcp.json --db data/implement-20261116-2122.sqlite3 --check，退出 0；169 条，OPEN / IN_PROGRESS / RESOLVED = 40 / 69 / 60。statement_id 为 01f1e1c2-14b6-156e-8979-e092c792ae37，poll_count=0。本机配置由现有后端读取，未打印凭据内容。

### 真实页面保存、故障及隔离

- 验收服务使用端口 8879 避免干扰默认端口；练习库固定为 data/implement-20261116-2122.sqlite3，未删除或覆盖已有练习库。
- 从实际源查询选出同单异常 EXC00082 / EXC00083（SHP000222）；前者源 RESOLVED，后者源 OPEN，备注为“待确认异常原因”。不使用效果稿样例。
- 浏览器将 EXC00083 从 OPEN 保存为 IN_PROGRESS，备注“课堂验收：已联系承运商，等待地址确认。”，首尾空格去除后重读确认。页面保存期间禁用按钮，再触发两次 submit 未重复写入；服务日志仅有一次 POST /api/exceptions/EXC00083 200，随后一次 GET 同编号 200。浏览器事件监听未采到请求数组，故顺序及次数证据使用服务日志，不虚报网络监听结果。
- 概览由 40 / 69 / 60 变为 39 / 70 / 60；保留待处理筛选时该异常退出筛选结果，详情仍显示源待处理及源更新时间。
- 同状态补备注“课堂验收：重读失败后恢复确认。”；仅对紧随 POST 的一个详情 GET 注入浏览器连接失败，不注入业务数据，原 fetch 自动恢复。实际显示“已提交但尚未确认”，手动重读后才显示已保存并确认。
- 用同一本机 API 将 EXC00083 从 IN_PROGRESS 推进为 RESOLVED，最终备注“课堂验收：地址已核实，完成跟进。”；旧页面仍以 IN_PROGRESS 提交时实际收到 409，显示状态已变化，保留草稿“旧页面不应覆盖”。手动读取后显示真实 RESOLVED 和最终备注。
- 刷新页面后搜索 SHP000222：EXC00082 仍为源 RESOLVED，无本机记录；EXC00083 为本机 RESOLVED，源仍 OPEN；最终概览为 39 / 69 / 61，总数 169。
- 再次只读查询源，同单两条异常的状态、备注及源更新时间与保存前一致；源核对 statement_id 为 01f1e1c2-bb21-1a5f-97dd-df8fd2bed570。EXC00083 源 updated_at 为 2026-09-14T19:09:00Z，页面上海时间为 2026/09/15 03:09，未被本机保存时间替代。

### 同库服务重启恢复

- 停止本次工具启动的服务，再用相同 --db data/implement-20261116-2122.sqlite3 和端口 8879 重启。
- 首次停工具后 Windows Python 子进程仍残留，重启页两次遇到 ERR_EMPTY_RESPONSE；核对本次命令及进程 ID 后，仅清理本次旧 Python 子进程。未修改应用来掩盖该环境问题。curl 本机页面返回 200 后重试读取成功。
- 重启后的真实页面仍显示 EXC00083 为 RESOLVED，最终备注完整，本机保存时间仍为 2026/11/16 21:35（上海）；源状态 OPEN、源更新时间和 EXC00082 源记录均不变，概览为 169 条、39 / 69 / 61。
- 验收结束后停止本次服务并清理经命令核对的本次残余子进程，确认端口 8879 不再监听；保留 SQLite 供本机复查。临时测试库由 TemporaryDirectory 清理，数据库及 .venv/.env 均经 git check-ignore 确认为忽略。

### 实际验证边界

- 空白/超长备注、跳级/退回、未知状态、缺失原状态、不存在异常、并行推进、写入故障回滚、500 和解析失败均有离线用例；没有逐一在真实源页面复演所有非法输入或破坏真实库权限。
- GET 编号/状态/备注不匹配、迟到响应及切换异常以 Node 替身测试验证；真实页面验证了连接失败未确认和恢复，没有伪造实时业务响应。
- 同库重启已验证停止进程后恢复；未验证断电、磁盘损坏或跨库迁移，也未承诺同状态并发备注的版本冲突检测。
- 所有凭据仅留在后端，本次没有新增依赖、源写入、提交、推送或部署。已有 .vscode/mcp.json 用户改动保留，未读取或展示其内容。
