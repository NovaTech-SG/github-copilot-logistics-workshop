# HTTP与保存合同
- GET /api/exceptions：返回通过源数据与本机overlay合成的队列。
- GET /api/exceptions/{exception_id}：返回同一异常最新状态与备注，标明源与本机。
- POST /api/exceptions/{exception_id}：输入status、note、expected_status。仅写本机SQLite。
- 保存后前端再次GET确认。400无效输入，404记录不存在，409过期状态，502源查询失败；未确认不能显示成功。
- 事务核对当前本机或源状态，复用validate_change，再参数化写入并overlay读取；失败不部分写入。
