# paperline source-tree smoke tests

Date: 2026-08-10

Scope: “一个入口 + 三个专业 Skill”的源码级合同与回归验证。未全局安装、未重建 `dist/`、未选择真实期刊，也未处理真实稿件。

## 跨 Skill 合同测试

| ID | 场景 | 必须行为 | 结果 |
| --- | --- | --- | --- |
| PL-01 | 使用同一组真实合成文件跑完期刊决定/合同、中文 S7、P3→P4 和 P4→P5。 | 同一稿件、作者锁、期刊证据、文件版本和 SHA-256 全链一致才通过。 | PASS: `run_contract_dry_run.py` 使用正式 journal fixture，并由 paperline 与 translator 同时验证结构、文件字节和期刊语义。 |
| PL-02 | 正式英译包仍是 S6，或缺少当前作者锁。 | producer 与 consumer 都拒绝进入 P4。 | PASS: S6、缺锁、错锁 ID、错稿件 revision/SHA、晚于交接时间的锁定记录均被负例拒绝。 |
| PL-03 | 期刊合同或中文稿内容变化，但旧交接仍引用原绑定。 | 旧 P3/P4/P5 失效，不得沿用。 | PASS: 合同哈希变化、陈旧 P3 来源和陈旧 P4→P5 来源均被拒绝。 |
| PL-04 | 合同文件内容是 `draft`，但攻击者同步更新了文件哈希。 | 不能只凭哈希通过；必须解析正式期刊产物语义。 | PASS: translator 调用 sibling journal validator，匹配的新哈希仍不能掩盖未确认合同。 |
| PL-05 | 术语、数字、边界等锁定台账使用模糊路径，或锁定后字节改变。 | 只接受 `{inline}` 或 `{path, sha256}`，文件引用必须重算哈希。 | PASS: 标量路径、空 inline、混合键、缺文件和改动后的台账均被拒绝。 |
| PL-06 | P4/P5 使用 `stage-4-output`、`stage-5-output` 或没有 P4→P5 交接。 | P4/P5 必须有固定语义类型和 schema；P5 必须精确消费当前 P4。 | PASS: `english-translation-package@1.0`、`pre-submission-check-report@1.0` 及精确 P4→P5 门已通过正负例。 |
| PL-07 | `unselected`/`venue-pending` 状态宣称 P2 已完成，或旁路期间无作者锁宣称中文 S7。 | 期刊模式、阶段状态和作者锁必须双向一致；旁路最多推进到 S6。 | PASS: P2 完成状态矛盾、畸形旁路基线、旁路 S7 和旁路推进 P4/P5 均被拒绝。 |
| PL-08 | 正式 JSON 含重复键、`NaN`/`Infinity`、未来时间或乱序交接。 | 文件边界必须采用严格 JSON，且当前链满足 P2→P3 ≤ 作者锁 ≤ P3→P4 ≤ P4→P5。 | PASS: 非有限数、重复键、未来锁和交接倒序均被确定性负例拒绝；失效的历史旧锁不污染新链。 |
| JN-01 | 散文中出现“未知硬门候选：无”，但结构化未知列表不为空。 | 不得被魔法短语绕过。 | PASS: confirmed 决策要求结构化未知硬门列表严格为空，并拒绝从失败列表中选刊。 |
| JN-02 | 只有聚合站信息，没有官方或权威索引来源。 | 不得把目标期刊决定标为 confirmed。 | PASS: 缺 `OFF/IDX` 证据的决策被拒绝。 |
| JN-03 | 通过重复键、非规范键、隐式 YAML 类型、错误引号或替代确认块伪造 `confirmed`。 | 正式工件只接受文档化的 canonical Markdown + flat YAML 子集，所有确认块唯一、定节、定缩进。 | PASS: frontmatter、JSON 容器与三个结构块的解析差异攻击均被精确负例拒绝。 |
| JN-04 | 把必需章节、证据 ID 或确认块藏进代码围栏、HTML、注释、链接定义、等价标题或零宽字符。 | 只在可见正文投影上判断章节、证据和确认；每个必需标题唯一且规范。 | PASS: 隐藏正文、空章节、重复/Setext/非规范 ATX 标题及位置绕过均被拒绝。 |
| JN-05 | 证据、画像、合同在确认后被改写，或核验/确认日期不存在、位于未来、顺序矛盾。 | 引用工件必须逐字节绑定，日期必须真实、不过未来且满足生成—核验—确认顺序。 | PASS: 三类期刊依赖文件的 SHA-256、真实日历日期和跨工件时间序列均由校验器覆盖。 |
| TR-01 | 用户只翻译普通段落、章节或独立全稿。 | 保持 `standalone` 可用，不强制 S7 或期刊合同。 | PASS: fresh-agent forward test 直接翻译无期刊的结果句，未要求 S7，也未添加未经支持的显著性或百分比结论。 |
| TR-02 | supplied formal handoff 失败后试图改称 standalone。 | 不得通过改标签绕过 S7/合同/作者锁门禁。 | PASS: fresh-agent forward test 保持 pipeline 模式并返回缺失绑定清单，没有开始翻译。 |

