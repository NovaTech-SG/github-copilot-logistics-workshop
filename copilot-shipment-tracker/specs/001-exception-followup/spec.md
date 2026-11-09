# Feature Specification: 运输异常状态与备注跟进

**Feature Branch**: `main`（本次未创建分支，活动功能由.specify/feature.json选择）
**Created**: 2026-11-09
**Status**: Completed reference; validation reported separately
**Input**: 物流同事希望从异常队列找到待跟进记录，保存处理状态和备注，重新打开后仍能看到进度。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 保存并确认跟进结果 (Priority: P1)
物流同事选一条待处理异常，改为处理中并填备注；保存后重新读取，刷新或重启后复查。

**Why this priority**: 这是15分钟跟练的核心闭环。
**Independent Test**: 同一异常编号保存、重新读取、重新打开后状态和备注一致。
**Acceptance Scenarios**:
1. **Given** 一条OPEN异常，**When** 填有效备注并改为IN_PROGRESS，**Then** 保存后重新读取到同一状态和备注。
2. **Given** 已保存记录，**When** 重启并使用同一存储位置，**Then** 修改仍保留；使用新存储位置仍显示源记录。
3. **Given** 同一运输单的另一条异常，**When** 保存目标异常，**Then** 另一条异常和源数据均不改变。

### User Story 2 - 拒绝非法或过期的更新 (Priority: P1)
物流同事提交无效输入或过期页面时，得到明确提示，原记录保持原值。

**Why this priority**: 避免页面成功提示与真实保存不一致。
**Independent Test**: 空备注、超长备注、跳过或退回状态、过期原状态分别拒绝且不留下部分写入。
**Acceptance Scenarios**:
1. **Given** OPEN，**When** 直接提交RESOLVED或空备注，**Then** 拒绝保存，记录保持原值。
2. **Given** 页面原状态已过期，**When** 再提交，**Then** 提示重新读取，不能覆盖新状态。
3. **Given** 提交或确认失败，**When** 页面反馈，**Then** 不显示保存成功。

### Edge Cases
- 可保持当前状态补充备注，RESOLVED不能重新打开。
- 备注去首尾空格后必须非空且最多1000字。
- 一个运输单有多条异常，以异常编号分别保存。

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: 从获授权的培训源数据读取队列和详情，显示源状态与本机跟进记录的区别。
- **FR-002**: 状态按OPEN到IN_PROGRESS再到RESOLVED推进，不跳过或退回；允许同状态更新备注。
- **FR-003**: 备注去首尾空格后非空且最多1000字。
- **FR-004**: 按exception_id保存本机状态与备注，不回写源数据；同运输单其他异常不变。
- **FR-005**: 保存后重新读取同一异常确认；未确认或失败不显示成功，保存期间防止重复提交。
- **FR-006**: 重启后使用相同存储位置仍保留状态和备注，新存储位置显示源记录。
- **FR-007**: 检查提交时的原状态，过期时拒绝覆盖；无效更新不产生部分写入。
- **FR-008**: 连接或读取失败给出明确提示，凭据不进入页面或提交，显示时区为Asia/Shanghai。
- **FR-009**: 保留规则校验、保存恢复、失败反馈和独立异常的验证记录。

### Key Entities
- Exception：异常记录，exception_id唯一，可与同一shipment_id的其他异常并存。
- FollowUp：本机保存的handling_status、follow_up_note、updated_at及异常编号。
- OriginalStatus：页面提交时看到的原状态，用于拒绝过期更新。

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: 未保存本机记录时，169条源异常分布为待处理40、处理中69、已解决60。
- **SC-002**: 合法更新在重新读取和重启后保持一致，源记录及其他异常不变。
- **SC-003**: 非法与过期更新全部拒绝，且原记录保持原值。
- **SC-004**: 学员能说明保存位置与源数据的区别，提供必要检查和未验证项。

## Assumptions
- 状态流转和备注要求是本课教学约定，不代表Nike生产政策。
- 连接、列表、详情和保存基础结构已课前准备，本课补全保存与提交后确认。
- 仅本地使用；不安排多人生产存储、服务器部署或自动发布。

## Clarifications
### Session 2026-11-09
- Q: 状态直接写回源数据吗？ → A: 不写回，源只读，跟进结果仅保存在本机。
- Q: 已解决后能否重新打开？ → A: 本课不允许，可在同状态补充有效备注。
- Q: 怎样证明保存成功？ → A: 保存后重新读取，并用同一存储位置重启复查。
以上答案来自已确认培训规格，非现场自动收集的回答。
