# 跨期刊筛选规则

本模式回答“哪些期刊符合作者约束、各自取舍是什么、作者最终选哪本”。它不分析论文样本的章节用途，因此禁止使用写作画像的 `J/R/E/U`。

## 目录

1. 输入合同
2. 硬门
3. 软偏好
4. 候选与来源 ID
5. 固定产物
6. 作者最终选择

## 1. 输入合同

至少登记：

| 类别 | 字段 |
| --- | --- |
| 研究快照 | 论文类型、对象、问题、方法、关键结果、贡献、成熟度 |
| 硬约束 | 必须收录、范围、可接受论文类型、费用上限、语言、截止时间、机构政策 |
| 软偏好 | 读者匹配、影响力、速度、OA、费用、地域、学术或工程侧重 |
| 决策权 | 作者、共同作者、导师或机构；谁能最终确认 |

不知道的字段写 `unknown`，并说明它是否阻塞。用户未提供 APC 上限时，不得自行假定“越低越好”是硬门。

## 2. 硬门

每个候选使用同一张表，结果只允许 `pass / fail / unknown / not_applicable`。

| 硬门 ID | 核验问题 | 主要证据 |
| --- | --- | --- |
| G1 | 期刊范围是否明确覆盖研究问题和贡献类型 | 官方 aims & scope、栏目页 |
| G2 | 是否接收当前论文类型 | 官方 article types、作者指南 |
| G3 | 作者要求的收录状态是否满足 | 指定索引数据库官方记录 |
| G4 | OA/APC 或版面费是否在硬上限内 | 官方费用页；未知附加费单列 |
| G5 | 语言、长度、图表或数据政策是否存在不可满足项 | 官方作者指南和政策页 |
| G6 | 时间、专题截止或投稿状态是否满足 | 官方征稿/投稿系统状态 |
| G7 | 伦理、数据、代码或利益冲突要求是否可满足 | 官方伦理与数据政策 |
| G8 | 是否存在撤刊、停刊、异常警示或身份混淆风险 | 出版社与索引官方记录 |

纪律：`fail` 立即淘汰；`unknown` 不进入可确认短名单，只进入待核验表。不得用软偏好高分覆盖硬门失败或未知。

硬门状态必须同时写入 frontmatter 的结构化候选列表，不得依赖正文中的“无”“全部通过”等措辞：

- `shortlist_candidate_ids`：所有硬门均为 `pass/not_applicable` 的短名单候选；
- `unknown_hard_gate_candidates`：至少一个硬门为 `unknown` 的候选；
- `failed_hard_gate_candidates`：至少一个硬门为 `fail` 的候选。

三个字段使用 JSON 兼容的 YAML 行内列表，例如 `["CAND-001"]` 或 `[]`。三个集合不得冲突；短名单不得包含 unknown 或 failed 候选。正文表格负责解释逐项 G1—G8 证据，frontmatter 列表负责机械交接。

正式产物的 frontmatter 不允许任何重复键；重复字段会使整个产物无效，不能依赖“后一行覆盖前一行”的解析行为。

## 3. 软偏好

只对全部硬门为 `pass/not_applicable` 的候选评分。默认 0—5 分，但权重由作者确认；若作者拒绝赋权，使用等权并标记为“可替换默认值”。

| 偏好 ID | 维度 | 评分依据 |
| --- | --- | --- |
| S1 | 主题与贡献匹配 | 官方范围、近期同类型论文 |
| S2 | 目标读者匹配 | 编辑定位、栏目和论文主题分布 |
| S3 | 方法与证据形态兼容 | 近期同类型全文；不是仅看题名 |
| S4 | 学术/工程定位匹配 | 官方定位与多篇近期样本 |
| S5 | 费用与开放获取偏好 | 官方费用和许可政策 |
| S6 | 时间偏好 | 官方公布统计优先；第三方经验降级 |
| S7 | 作者战略偏好 | 团队、基金、机构或职业目标 |

可计算 `weighted_preference = Σ(weight × score) / Σweight`，但必须同时展示原始维度、权重、证据和未知项。该分数只用于短名单排序，不代表论文质量、录用概率或期刊绝对优劣。

## 4. 候选与来源 ID

- 候选：`CAND-001`、`CAND-002`。
- 官方来源：`OFF-001`；索引记录：`IDX-001`；正式文章：`ART-001`；作者约束：`USR-001`；二手线索：`SEC-001`。
- 来源 ID 在同一次筛选中稳定；淘汰后保留编号和理由。

## 5. 固定产物

完整候选表、硬门、软偏好、来源卡和排除日志保存为 `journal-selection-evidence.md`：

```yaml
---
artifact_type: "journal_selection_evidence"
schema_version: "1.0"
evidence_version: "<稳定证据版本>"
manuscript_id: "<稿件 ID>"
manuscript_revision: "<稿件修订号>"
generated_at: "YYYY-MM-DD"
last_verified_at: "YYYY-MM-DD"
shortlist_candidate_ids: ["CAND-001"]
unknown_hard_gate_candidates: []
failed_hard_gate_candidates: ["CAND-002"]
---
```

固定正文标题：

```text
## 1. 研究快照与作者约束
## 2. 证据来源与核验日期
## 3. 硬门结果
## 4. 软偏好、权重与评分理由
## 5. 淘汰与待核验候选
## 6. 短名单及取舍
## 7. 推荐次序与适用条件
```

confirmed 决策要求 `unknown_hard_gate_candidates: []`，且所选候选属于 `shortlist_candidate_ids`、不属于 `failed_hard_gate_candidates`。正文中的自然语言总结不参与该机械判断。正式决策固定命名为 `target-journal-decision.md`：

```yaml
---
artifact_type: "target_journal_decision"
schema_version: "1.0"
status: "confirmed"
manuscript_id: "<稿件 ID>"
manuscript_revision: "<稿件修订号>"
target_journal: "<作者选定期刊>"
article_type: "<论文类型>"
section_or_collection: "<栏目或 none>"
evidence_version: "<与证据文件一致>"
last_verified_at: "YYYY-MM-DD"
author_confirmed_at: "YYYY-MM-DD"
selected_candidate_id: "CAND-001"
selection_evidence_file: "./journal-selection-evidence.md"
selection_evidence_sha256: "<选刊证据确切字节的 64 位小写 SHA-256>"
blocking_issues: []
---
```

决策正文固定包含：`## 1. 选定期刊与论文类型`、`## 2. 硬门结论`、`## 3. 软偏好与取舍`、`## 4. 作者确认`、`## 5. 写作画像交接块`。第 4 节必须包含与头部一致的结构化确认块：

```yaml
author_decision:
  status: confirmed
  confirmed_at: "YYYY-MM-DD"
```

`selected_candidate_id` 必须与作者最终选择一致，并属于证据文件的结构化短名单；`selection_evidence_sha256` 必须绑定该证据文件的确切字节，不能只靠可复用的版本名。决策还必须至少引用一个候选 ID 和一个官方期刊/出版社或权威索引来源 ID（`OFF-###` 或 `IDX-###`）。`USR-###`、`ART-###` 或 `SEC-###` 可以补充决策，但不能单独证明期刊硬门。

## 6. 作者最终选择

推荐可以写“首选、备选及适用条件”，但最终选择必须由有决策权的人确认。作者选择不等于分数最高：作者可以基于未量化的合作、时点或战略原因改选，只需在决策文件中记录理由，不要篡改证据文件中的原评分。