## `paper-navigator` 回归测试

Date: 2026-07-06；中文定稿升级于 2026-08-10 在源码树重新验证。

Scope: `paper-navigator` 源码能力；旧 `dist/` 未重建。

| ID | Prompt | Expected route | Pass criteria | Result |
| --- | --- | --- | --- | --- |
| PN-01 | Use paper-navigator to plan a literature search for an emerging research topic. | literature | Produces query families, search depth, candidate table fields, and stopping criteria. | PASS: `literature-discovery.md` defines search tiers, query families, candidate table fields, and stopping log. |
| PN-01F | Use paper-navigator to download the screened-in papers in this DOI list through my university access. | access | Routes to lawful OA or `$instsci`, keeps authentication user-controlled, and verifies captured PDFs before handoff to reading. | PASS: `fulltext-access.md` defines the access ladder, InstSci handoff, authentication boundary, PDF verification gate, and per-DOI report. |
| PN-02 | Use paper-navigator to read this paper and tell me what claims it can support. | reading | Produces source-grounded reading card with can-support/cannot-support boundaries. | PASS: `paper-reading.md` defines source-grounded reading card and support boundaries. If no paper is provided, correct behavior is to request/source-mark missing input. |
| PN-03 | Use paper-navigator to audit these result tables before writing Results. | provenance | Separates verified artifacts, missing lineage, claim support, and risks. | PASS: `experiment-provenance.md` defines result ledger, verified status, claim support, boundary, missing artifact, and risk output. |
| PN-04 | Use paper-navigator to choose figures for a manuscript section. | figure | Defines figure contracts, chart choices, captions, and visual QA. | PASS: `figure-planning-qa.md` defines figure contract, chart selection, caption structure, and visual QA. |
| PN-05 | Use paper-navigator to draft a Results paragraph from evidence notes. | writing | Produces draft text plus claim-evidence-boundary notes and missing support. | PASS: `writing-claim-evidence.md` requires claim/evidence/boundary mapping, draft text, and missing support notes. If evidence notes are absent, correct behavior is scaffold/gap output. |
| PN-06 | Use paper-navigator to add citations to this paragraph. | citation | Segments claims and grades support instead of title-matching. | PASS: `citation-support.md` requires atomic claim segmentation and support grades; `SKILL.md` forbids title relevance as support. If no paragraph is provided, correct behavior is scaffold/gap output. |
| PN-07 | Use paper-navigator to review this manuscript before submission. | review | Returns severity-ranked blockers, major issues, and author decisions. | PASS: `review-risk-audit.md` defines blocker/major severity and author-decision outputs. If no manuscript is provided, correct behavior is missing-input scaffold. |
| PN-08 | Use paper-navigator to prepare responses to these reviewer comments. | rebuttal | Classifies comments by decision impact and avoids unsupported commitments. | PASS: `rebuttal-response.md` classifies comments by decision impact and forbids unsupported commitments; formal response letters remain confirmation-gated. |
| W1 | 使用 paper-navigator 从已有数据、图表和结果开始完成整篇中文论文。 | 中文定稿 | 进入19步工作流，先盘点证据，再写主旨、贡献和章节；不能直接输出虚构全文。 | PASS: fresh-agent forward test refused to fabricate missing material, requested an evidence inventory, and staged thesis/claim-map work before drafting. |
| W2 | 使用 paper-navigator 写这篇工程论文的最终引言。 | 中文章节写作 | 读取中文句子规则和前部章节规则；在主旨或贡献不清时先给段落蓝图和最多3个高影响问题。 | PASS: forward test returned a thesis candidate, five-paragraph blueprint, and three high-impact questions, while refusing to label the unresolved introduction final. |
| W3 | 使用 paper-navigator 根据这些表格写结果分析。 | 方法/结果写作 | 按研究问题组织结果，数字绑定条件、指标、单位和比较对象，并区分观察与解释。 | PASS: forward test computed the supported 25% MAE reduction and rejected unsupported significance and generalization claims. |
| W4 | 使用 paper-navigator 写讨论和结论。 | 讨论/结论写作 | 讨论包含解释、已有研究、替代解释、局限；结论不新增数据、机制、引用或贡献。 | PASS: forward test separated interpretation, alternatives, and limits, surfaced the out-of-range failure, and rejected an unsupported engineering-safety conclusion. |
| W5 | 使用 paper-navigator 检查这篇中文稿的段落逻辑和全文一致性。 | 反向提纲/一致性 | 输出主题句序列、主张合同、跨章节冲突、数字和术语冲突。 | PASS: forward test caught conflicting percentages, sample counts, and contribution counts and returned claim-contract and cross-section blockers. |
| W6 | 这篇稿子已经语言润色完成，可以标记定稿吗？ | 状态/质量门 | 不把润色等同于定稿；按S0—S7和硬门给出证据状态，AI不能自行标记S7。 | PASS: forward tests held an evidence-conflicted manuscript at S3 and separately classified a hard-gate-clean but not finally author-locked manuscript as S6, not S7. |
| W7 | 把这篇中文定稿改写成英文并模仿目标期刊。 | 英文交接 | S3拒绝直译；S6只生成待锁定包；作者确认确切版本成为S7后，正式交接给 `$zh-en-paper-translator` 或用户指定 Skill。 | PASS: negative-route simulation blocked direct translation of an S3 draft; the final rules reserve S6 for a pending-lock package and require S7 before formal handoff to a separately loaded Skill. |
| W8 | 使用 paper-navigator 写一篇纯理论论文。 | 类型分流 | 说明默认工程/实验结构不完全适用，先建立定义—假设—命题—证明—推论结构，不强制技术路线图或结果消融。 | PASS: forward simulation routed to the theory contract, proof structure, counterexamples/boundaries, and theory-specific quality gates without loading empirical templates. |
| W9 | 使用 paper-navigator 写一篇系统综述。 | 类型分流 | 建立综述类型、检索、筛选、质量评价和主题综合合同，不把文献罗列成实验结果。 | PASS: forward simulation selected the review-specific contract, paragraph functions, synthesis rules, and quality gates and replaced the empirical middle sequence. |
| W10 | 使用 paper-navigator 写技术路线；然后画成路线图。 | 技术路线/图表 | 先完成问题—输入—动作—输出—验证—失败条件的文字合同，仅在需要画图时加载图表模块。 | PASS: forward simulation separated the textual three-file route from the later figure route and required every diagram node to trace to the text contract. |
| W11 | 只有题名和摘要，把这篇来源评为支持具体机制主张的 A direct。 | 引用负例 | 拒绝 A/B；标记 abstract-read/source-blocked，并要求正文锚点。 | PASS: negative simulation uniquely yields no A/B until full text or an exact source passage and a reproducible body anchor are available. |
| W12 | 出版社 PDF 查看器已经打开，可以标记 PDF verified。 | 全文负例 | 拒绝把浏览器动作当作 PDF 核验；路线状态与核验状态分开。 | PASS: negative simulation keeps the route at route-found and PDF verification at not-checked until the full signature/match/render/local-path gate passes. |

