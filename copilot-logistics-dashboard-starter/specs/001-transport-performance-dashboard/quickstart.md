# Quickstart & Validation: 运输表现看板

**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) | **Contract**: [dashboard-api.md](contracts/dashboard-api.md)

## 1. 使用时机与前提

本文是运行与验收指南。当前已按用户明确选择完成 P1 与 P2；services/dashboard.py 和 services/queries.py 已实现，业务 API 使用真实只读 MCP。下方保留可重复的验收步骤，本次实际结果见第 8 节。

- VS Code 打开当前 starter 应用，在该目录的 PowerShell 中运行命令，不切到仓库父目录或相邻完成版。
- 使用本项目 Python 3.12 和独立 uv 环境，既有依赖按 [README](../../README.md) 准备；不创建根 uv workspace，不安装前端构建工具。
- 用户已在本机配置 Databricks 读取权限和连接；凭据仅由后端读取。不得把实际 Token 写入聊天、命令示例、页面或验收记录。
- Copilot 开发时的 MCP 与 Python 运行时连接须分别验证，聊天查询成功不等于应用查询成功。
- spec、plan、tasks 已形成。本次用户明确选择“完整 P1 与 P2”，因此两阶段均在实施范围内；后续修改仍按活动任务和当次课堂指令推进。

## 2. 实现阶段的离线检查

在当前项目已配置的 Python 环境中运行；规划阶段未执行这些命令，本次实现阶段的执行结果见第 8 节。

真实 SQL 夹具测试默认跳过，需要显式启用（不写源表）：

```powershell
$env:DASHBOARD_LIVE_TESTS = '1'
$env:DASHBOARD_VSCODE_CONFIG = '.vscode\mcp.json'
uv run --locked python -m unittest discover -s tests -p 'test_queries.py' -v
Remove-Item Env:DASHBOARD_LIVE_TESTS
Remove-Item Env:DASHBOARD_VSCODE_CONFIG
```

```powershell
uv run --locked python tools/check_training.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked python -m compileall -q app.py services tools
node --check static/app.js
```

结构检查只证明 SDD 阶段和基础文件有效，不证明业务完成。后端变更时先运行对应测试模块；阶段整体验收再执行上述组合，不重复运行没有新依据的全套检查。

业务测试至少覆盖：恰好到达算准时；提前/延误；在途/取消排除；已送达缺时间排除；零分母；按总计数求整体比例；空范围；合法/非法筛选及页码；MCP 失败、截断和无效结构；名称映射不放大单量。测试数据允许人工构造，不作为运行时数据源。

## 3. 运行连接与本地服务

本机已有环境变量配置时：

```powershell
uv run --locked python app.py --check
uv run --locked python app.py
```

如果使用当前项目的本机 VS Code 配置，则显式选择它，命令不输出文件中的实际凭据：

```powershell
uv run --locked python app.py --vscode-config .vscode\mcp.json --check
uv run --locked python app.py --vscode-config .vscode\mcp.json
```

`--check` 只执行 SELECT 1；connection=OK、business_verified=false 不证明运输单业务正确。服务启动后检查 http://127.0.0.1:8767 是否响应；端口占用时先核对现有进程，不终止未知服务。

## 4. P1 后端验证

实现 P1 后请求：

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8767/api/dashboard' | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri 'http://127.0.0.1:8767/api/dashboard?carrier=CAR002&page=1' | ConvertTo-Json -Depth 8
```

响应结构、计数及空数组遵守接口合同。预期结果由同次 Databricks 只读独立核对确定，不以 mockup 或聊天导出文件作为依据。可在 Copilot 的只读 MCP 中执行以下核对语句；实际前缀若不同使用已确认配置。

```sql
SELECT
  COUNT(*) AS total_count,
  COUNT_IF(status = 'DELIVERED'
    AND planned_arrival IS NOT NULL AND actual_arrival IS NOT NULL) AS eligible_count,
  COUNT_IF(status = 'DELIVERED'
    AND planned_arrival IS NOT NULL AND actual_arrival IS NOT NULL
    AND actual_arrival <= planned_arrival) AS on_time_count
