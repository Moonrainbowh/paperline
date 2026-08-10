# 目标期刊写作合同接收

用于接收外部期刊筛选模块产生的 `target-journal-writing-contract.md`。本模块只验证并引用交接文件，不执行期刊筛选，不复制期刊画像、领域蓝图或上游 Skill 的正文。

## 目录

1. 两种合法入口
2. 状态映射
3. 接收校验
4. 应用边界
5. 期刊或合同变化
6. 交接记录

## 两种合法入口

### 通用中文稿

目标期刊未确定时：

- 单独使用本 Skill 时记录 `venue-unselected`，使用通用中文学术结构和证据规则。
- 仅在 `paperline` 已记录作者授权、旁路原因和回退点时，才将顶层模式标记为 `venue-pending`。
- 单独使用本 Skill 的 `venue-unselected` 路线允许通用中文稿达到 `S6`，也允许作者锁定该通用版本为 `S7`；`paperline` 的 `venue-pending` 旁路最多到 `S6`，不得声明 `S7`、建立作者锁或把 P3 标记为完成。
- 不宣称已经满足任何期刊的篇幅、结构、披露、格式或语言要求。

### 已确认期刊合同

要求同时能读取正式写作合同及其链接的正式选刊决定。验证下列字段，字段值仍保留在原文件中：

| 文件 | 必需字段 |
| --- | --- |
| `target-journal-decision.md` | `artifact_type: target_journal_decision`、`schema_version`、`status: confirmed`、`manuscript_id`、`manuscript_revision`、`selected_candidate_id`、`target_journal`、`article_type`、`section_or_collection`、`evidence_version`、`last_verified_at`、`author_confirmed_at`、`selection_evidence_file`、`selection_evidence_sha256`、`blocking_issues: []` |
| `target-journal-writing-contract.md` | `artifact_type: target_journal_writing_contract`、`contract_version`、`contract_id`、`status: confirmed`、`manuscript_id`、`manuscript_revision`、`target_journal`、`article_type`、`section_or_collection`、`research_field`、`generated_at`、`last_verified_at`、`author_confirmed_at`、`selection_evidence_version`、`writing_profile_evidence_id`、`decision_file`、`decision_sha256`、`journal_profile_file`、`journal_profile_sha256`、`field_blueprint_file`、`field_blueprint_sha256`、`requires_recheck_before_submission: true`、`blocking_issues: []` |

`section_or_collection` 必填，没有专栏时显式写 `none`。合同正文 `paper_navigator_handoff` 块中的状态、期刊、论文类型、两类证据标识、决策哈希和阻塞项也必须与头部一致；`priority_focus`、`required_sections` 和各类 `*_source` 仅是可选路由提示，缺少时直接读取已验证契约正文。不要根据散文描述猜测缺失字段，也不要把候选表、推荐报告、未确认画像或单独的选刊决定冒充写作合同。

## 状态映射

| 上下文 | 规范状态 | 含义 |
| --- | --- | --- |
| `paper-navigator` 单独写作 | `venue-unselected` | 普通未选刊，可写通用中文稿 |
| `paperline` 作者授权旁路 | `venue-pending` | 已显式跳过 P2，须记录回退与失效范围 |
| 已有契约但未通过 | `contract-pending` | 不应用期刊规则 |
| 契约通过且绑定当前稿件 | `contract-confirmed` | 可将锁定规则应用到中文写作 |

`journal-navigator` 文件内部的 `draft / pending_confirmation / confirmed` 是产物状态，不直接代替上表的路由状态。

## 接收校验

按顺序执行：

