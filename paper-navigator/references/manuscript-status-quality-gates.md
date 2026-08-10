# 章节状态与中文定稿质量门

用于区分材料准备、初稿、核验、中文定稿和作者锁定。硬性阻塞项不能被语言评分或综合分数抵消。

## 目录

1. 章节状态
2. 独立阻塞标记
3. 全文中文定稿硬门
4. 质量门执行记录
5. 定稿判定
6. 交接包

## 章节状态

| 状态 | 定义 | 允许存在 | 不允许宣称 |
| --- | --- | --- | --- |
| `S0 输入不足` | 核心主张、证据或边界缺失，不能安全写作 | 缺口表、占位脚手架 | 章节初稿完成 |
| `S1 材料就绪` | 数据、图表、文献、主张和缺口已盘点 | 待作者选择的叙事方案 | 已形成章节结构 |
| `S2 结构已确认` | 当前版本的主旨、贡献取舍、段落蓝图和核心术语等写作所需科学选择已经作者确认 | 显式待核证据 | 文字已定稿或最终版本已锁定 |
| `S3 中文初稿完成` | 已形成完整中文文字 | 显式待核项、局部表达问题 | 证据或逻辑已通过 |
| `S4 证据核验通过` | 实质主张、数字、引用和来源已经核对 | 局部结构和表达问题 | 逻辑定稿 |
| `S5 逻辑定稿` | 反向提纲、段落顺序、主张强度和边界稳定 | 局部中文表达修改 | 中文文字定稿 |
| `S6 中文文字定稿` | 除最终版本锁定外的全部硬门通过；写作所需科学选择均已确认，无占位符，术语、数字、表达和章节职责稳定 | 最终版本确认、准备待锁定交接包 | 作者已对完整最终版本作锁定或可正式启动英译 |
| `S7 作者确认锁定` | 作者审阅确切的 S6 稿件并明确锁定该版本的主旨、创新排序、关键解释、局限和外推边界 | 英文转换、期刊适配、投稿准备 | 已投稿或已接受 |

AI 可以依据证据判定到 `S6`，不得自行标记 `S7`。

## 独立阻塞标记

- `evidence-blocked`：关键主张缺少直接证据。
- `author-decision-blocked`：`research-context-passport.md` 的“写作中的科学选择”仍有未决项；作者确认该项后可清除，但不因此自动达到 S7。
- `analysis-blocked`：需要新实验、统计、重算或验证路线确认。
- `source-blocked`：关键文献或原始材料尚未获得/核验。
- `venue-unselected`：目标期刊规则尚未确认；不阻塞通用中文稿，但阻塞期刊适配。`paperline` 中的 `venue-pending` 特指已记录作者授权的选刊旁路，不与本地普通未选刊状态混用。

阻塞标记必须单独展示，不能用“总体良好”或高分覆盖。

## 全文中文定稿硬门

| 质量门 | 硬性通过条件 | 典型阻塞 |
| --- | --- | --- |
| 完整性门 | 所有必要章节完成，无TBD、待补、占位符或隐藏空节 | 缺章节、图表未解释、引用占位 |
| 主旨与贡献门 | 一句话主旨稳定，每项贡献有动作、新增能力、证据和边界 | 创新只是功能列表、贡献无证据 |
| 主张—证据门 | 每项核心主张有直接证据、来源和适用边界 | 只有间接文献或语言推断 |
| 方法有效性门 | 数据、设计、基线、指标、参数和排除足以评估有效性 | 泄漏、选择偏差、不公平比较、方法缺失 |
| 章节职责门 | 结果不写长推测，讨论不新增结果，结论不新增主张 | 信息放错章节 |
| 反向提纲门 | 一段一义，主题句序列形成连续论证 | 重复段、孤立段、双任务段 |
| 跨章节门 | 主张合同闭环，无未兑现贡献、方法/结果孤儿和范围漂移 | 摘要、引言、正文相互矛盾 |
| 数据一致门 | 数字、单位、样本、指标、图表、正文和比较对象一致 | 抄录错误、不同版本混用 |
| 术语一致门 | 术语、缩写、符号、方法和贡献名称使用锁定写法 | 同义词漂移、符号复用 |
| 解释边界门 | 因果、机制、推广、创新和工程应用措辞不超出证据 | 相关写成因果、局部写成普遍 |
| 局限性门 | 真实局限、影响方向、受影响主张和未验证范围明确 | 通用免责声明或隐瞒失败条件 |
| 引用门 | 引文支持相邻原子主张，元数据和来源状态可核验 | 只看标题、二手转引、来源冲突 |
| 中文表达门 | 主谓明确、指代清楚、逻辑显式，无堆叠长定语和空泛宣传 | 流畅但命题不清、AI套话 |
| 作者科学决定门 | `research-context-passport.md` 的五项科学选择均有作者决定记录，且与当前稿件一致 | AI替作者选择主旨、解释或边界 |