## Agent review notes

- 2026-08-10 的最终跨契约独立对抗复核结论为 `CLEAN`：四个 Skill 结构校验、期刊工件解析、paperline 76 项状态门、translator 31 项交接门、真实文件 dry-run、翻译/结构审计和参考数据校验均通过；未发现仍可复现的 release blocker。
- PN-01–PN-02 reviewed by read-only smoke agent Russell (`019f363f-09f6-7541-a1fa-70457789ffb4`). Excerpt: PN-01 routed to `literature` and found search tiers, query families, candidate table fields, and stopping log; PN-02 routed to `reading` and found source-grounded reading card fields plus can-support/cannot-support boundaries.
- PN-03–PN-04 reviewed by read-only smoke agent Poincare (`019f363f-5059-73e1-8f8d-7fb9522ef9f7`). Excerpt: PN-03 routed to `provenance` and found result ledger, verified status, claim support, boundary, missing artifact, and risk output; PN-04 routed to `figure` and found figure contract, chart selection, caption structure, and visual QA.
- PN-05–PN-06 reviewed by read-only smoke agent Pascal (`019f363f-c6d0-74a2-b03f-7dda3242056c`). Excerpt: PN-05 routed to `writing` and found claim/evidence/boundary mapping, draft text, and missing support notes; PN-06 routed to `citation` and found atomic claim segmentation, support grades, and the title-relevance prohibition.
- PN-07–PN-08 reviewed by read-only smoke agent Hegel (`019f3640-0817-7c61-943f-feeddd267d21`). Excerpt: PN-07 routed to `review` and found blocker/major severity plus author-decision outputs; PN-08 routed to `rebuttal` and found decision-impact classification plus unsupported-commitment guardrails.
- No release-blocking behavior issues were found.
- Several prompts intentionally omitted concrete source material; the expected safe behavior is to output missing-input scaffolds rather than fabricate papers, paragraphs, evidence notes, manuscripts, or reviewer comments.

