# 契约、确认门与交接

正式产物使用可确定解析的 Markdown + 扁平 YAML 规范子集：起止分隔符必须各自独占一行；YAML 字段名只能使用未加引号的英文字母、数字和下划线，冒号前不得留空格，标量引号必须同种且成对闭合，且不使用反斜线转义。自由文本、路径、日期、版本、数字以及 YAML 隐式类型值必须加成对引号；未加引号时只允许校验器按字段明确列出的机器字面量（当前为确认状态的 `confirmed` 和重检开关的 `true`），不再接受通用简单 token。只有候选列表、阻塞项和文档明确列出的列表提示字段可使用严格 JSON 行内数组/对象；其中数字必须解析为有限值，`1e999` 这类会溢出为无穷的表示拒绝。结构块字段必须紧随标记、连续书写并恰好缩进两个空格。重复字段、未知缩进语法均拒绝。正文二级标题只能使用本合同列出的固定写法且必须唯一；额外或 CommonMark 等价的非规范 H2、Setext 标题和横线分隔符均拒绝。fenced code block、HTML 注释、原始 HTML 块、制表符和不可见链接引用定义不得承载或包裹正式章节、来源、确认块或交接块。该限制用于保证生产校验器与下游消费者不会对同一文件产生不同解释。

## 目录

1. 选刊到画像
2. 双轨融合契约
3. confirmed 质量门
4. Paper Navigator 交接块
5. 变更与回退

## 1. 选刊到画像

模式一固定产物为 `journal-selection-evidence.md` 和 `target-journal-decision.md`。只有以下条件同时满足时才进入模式二：

- `status: confirmed`；
- `unknown_hard_gate_candidates: []`；
- `selected_candidate_id` 属于 `shortlist_candidate_ids`，且不属于 `failed_hard_gate_candidates`；
- 作者最终选择已确认；
- 选定期刊、论文类型、栏目或 `none` 明确；
- 校验器通过。

作者直接指定期刊时仍生成简化版证据和决策文件：候选池可以只有一本，软偏好可以标为不适用，但必须核验期刊身份、范围、论文类型和作者确认。此时结构化短名单包含该候选，unknown 与 failed 列表均为空。这样下游始终只接收一个稳定决策接口。

## 2. 双轨融合契约

正式文件固定命名 `target-journal-writing-contract.md`，YAML 头部：

```yaml
---
contract_version: "2.0"
artifact_type: "target_journal_writing_contract"
contract_id: "<稳定 ID>"
status: "draft | pending_confirmation | confirmed"
manuscript_id: "<稿件 ID>"
manuscript_revision: "<稿件修订号>"
target_journal: "<期刊名>"
article_type: "<论文类型>"
section_or_collection: "<栏目或 none>"
research_field: "<领域>"
generated_at: "YYYY-MM-DD"
last_verified_at: "YYYY-MM-DD"
author_confirmed_at: "YYYY-MM-DD 或 pending"
selection_evidence_version: "<与 target-journal-decision.md 一致>"
writing_profile_evidence_id: "<双轨画像共享证据 ID>"
decision_file: "<target-journal-decision.md 相对路径>"
decision_sha256: "<决策文件确切字节的 64 位小写 SHA-256>"
journal_profile_file: "./journal-writing-profile.md"
journal_profile_sha256: "<期刊画像确切字节的 64 位小写 SHA-256>"
field_blueprint_file: "./field-writing-blueprint.md"
field_blueprint_sha256: "<领域蓝图确切字节的 64 位小写 SHA-256>"
requires_recheck_before_submission: true
blocking_issues: []
---
```

固定正文：

```text
## 1. 目标定义与选择依据
## 2. 双轨来源与可信度摘要
## 3. 编辑侧重点与贡献排序
## 4. 全文架构与篇幅预算
## 5. 章节写作合同
## 6. 图表与补充材料合同
## 7. 语言、术语与语气
## 8. 证据门槛
## 9. 禁止事项
## 10. 融合决策与冲突裁决
## 11. 作者确认
## 12. Paper Navigator 交接块
```

第 5 节逐章覆盖摘要、引言、相关工作/背景、方法、结果、讨论和结论。每章至少说明：职责、段落/论证顺序、`JP/FB/FR` 规则、必须包含、证据门槛、图表接口、篇幅、不可迁移项和不采用风险。

第 11 节不使用自由散文充当确认状态，必须且只能包含一个结构化块，并与头部一致：

```yaml
contract_author_decision:
  status: confirmed
  confirmed_at: "YYYY-MM-DD"
  blocking_issues: []
```

## 3. confirmed 质量门

- 三份产物存在并共享 `writing_profile_evidence_id`；
- 契约中的 `journal_profile_sha256` 与 `field_blueprint_sha256` 分别绑定两份画像的确切字节；
- 契约的 `selection_evidence_version` 与决策文件一致，`decision_sha256` 与决策文件确切字节一致；
- O/A/B/C/D 分类和 J/R/E/U 理由可追溯；
- 官方硬要求与样本观察分开；
- 所有必需章节有合同；
- 每条高影响融合决定说明来源、章节用途、迁移边界和不采用风险；
- 作者已确认目标期刊、论文类型和高影响冲突；
- 第 11 节 `contract_author_decision` 为 confirmed、日期与头部一致且阻塞项为空；
- 交接块 `contract_status: confirmed`、`author_confirmation: confirmed`、`blocking_issues: []`；
- 校验器成功。

## 4. Paper Navigator 交接块

机器必需字段只有以下八项：`contract_status`、`author_confirmation`、`target_journal`、`article_type`、`selection_evidence_version`、`writing_profile_evidence_id`、`decision_sha256` 和 `blocking_issues`。校验器要求它们与头部一致且无重复键。

下面示例中的 `priority_focus`、`required_sections`、各类 `*_source`、`unresolved_nonblocking` 是可选的路由提示；提供时应指向本契约的真实章节或链接文件，但缺少它们不使身份与确认门失效。`paper-navigator` 可以直接从已验证契约正文读取这些内容，不得把可选提示当作新的规则来源。

```yaml
paper_navigator_handoff:
  contract_status: "confirmed"
  author_confirmation: "confirmed"
  target_journal: "期刊名"
  article_type: "论文类型"
  selection_evidence_version: "选刊证据版本"
  writing_profile_evidence_id: "双轨画像证据 ID"
  decision_sha256: "决策文件 SHA-256"
  priority_focus: ["重点一", "重点二"]
  required_sections: ["摘要", "引言", "方法", "结果", "讨论", "结论"]
  journal_profile_source: "./journal-writing-profile.md"
  field_blueprint_source: "./field-writing-blueprint.md"
  section_budget_source: "第4节"
  evidence_gate_source: "第8节"
  terminology_source: "第7节"
  fusion_decision_source: "第10节"
  unresolved_nonblocking: []
  blocking_issues: []
```

交接成功只表示 `paper-navigator` 可以按已确认契约开始或调整中文写作，不表示中文稿定稿、英文稿完成或投稿完成。

## 5. 变更与回退

| 变化 | 回退动作 |
| --- | --- |
| 作者改选期刊/论文类型 | 重新运行画像两轨和全部融合规则 |
| 范围、费用、收录或政策变化 | 回退选刊相关硬门；必要时重新选择 |
| 对象、问题、方法或输出变化 | 重算相关度、用途和受影响章节合同 |
| 新增核心来源 | 更新来源卡、规则分母、冲突与置信度 |
| 仅核验日期变化 | 复核受影响字段；事实未变则不重写全文 |

任何变更导致阻塞项重现时，把状态退回 `pending_confirmation`，不要保留虚假的 confirmed。
