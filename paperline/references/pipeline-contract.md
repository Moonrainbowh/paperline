# Paperline 流程与交接合同

本文件只定义编排层合同。章节怎么写、期刊怎么筛、论文怎么翻译，分别由对应专业 Skill 决定。

## 目录

1. 状态枚举
2. 固定阶段与依赖
3. 状态文件最小结构
4. 阶段产物与通用交接外壳
5. `venue-pending` 旁路
6. 失效传播
7. 恢复算法

## 1. 状态枚举

每个阶段只能处于以下状态之一：

| 状态 | 含义 |
| --- | --- |
| `pending` | 尚未开始，或上游失效后等待重做 |
| `active` | 当前唯一正在执行的阶段 |
| `waiting-human` | 只能由作者选择或确认后继续 |
| `blocked` | 缺少材料、权限或外部条件，当前无法安全推进 |
| `complete` | 产物已生成、哈希已记录且没有未解决的失效标记 |

全流程最多有一个 `active`。`waiting-human` 与 `blocked` 必须在 `blocked_by` 中说明原因。`complete` 必须有 `output`，且 `blocked_by` 和 `invalidated_by` 都为空。

期刊顶层状态只使用：

| `venue.mode` | 含义 | 与专业 Skill 的映射 |
| --- | --- | --- |
| `unselected` | 正常尚未完成 P2，不授权跳过 | `paper-navigator: venue-unselected` |
| `venue-pending` | 作者已明确授权先写通用中文稿 | 仅 `paperline` 旁路，必须有 `bypass` 记录 |
| `locked` | 决策与写作契约已确认并绑定 | `paper-navigator: contract-confirmed` |

`journal-navigator` 产物内的 `draft / pending_confirmation / confirmed` 是文件状态；翻译 payload 的 `contract-confirmed` 是 `locked` 模式下的交接声明。不得用这些词互相代替。

`venue.mode` 与 P2 `journal-contract` 状态双向绑定：`unselected` 和 `venue-pending` 都禁止 P2 为 `complete`；`locked` 必须且只表示 P2 已经 `complete`，不能只填写 venue 字段而保留未完成的期刊合同阶段。

## 2. 固定阶段与依赖

```text
chinese-evidence-profile
  → journal-contract
  → chinese-finalization
  → english-translation
  → pre-submission-check
```

阶段依赖如下：

| 阶段 | 必须消费的有效上游 |
| --- | --- |
| `chinese-evidence-profile` | 无 |
| `journal-contract` | `chinese-evidence-profile` |
| `chinese-finalization` | `chinese-evidence-profile`、`journal-contract`；`venue-pending` 旁路时可暂缺后者 |
| `english-translation` | 已锁定的 `journal-contract`、按该合同重新确认的中文 S7 |
| `pre-submission-check` | `journal-contract`、`chinese-finalization`、`english-translation` |

`input_versions` 必须记录当前产物实际消费的上游 `revision`。只要实际版本与记录不一致，就视为过期。

`journal-contract` 的正式产物固定为 `target-journal-decision.md` 和 `target-journal-writing-contract.md`。两者都必须满足：`status=confirmed`，包含一致的 `manuscript_id`、`manuscript_revision`、`target_journal` 和 `article_type`，记录证据来源、版本与核验日期，并且 `blocking_issues=[]`。编排层只记录两个文件的版本和哈希，不复制其中的期刊规则。

## 3. 状态文件最小结构

建议文件名为 `pipeline-state.json`：

状态文件按严格 JSON 解析：任意层级都不得有重复键，也不得使用 `NaN`、`Infinity`、`-Infinity`，或 `1e999` 这类会在运行时溢出为非有限值的数词。