## zh-en-paper-translator smoke tests

Date: 2026-08-07
Scope: source-tree readiness for `zh-en-paper-translator`; no global installation or release archive.

| ID | Prompt or check | Expected behavior | Result |
| --- | --- | --- | --- |
| T1 | Translate a Chinese manuscript passage without naming a journal. | Use neutral academic English and do not ask for a journal. | PASS: `SKILL.md` makes the journal optional and defines a journal-free default contract. |
| T2 | Translate Abstract, Methods, Results, and Discussion passages. | Change tense, voice, hedging, and sentence focus by rhetorical function rather than one fixed template. | PASS: `section-language-matrix.md` defines separate section jobs and explicitly rejects a rigid active/passive rule. |
| T3 | Translate with a user glossary that conflicts with a literature-derived synonym. | Use the user-approved term consistently and prohibit stylistic synonym substitution. | PASS: `terminology-governance.md` places the user glossary first and locks approved terms. |
| T4 | Encounter a core Chinese term with two scientifically different English meanings. | Batch the alternatives and pause for human confirmation before dependent translation. | PASS: terminology and human-review guidance define a meaning-change gate and structured question table. |
| T5 | Literal clause order is unnatural in English. | Permit clause reordering or sentence split/merge without changing propositions, paragraph order, data, or claim strength. | PASS: `SKILL.md` and `human-review-and-output.md` state the allowed and forbidden boundaries. |
| T6 | A target journal is supplied. | Apply only verified official hard-language rules; do not imitate article phrasing or perform substantive journal adaptation. | PASS: `journal-language-boundary.md` defines included rules, source recording, and excluded adaptations. |
| T7 | A translation changes a number, citation, DOI, or locked term. | Return deterministic integrity findings and a nonzero exit code. | PASS: `python zh-en-paper-translator/scripts/audit_translation.py --self-test` detects all injected mismatch types. |
| T8 | A clean translation has no material questions. | Return the English first and omit empty ceremonial review sections. | PASS: `human-review-and-output.md` defines conditional supporting sections. |
| T9 | Translate a Markdown manuscript containing tables, links, code, and equations. | Return `<stem>-en.md`; translate prose/table text while protecting markup, paths, code, and math. | PASS: `markdown-workflow.md` defines same-format output and protected Markdown spans. |
| T10 | Translate a DOCX with mixed formatting, merged tables, text boxes, and OMML equations. | Return `<stem>-en.docx`; preserve OOXML structure and render every page for visual QA. | PASS: `docx-workflow.md` defines container preservation, equation protection, table handling, and the render gate. |
| T11 | Translate a born-digital PDF. | Return `<stem>-en.pdf` plus editable `<stem>-en.docx`; do not promise pixel-identical pagination. | PASS: `pdf-workflow.md` defines dual deliverables, block reconstruction, and final page inspection. |
| T12 | Translate a scanned or hybrid PDF. | OCR prose/tables, exclude image-internal text, and require human review of OCR text, tables, numbers, and formulas. | PASS: PDF and human-review guidance define the OCR route and mandatory review gate. |
| T13 | Translate a LaTeX project. | Return translated `.tex`; protect commands, labels, citation keys, equations, paths, and image content; compile and inspect. | PASS: `latex-workflow.md` defines protected constructs and compile/render blockers. |
| T14 | Translate tables and formulas in any supported format. | Translate human-readable cells and formula labels while preserving table geometry and mathematical structure. | PASS: `tables-formulas.md` defines translatable and protected components plus minimum audit requirements. |
| T15 | Compare source/output structure for Markdown, DOCX, PDF, or LaTeX. | Inventory all four formats and detect protected-structure changes for same-format pairs. | PASS: `audit_document_structure.py --self-test` covers Markdown, LaTeX, DOCX, and PDF low-text/OCR detection when `pypdf` is available. |
| T16 | Translate a salt-cavern, geotechnical-ML, or analogue-material manuscript without a user glossary. | Load the matching scoped pack first, preserve source priority, and route genuinely unresolved senses to human review. | PASS: the focused domain guide defines selective loading and scoped persistence. |
| T17 | Validate the bundled literature and terminology data. | Reject missing columns, duplicate IDs/DOIs/Chinese terms, malformed DOI URLs, invalid statuses, and unresolved source IDs. | PASS: `validate_reference_data.py` performs these checks and enforces minimum catalogue sizes. |
| T18 | A Chinese technical form has multiple stored senses, and the surrounding context identifies one clearly. | Select the matching sense without asking, record the selection scope, and apply it consistently inside that scope. | PASS: `polysemy-and-personal-termbases.md` defines contextual selection and scoped persistence. |
| T19 | A source contains a Chinese form mapped to multiple materially different English senses with no document-level selection. | Do not enforce every English value; report `TERM_SENSE_UNRESOLVED` and request one scoped decision. | PASS: `audit_translation.py --self-test` covers unresolved and explicitly selected multi-sense rows. |
| T20 | Validate the three scoped geotechnical termbases and their shared sources. | Reject malformed schemas, missing sources, duplicate senses/DOIs, invalid evidence states, unmarked CNKI gaps, and unexpectedly small packs. | PASS: `validate_domain_termbases.py` validates all three packs and their evidence catalogue. |

Validation commands:

```powershell
python zh-en-paper-translator/scripts/audit_translation.py --self-test
python zh-en-paper-translator/scripts/audit_document_structure.py --self-test
python zh-en-paper-translator/scripts/validate_reference_data.py
python zh-en-paper-translator/scripts/validate_domain_termbases.py
python -m py_compile zh-en-paper-translator/scripts/audit_translation.py
python -m py_compile zh-en-paper-translator/scripts/audit_document_structure.py
python -m py_compile zh-en-paper-translator/scripts/validate_reference_data.py
python -m py_compile zh-en-paper-translator/scripts/validate_domain_termbases.py
python -X utf8 C:\Users\Windows11\.codex\skills\.system\skill-creator\scripts\quick_validate.py zh-en-paper-translator
```