作者对**完整 S6 稿件的最终版本锁定**不是 S6 硬门，而是从 S6 进入 S7 的单独动作，不能与“作者科学决定门”混用。

## 质量门执行记录

| 门 | 状态 | 检查证据 | 问题 | 修复动作 | 责任人/决策者 |
| --- | --- | --- | --- | --- | --- |

状态只使用：

- `pass`：证据表明已通过。
- `fail`：存在明确违反项。
- `blocked`：缺少材料、授权或作者决定，当前不能判断。
- `not-applicable`：说明为何不适用。

不得使用没有证据的“基本通过”。

## 定稿判定

只有满足以下条件才能标记 `S6 中文文字定稿`：

1. 所有必要章节至少达到 `S5`，全文整合后重新通过相关局部门。
2. 全文硬门（包括作者科学决定门）均为 `pass` 或有正当理由的 `not-applicable`；最终版本锁定不在这些硬门中。
3. 所有阻塞标记清零；`venue-unselected` 仅在目标是通用中文稿时可以保留。
4. 没有未核数值、未定位引用、待补实验、TBD、隐藏批注或旧版本冲突。
5. 输出明确写明：这是中文内容与逻辑的定稿状态，不代表已英译、已适配期刊、已排版、已投稿或已接受。

`S7` 需要作者在看到确切 S6 版本后明确回复确认；记录确认日期、稿件版本和被锁定的主旨、贡献、解释、局限与边界。更早的提纲或局部确认不能替代此动作。

## 交接包

达到 S6 时可以先生成“待作者锁定”的核对包，但不得据此启动正式英译。核对包至少记录：

```text
manuscript_id:
manuscript_revision:
chinese_manuscript_sha256:
chinese_manuscript_status: S6
handoff_status: pending_author_lock
thesis_and_contribution_ledger:
terminology_ledger:
numbers_and_units_ledger:
claim_boundaries_ledger:
citations_and_cross_references_ledger:
figure_inventory:
unresolved_blockers: []
```

作者必须审阅与该 SHA-256 完全一致的 S6 稿件，再生成结构化的 `author_lock_record`。完成后才可标记 S7：

```text
author_lock_record:
  lock_id:
  status: locked
  confirmed_by:
  confirmed_at:
  manuscript_id:
  manuscript_revision:
  manuscript_sha256:
```

其中七个键必须精确存在，`status` 必须为 `locked`；稿件 ID、修订号和 SHA-256 必须与当前 S6 文件完全一致，`lock_id` 必须同时出现在正式交接外壳的 `author_decisions` 中。`confirmed_at` 必须是带 UTC 偏移的 ISO-8601 时间，其本地日历日期不得晚于校验当天；正式 P3→P4 包中还不得晚于交接外壳的 `created_at`，该外壳时间由 `paperline` 按同一格式生成。缺少任一绑定字段、记录与稿件不一致，或只有口头说明而没有锁定记录，都不能进入 S7。

对于 `paperline` 的 P3→P4 正式全稿交接，必须已接收并应用确认的目标期刊合同，然后直接产出以下 `payload`；编排层不得替作者补造任一字段：

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
locked_thesis_and_contributions: {"inline": ["<已锁定主旨与贡献条目>"]}
terminology_ledger: {"path": "<相对交接文件的路径>", "sha256": "<64位小写十六进制>"}
locked_numbers_and_units: {"inline": ["<已锁定数字与单位条目>"]}
locked_claim_boundaries: {"inline": ["<已锁定主张边界条目>"]}
locked_citations_and_cross_references: {"inline": ["<已锁定引文与交叉引用条目>"]}
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

五项锁定台账只允许两种表示：`{"inline": <非空字符串、列表或对象>}`，或 `{"path": "<非空路径>", "sha256": "<64位小写十六进制>"}`；不得混合或添加第三种键。正式文件核验时，路径相对交接 JSON 所在目录解析，文件必须存在且哈希一致。

上述稿件 ID/修订号/哈希必须与当前 S7 产物和 `author_lock_record` 一致；`author_lock_record.lock_id` 必须出现在交接外壳的 `author_decisions` 中。期刊决定文件的 schema 版本、合同版本、两份文件的哈希和两类证据标识必须与当前已锁定契约一致。任一项变化都必须作废旧包。

若仍为 `venue-unselected`，可保留 S7 作者锁定历史，但不生成上述正式 `paperline` P4 包；需要中性英译时可单独调用翻译 Skill 的 `standalone` 模式。

生成 S7 正式交接包后结束 `paper-navigator` 流程。只有另行加载相应 Skill 后，才能执行英译或投稿材料制作。