```json
{
  "schema_version": "1.0",
  "pipeline_id": "paper-2026-001",
  "manuscript_id": "paper-2026-001",
  "manuscript_revision": "r1",
  "revision": 1,
  "current_stage": "chinese-evidence-profile",
  "venue": {
    "mode": "unselected",
    "target_journal": null,
    "article_type": null,
    "decision_path": null,
    "decision_schema_version": null,
    "decision_hash": null,
    "contract_path": null,
    "contract_version": null,
    "contract_hash": null,
    "selection_evidence_version": null,
    "writing_profile_evidence_id": null,
    "bypass": null
  },
  "stages": {
    "chinese-evidence-profile": {
      "status": "active",
      "revision": 0,
      "input_versions": {},
      "output": null,
      "blocked_by": [],
      "invalidated_by": []
    }
  },
  "handoffs": []
}
```

实际文件必须包含全部五个阶段。尚未完成的阶段使用同样字段，`output` 为 `null`。`unselected` 表示正常流程尚未选定期刊；它不代表作者已经允许跳过 P2。

## 4. 阶段产物与通用交接外壳

完成阶段的 `output` 使用：

```json
{
  "artifact_id": "paper-2026-001-cn-s7",
  "artifact_type": "chinese-manuscript-s7",
  "path": "artifacts/manuscript-cn-s7.docx",
  "version": "r1",
  "sha256": "64位小写十六进制SHA-256"
}
```

P4 与 P5 不得使用 `stage-4-output` 一类无语义占位名。它们的产物类型和 schema 固定为：

| 阶段 | `artifact_type` | `artifact_schema_version` |
| --- | --- | --- |
| P4 `english-translation` | `english-translation-package` | `1.0` |
| P5 `pre-submission-check` | `pre-submission-check-report` | `1.0` |

这里的 `artifact_schema_version` 描述产物结构，`version` 描述该产物实例的修订版本；两者不得混用。

P3 另外保存 `content_state`，区分通用中文基线与期刊整合状态：

```json
{
  "generic_chinese_status": "S7",
  "journal_adaptation_status": "contract-applied",
  "author_lock_binding": {
    "lock_id": "author-lock-001",
    "status": "locked",
    "confirmed_by": "author-001",
    "confirmed_at": "2026-08-10T12:40:00+08:00",
    "manuscript_id": "paper-2026-001",
    "manuscript_revision": "r1",
    "manuscript_sha256": "64位小写十六进制SHA-256",
    "contract_version": "2.0",
    "contract_sha256": "64位小写十六进制SHA-256"
  },
  "affected_sections": []
}
```

期刊改变时，P3 的“期刊整合产物”回到 `pending`，但 `generic_chinese_status` 和旧 `author_lock_binding` 作为历史保留；旧绑定不能授权新契约下的英译。

专业 Skill 之间传递信息时统一包在以下外壳中；`payload` 内容由发送方专业 Skill 定义，编排层不复制其内部方法：

```json
{
  "handoff_id": "h-004",
  "from_stage": "chinese-finalization",
  "to_stage": "english-translation",
  "from_skill": "paper-navigator",
  "to_skill": "zh-en-paper-translator",
  "created_at": "2026-08-10T12:45:00+08:00",
  "source_artifacts": [
    {
      "artifact_id": "paper-2026-001-cn-s7",
      "artifact_type": "chinese-manuscript-s7",
      "path": "artifacts/manuscript-cn-s7.docx",
      "version": "r1",
      "sha256": "64位小写十六进制SHA-256"
    }
  ],
  "payload": {},
  "author_decisions": ["author-lock-001"],
  "open_questions": [],
  "blockers": []
}
```

三条正式交接的 Skill 映射固定为：P2→P3 `journal-navigator → paper-navigator`、P3→P4 `paper-navigator → zh-en-paper-translator`、P4→P5 `zh-en-paper-translator → paperline`。`created_at` 与作者锁定时间都必须是带 UTC 偏移的 ISO-8601 时间，且按该时间自身 UTC 偏移计算的本地日期不得晚于校验当天；相关事件存在时，时序必须满足 `P2→P3.created_at ≤ P3 author_lock.confirmed_at ≤ P3→P4.created_at ≤ P4→P5.created_at`。时序链中的 P3 作者锁只指当前 `complete + contract-applied` 且 `contract_sha256` 等于当前 venue 合同哈希的有效锁；失效回退时保留的旧历史锁不进入新链。