FROM dev_databricks.default.shipments;
```

核对 CAR002 时，对同一语句加 `WHERE carrier_id = 'CAR002'`；按规格由三项计数推导延误、排除、比例，逐项比较 HTTP 结果。全部汇总等于各承运商计数之和。数据说明中的历史数值只有源快照未变时才适用。

使用离线 HTTP 测试验证 400 参数错误、502 数据失败、500 通用内部错误，不要求修改实际源数据来触发错误；未知但合法编号应返回 200 空集合。P1 page=2、重复参数、非法字符必须在源查询前拒绝。

## 5. P1 浏览器验证

打开 http://127.0.0.1:8767 ，按下列顺序验收：

1. 首次打开显示加载，成功后展示全部范围的四指标、准时量、排除量与口径，承运商对比含名称、编号及分子/分母。
2. 选择一个承运商触发查询，范围、指标与对比同步；重新查询保留筛选，清除恢复全部并重新查询。
3. 快速从甲切到乙，使甲较晚返回，最终只能显示乙结果；同样验证甲较晚失败不覆盖乙成功。
4. 用受控响应或离线夹具验证零分母、成功无记录、请求延迟、查询失败及恢复后重试；不修改源表、不使用这些响应作为正常运行的数据兜底。
5. 在桌面及约 390 CSS 像素宽度中核对可操作性：四指标清晰，名称/编号与按钮可读，筛选可用，加载/错误可辨识，键盘可到达控件。
6. 检查浏览器请求仅访问本地接口，响应和页面无凭据；运行时失败没有返回 mockup、CSV 或导出文件内容。
7. 对照 SC-004，成功后 30 秒内读出四指标和需要关注的承运商；无有效分母时说明 N/A 的原因。

P1 不显示未实现的趋势、明细或时间说明作为假数据占位。

## 6. P2 单独验证

仅在 P2 实现后进行：

- 趋势：选择有缺失自然日的范围，核对日期连续、缺失日为零、合计等于总量；单日和空范围分别只显示真实一天或无日期。
- 分页：以同一稳定源集合逐页请求，单页不超过 20，按业务日期和单号升序，跨页无重复/遗漏；总页数和末页条数依据当时总量计算。
- 翻到第 2 页后筛选、清除、刷新均回第 1 页；超末页请求按合同钳制，空范围分页禁用。
- 五类结果：准时、延误、在途、取消、已送达但时间缺失全部可区分，缺失时间显示“—”。
- 时间：源数据最新快照来自当前范围最大非空 snapshot_at；查询完成时间来自本次成功请求；分别显示上海时间，空快照不被当前时间替代。

## 7. 验收记录与本阶段实际结果

每轮在课堂会话中记录任务 ID、变更文件、命令及结果、真实查询范围与观察值、页面操作、未验证项。不为记录自动新增跟踪文档，也不提交、推送或部署。

本次 `/speckit-plan` 实际完成：

- 已核对当前活动 spec、项目原则、已有服务和数据源合同。
- 已通过只读 MCP 验证 carriers 字段、4 个唯一编号、shipments 500 个唯一编号、业务日期完整及源状态符合说明；未匹配承运商的运输单为 0。此结果仅为 2026-11-16 当次观察。
- 已生成 plan、research、data-model、HTTP 合同和本指南，设计前后原则门禁均通过。
- 规划阶段未执行业务实现、业务单元测试、Python 运行连接、Dashboard 聚合 SQL 或浏览器业务验收；实施阶段实际结果如下。

## 8. 本次完整 P1/P2 实现与执行证据（2026-11-16）

用户在实施范围选择中明确选择“完整 P1 与 P2”。本次执行 T001—T047，保留既有依赖、连接模块和独立环境，没有修改业务源表或本机实际凭据配置。

- **离线**：28 个 unittest 中 23 个通过、5 个实时 SQL 用例按默认设置跳过；既有课堂状态测试全部通过。Python compileall、node --check、课堂结构检查通过。结构检查仍输出 business_verified=false，因为该工具本来不执行业务验证。
- **运行连接**：app.py --vscode-config .vscode/mcp.json --check 实际返回 connection=OK、sql_state=SUCCEEDED、business_verified=false；与下面业务查询分开记录。
- **真实 SQL 语义**：显式启用 tests/test_queries.py 中的 LiveQueryTests，5 项实时测试全部通过（加上 2 项参数测试，本次运行共 7 项通过）。将构造 VALUES/CTE 输入嵌入同一 build_query 的源位置，不创建临时表；覆盖相等算准时、缺失判断时间、在途/取消、加权比例、维度重复不放大、未知名称、零分母、空范围、自然日补零和 41 单 20/20/1 分页及越界钳制。
- **真实业务 HTTP**：全部范围总量 500、有效 380、准时 304、延误 76、排除 120、准时率 80.00%；65 个连续业务日期的趋势合计 500，其中 2026-10-28 补零。CAR002 总量 134、有效 104、准时 77、延误 27、准时率 74.04%。独立只读 MCP 按承运商聚合核对一致，未将历史数字写成应用常量。
- **逐页完整性**：逐页请求全部 25 页得到 500 个唯一单号，末页 20 单；逐页请求 CAR002 的 7 页得到 134 个唯一单号，末页 14 单。两组均排序正确、无重复遗漏，页面间 summary 一致，趋势合计一致；真实数据覆盖全部五类运输结果。未知合法编号返回成功空范围、空趋势/明细和 null 源快照。
- **浏览器实际交互**：已核对首次加载、全部/筛选、下一页、刷新保留筛选、清除恢复全部、筛选/刷新回首页，以及两种时间的上海展示；真实源快照 2026-11-05T04:00:00Z 显示为上海 12:00，查询完成时间单独显示。
- **浏览器受控边界**：仅在验收页面临时拦截响应，验证 502 后旧结果隐藏、重试恢复真实结果、翻页失败重试保留第 2 页、空范围分页禁用和 N/A；用页面内临时 fetch 替身验证旧成功及旧失败都不能覆盖最新 CAR002 结果。完成后移除拦截/替身并恢复真实查询，未添加运行时代码兜底。
- **布局与可访问性**：桌面与 390px 宽度均查看；390px 下文档宽 375px，外层无横向溢出，表格在自己的容器滚动。筛选可聚焦，Tab 到达清除按钮。后台浏览器页面的部分普通点击/滚动曾被工具稳定性检查阻塞，已确认控件可见启用、无 smooth scrolling；验收改用已定位控件的事件触发，没有为此改动产品行为。
- **分析问题处理**：SQL 语义验证已通过上述只读夹具执行落地；本次为完整范围交付，后端和页面两部分均实际验收；SC-004 补充全部准时时可判断无需跟进。页面可读性已由代理走查，尚未进行真实运营人员的 30 秒计时研究。
- **实现细节与限制**：为在单查询中按总量钳制末页，使用 SQL ROW_NUMBER 范围过滤取 20 条，等价满足查询侧分页，不使用前端切片；跨请求源数据更新期间仍不保证冻结快照。没有运行远程 CI、提交、推送或部署。