1. 核对两个 `artifact_type`、版本字段与 `status: confirmed`；核对 `selected_candidate_id` 确实来自选刊证据的短名单，且不在未知或失败硬门列表中。
2. 核对两个文件的 `manuscript_id`、`manuscript_revision`、`target_journal`、`article_type` 和 `section_or_collection` 一致，并与当前稿件一致。
3. 核对两个头部、合同第 11 节唯一的 `contract_author_decision` 以及第 12 节交接块的 `blocking_issues` 均为空；作者确认日期与头部一致，且 `contract_status`、`author_confirmation` 均为已确认。任一不满足即标记 `contract-pending`，不应用目标期刊规则。
4. 沿 `decision_file`、`selection_evidence_file`、`journal_profile_file` 和 `field_blueprint_file` 检查文件存在、可读且引用方向一致；分别重算决策、选刊证据、期刊画像和领域蓝图 SHA-256，并与各自绑定字段比对。
5. 核对决策 `evidence_version` 与契约 `selection_evidence_version` 一致，三份画像/契约的 `writing_profile_evidence_id` 一致；这两个命名空间不相互替代。
6. 核对 `requires_recheck_before_submission: true`；本阶段的接收不替代投稿前重新核验。
7. 只保存原文件路径、关键版本、接收时间和合同指纹，不复制合同正文到本 Skill 的台账。

输出：

```text
期刊合同状态：venue-unselected / venue-pending（仅 paperline 授权旁路） / contract-pending / contract-confirmed
目标期刊：
稿件ID与修订版：
合同版本：
选刊证据版本 / 双轨画像证据ID：
决策文件 SHA-256：
决定/画像/蓝图/证据文件：
阻塞项：
合同指纹：
未应用规则及原因：
```

## 应用边界

- 仅从已验证引用文件读取当前任务需要的规则，不把上游文件全文载入或转存。
- 将有官方证据的硬要求应用到明确受其约束的章节、声明、图表或篇幅检查。
- 将经验性指导保留为建议，不把它升级为硬门，也不模仿期刊论文中的常见措辞。
- 遇到删减证据、改变主张强度、重排贡献、隐去局限或新增科学解释的要求时，触发作者确认边界。
- 合同不能覆盖主张—证据—边界规则，也不能把尚未完成的分析写成结果。

## 期刊或合同变化

比较旧、新合同的目标期刊、稿件修订版、`contract_version`、`selection_evidence_version`、`writing_profile_evidence_id`、`decision_sha256`、`last_verified_at` 和受影响规则：

| 变化 | 必须动作 | 状态影响 |
| --- | --- | --- |
| 仅证据快照变化，规则语义不变 | 更新来源引用并复核受影响硬门 | 通过复核前撤销相应期刊合规声明 |
| 机械格式或语言规则变化 | 使对应适配层失效并重新检查 | 保留中文内容状态；适配状态回退 |
| 篇幅、章节结构或必备内容变化 | 标出受影响章节并重建蓝图 | 相关章节最多保留到 `S2`，重新写作与核验 |
| 披露、方法或结果报告要求变化 | 检查缺失材料和证据 | 按缺口回退相关章节并添加相应阻塞标记 |
| 目标期刊身份变化 | 废止全部旧期刊适配声明，重新接收合同 | 保留通用中文基线；整合稿不沿用旧 `S7` |

不要机械降低所有章节状态。只回退受影响章节，并记录旧状态、触发变化、保留证据、新状态和恢复条件。作者对旧稿件—旧合同组合的 `S7` 锁定仍是历史事实，但不能覆盖新合同下的整合稿；新整合稿必须重新通过相关门并由作者再次锁定。

## 交接记录

在中文定稿包中只附加引用与版本信息：

```text
目标期刊状态：
目标期刊决定文件：
目标期刊写作合同文件：
合同版本与指纹：
选刊证据版本 / 双轨画像证据ID：
决策文件 SHA-256：
合同适用稿件ID与修订版：
期刊规则影响的章节：
仍为 venue-unselected 或 paperline venue-pending 的事项：
合同变更与回退记录：
```

没有已确认合同时，单独写作保留 `venue-unselected`；只有正式记录旁路授权的 `paperline` 项目才保留 `venue-pending`。不要创建伪版本号或声称已由期刊筛选 Skill 核验。