P2→P3 的 `source_artifacts` 必须分别引用 `target-journal-decision.md` 和 `target-journal-writing-contract.md`，不能用编排层自行概括的期刊规则代替。例如：

```json
[
  {
    "artifact_id": "paper-2026-001-journal-decision-r1",
    "artifact_type": "target_journal_decision",
    "path": "target-journal-decision.md",
    "version": "1.0",
    "sha256": "64位小写十六进制SHA-256"
  },
  {
    "artifact_id": "paper-2026-001-journal-contract-r1",
    "artifact_type": "target_journal_writing_contract",
    "path": "target-journal-writing-contract.md",
    "version": "2.0",
    "sha256": "64位小写十六进制SHA-256"
  }
]
```

P3→P4 必须是正式全稿翻译交接。`source_artifacts` 引用当前 P3 的确切 `chinese-manuscript-s7` 产物，`payload` 至少包含：

```text
handoff_type: formal-full-manuscript-translation
handoff_package_schema_version: "1.0"
handoff_status: locked
chinese_manuscript_status: S7
manuscript_id:
manuscript_revision:
chinese_manuscript_sha256:
author_lock_record:
  lock_id:
  status: locked
  confirmed_by:
  confirmed_at:
  manuscript_id:
  manuscript_revision:
  manuscript_sha256:
locked_thesis_and_contributions:
terminology_ledger:
locked_numbers_and_units:
locked_claim_boundaries:
locked_citations_and_cross_references:
unresolved_blockers: []
target_journal_status: contract-confirmed
target_journal:
target_journal_article_type:
target_journal_decision_file:
target_journal_decision_schema_version:
target_journal_decision_sha256:
target_journal_contract_file:
target_journal_contract_version:
target_journal_contract_sha256:
target_journal_selection_evidence_version:
target_journal_writing_profile_evidence_id:
```

`author_lock_record` 必须是上述七个精确键组成的对象。其 `lock_id` 必须同时出现在交接外壳的 `author_decisions` 中，并与当前 P3 `content_state.author_lock_binding` 的锁定 ID、确认者、确认时间、稿件 ID、修订和 SHA-256 一致。

以下五个锁定台账字段采用同一个联合类型：`locked_thesis_and_contributions`、`terminology_ledger`、`locked_numbers_and_units`、`locked_claim_boundaries`、`locked_citations_and_cross_references`。每个字段只能是二者之一：

```json
{"inline": "非空字符串、数组或对象"}
```

```json
{"path": "artifacts/ledger.json", "sha256": "64位小写十六进制SHA-256"}
```

键集合必须精确匹配，不能混用 `inline` 与文件引用，也不能添加 `format` 等旁路键。编排器只验证联合类型形态；引用文件的存在性与字节哈希由 translator 的 `--verify-files` 验证。对不适用项也要在 `inline` 中显式记录作者确认的 `not_applicable`，不能删掉字段。这一交接只授权忠实英译，不授权改变主张、结构或证据。

P4→P5 必须使用正式交接，且 `source_artifacts` 必须只包含当前 P4 `output` 的精确副本，包括 `artifact_schema_version`：

```json
{
  "handoff_type": "formal-pre-submission-check",
  "handoff_package_schema_version": "1.0",
  "handoff_status": "locked",
  "manuscript_id": "paper-2026-001",
  "manuscript_revision": "r1",
  "chinese_manuscript_sha256": "64位小写十六进制SHA-256",
  "author_lock_id": "author-lock-001",
  "english_translation_artifact_id": "paper-2026-001-en-r1",
  "english_translation_artifact_type": "english-translation-package",
  "english_translation_artifact_schema_version": "1.0",
  "english_translation_version": "r1-en1",
  "english_translation_sha256": "64位小写十六进制SHA-256",
  "target_journal_contract_sha256": "64位小写十六进制SHA-256",
  "unresolved_blockers": []
}
```

P5 为 `active`、`waiting-human` 或 `complete` 前都必须存在该交接。交接中的作者锁、中文稿、期刊合同和英文产物标识必须分别匹配当前 P3、venue 与 P4 状态。

