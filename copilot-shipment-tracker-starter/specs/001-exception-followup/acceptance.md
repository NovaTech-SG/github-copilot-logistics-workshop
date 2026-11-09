# 验收明细与原教学约定

本页保留已确认的详细规则和数值，业务需求以spec.md为准，技术实现以plan.md为准。

# 运输异常跟进规格

## 业务目标

物流同事从异常队列中找到待跟进记录，填写处理动作并更新状态，重新打开后可以看到已保存的进度。

本案例对应大纲中的Shipment Tracker异常跟进。状态流转与备注规则为明确的教学约定，不代表Nike生产业务政策。

## 输入与存储

通过Databricks只读MCP读取dev_databricks.default.exceptions、shipments与carriers。源异常包含exception_id、shipment_id、exception_type、handling_status、follow_up_note、assigned_team、detected_at。

本机SQLite只保存exception_id、handling_status、follow_up_note、updated_at。显示时按异常编号覆盖源状态和备注，并保留源状态供识别。源表不修改。没有本机记录时显示源状态和备注，不自动批量写入SQLite。

## 业务规则

- OPEN（待处理）→IN_PROGRESS（处理中）→RESOLVED（已解决），不得跳过或退回。
- 可以保持当前状态并更新备注，RESOLVED可补充备注但不可重新打开。
- 备注去首尾空格后非空，最多1000字。
- 保存带上页面原状态。原状态与当前保存状态不符时拒绝覆盖，提示重新读取。
- 以exception_id为主键。一张运输单的多条异常分别跟进。
- POST成功后再次GET记录核对；失败或未确认不能提示成功。
- 时间显示Asia/Shanghai。源记录与本机保存记录明确标注。

## 课堂跟练

预置MCP连接、查询、异常列表、详情和本地库结构；学员完成保存方法与前端提交后重新读取。约15分钟，重心在业务规则、多文件修改与验收。

## 验收

1. 空本地库时读取169条源异常，待处理40、处理中69、已解决60。
2. 选择一条OPEN记录，改为IN_PROGRESS并填备注，保存后GET结果一致。
3. 刷新或重启相同数据库后仍保留修改；新数据库仍显示源状态。
4. 空备注、超过1000字、跳转OPEN→RESOLVED与逆向流转均拒绝，不能留下部分写入。
5. 源记录不变化，相同运输单的其他异常不变化；页面标明本机记录。
6. 过期原状态返回409；无效输入400；不存在记录404；MCP失败502且不以假数据替代。
7. 窄屏可操作，Token不进入前端；本地数据库与凭据不提交。

完成后的PR/CI演示放在大纲单独的Testing Debugging与协作交付环节，不挤入15分钟基础跟练。
