# 数据模型
- 源记录：exceptions、shipments、carriers，只读；exception_id唯一，shipment_id可能重复。
- FollowUp：exception_id主键、handling_status、follow_up_note、updated_at；只存当前项目SQLite。
- 状态：OPEN允许OPEN或IN_PROGRESS；IN_PROGRESS允许本身或RESOLVED；RESOLVED只允许本身。
- 备注：trim后1至1000字；expected_status不符拒绝覆盖；源记录通过overlay合成本机视图。