哈希针对交接时读取到的确切文件字节计算。正文变了但文件名没变，也必须提升阶段 `revision`、更新产物版本和哈希，并重新生成交接包。

## 5. `venue-pending` 旁路

启用旁路必须满足：

1. `venue.mode` 为 `venue-pending`；
2. `target_journal`、`article_type`、决策/契约路径、版本、哈希和两类证据标识均为 `null`；
3. `bypass` 只能包含 `authorized_at`、`reason`、`resume_stage`、`baseline_stage_revisions` 和 `invalidate_on_lock` 五个键；
4. `authorized_at` 是带 UTC 偏移且本地日期不晚于校验当天的 ISO-8601 时间，`reason` 是非空字符串，`resume_stage` 固定为 `journal-contract`；
5. `journal-contract` 可以保持 `pending` 或 `waiting-human`，但不能为 `complete`；
6. 旁路中的 P3 最多推进到中文 S6，不得标记 P3 `complete`、不得声明 `S7`/`chinese-manuscript-s7`，也不得保存结构化作者锁；
7. 不得激活或完成 `english-translation` 和 `pre-submission-check`。

`baseline_stage_revisions` 必须且只能包含 `chinese-finalization`、`english-translation`、`pre-submission-check` 三个键，每个值都是非负整数。建立旁路时必须精确复制三个阶段当时的 `revision`，之后基线保持不变：P3 写作推进时允许当前修订大于或等于基线，禁止推进的 P4/P5 当前修订必须始终等于各自基线。`invalidate_on_lock` 必须且只能各包含一次上述三个阶段，不得重复或加入 P2 等其他阶段。

锁定期刊时：

1. 保存新的期刊决策/合同路径、版本、哈希和两类证据标识，把 `venue.mode` 改为 `locked`；
2. 对比旁路基线，给 P3/P4/P5 添加 `invalidated_by` 记录；
3. 保留旧产物、通用中文基线和旧锁定记录，但把受影响的期刊整合阶段重置为 `pending`；
4. 从 `chinese-finalization` 恢复，应用合同并重新取得中文 S6/S7；
5. 生成新的 P3→P4 交接后才能开始英译。

## 6. 失效传播

按最早发生的变化向下传播：

| 变化 | 至少失效 |
| --- | --- |
| 主旨、贡献排序、决定性证据或研究边界改变 | P2、P3、P4、P5 |
| 目标期刊或期刊硬规则改变 | P3、P4、P5 |
| 中文 S7 正文、数字、图表、引用或术语改变 | P4、P5 |
| 英文正文、术语或文档结构改变 | P5 |
| 仅投稿清单或声明改变 | P5 中对应检查项 |

传播时不要删除文件。对每个受影响阶段：

1. 记录 `invalidated_by`，至少包含上游阶段和新旧版本；
2. 把状态设为 `pending`；
3. 保留历史 `output` 用于审计，但不得把它作为有效交接源；
4. 删除或作废引用旧哈希的未执行交接；
5. 将 `current_stage` 指向最早失效阶段。

## 7. 恢复算法

每次恢复按以下顺序执行：

1. 运行状态校验脚本，先修复结构错误。
2. 使用 `--verify-files` 按阶段顺序重算现存产物及交接来源 SHA-256，并与状态文件比较。
3. 检查 `input_versions` 是否仍等于有效上游 `revision`。
4. 从第一个哈希不符、输入版本过期、存在 `invalidated_by` 或非 `complete` 的阶段恢复。
5. 将该阶段设为唯一 `active`；需要作者选择时改为 `waiting-human`。
6. 把其后的阶段标为 `pending`，保留历史和失效原因。
7. 生成新产物后递增阶段及顶层 `revision`，记录新哈希，再生成交接包。

不带 `--verify-files` 时，脚本只报告 `STRUCTURALLY_VALID`，不得据此推进阶段。带该参数时还会核验状态文件相对路径下的实际文件哈希；但作者确认真实性、科学证据、期刊网页时效及文本语义仍需由相应专业流程核验。
