# paperline 学术论文 Skills

本仓库包含一个薄入口和三个可独立使用的专业 Codex Skills：

| Skill | 范围 |
| --- | --- |
| `paperline` | 编排中文研究画像、期刊决策/契约、中文 S6/S7 定稿、忠实英译和投稿前检查；只管阶段、确认门、版本、交接和恢复。 |
| `paper-navigator` | 组织证据驱动的文献检索、合法全文获取、阅读、结果溯源、中文论文写作定稿、引用、图表、投稿前审查和审稿回复。 |
| `journal-navigator` | 使用有日期和来源的证据做跨期刊硬门/软偏好筛选，再为作者确认的目标期刊建立“期刊轨道 + 领域轨道”写作画像和可验证契约。 |
| `zh-en-paper-translator` | 在中文稿定稿后，将其转换为忠实的学术英语，并执行章节语言、术语、人工确认和确定性完整性检查。 |

本仓库只包含工作流指导，不包含数据集、模型检查点、论文草稿、审稿意见、私人笔记或特定论文的中间产物。

## `paperline` 用途

- 用一个入口推进“中文研究画像 → 选刊与规则锁定 → 中文全文定稿 → 中译英 → 投稿前检查”。
- 对已有项目保存可恢复的阶段、产物版本、SHA-256、作者确认和失效原因。
- 期刊未定时可经作者授权先写通用中文稿，但正式流水线英译必须等目标期刊契约锁定且中文稿达到 S7。
- 期刊、契约、中文 S7 或英文稿变化时，从最早失效阶段恢复，不删除历史产物。

## `journal-navigator` 用途

- 将期刊范围、论文类型、收录、OA/APC、时间、数据/伦理政策等作为硬门；未知硬门不视为通过。
- 只对硬门通过者根据作者确认的偏好和权重排序，不伪造接受率或预测录用概率。
- 作者选定后，再分别建立目标期刊表达画像和领域科学论证蓝图。
- 只有 `target-journal-decision.md` 和 `target-journal-writing-contract.md` 都通过确定性校验，才允许正式交给 `paper-navigator`。

## `paper-navigator` 用途

- 从零散研究材料规划完整论文流程。
- 以工程、实验、数值模拟和方法类研究论文为默认对象，先完成中文文字定稿。
- 为综述、纯理论和技术路线请求提供独立结构合同，不把实证论文模板强套到其他类型。
- 执行“主题/边界→材料盘点→一句话主旨→贡献合同→章节结构→方法→结果→讨论→结论→最终引言→摘要→反向提纲→质量门”的19步工作流。
- 在写作前建立主张—证据—边界地图，并细化到章节、段落和句子功能。
- 保持文献检索、阅读、引用和相关工作可回溯来源。
- 将筛选保留的 DOI 交给合法开放获取或已安装的 InstSci 机构访问流程，并在阅读前核验 PDF。
- 审计数据、代码、结果、图表和引用来源。
- 围绕论文主张规划图表、图注和技术路线。
- 运行逐节反向提纲、跨章节一致性和中文定稿质量门。
- 从真实审稿意见组织修改和回复。

`paper-navigator` 的 AI 判定上限是 `S6 中文文字定稿`；此时只生成待作者锁定的交接包。只有作者审阅并明确锁定确切的 S6 版本后，才能标记 `S7 作者确认锁定` 并正式交给英文转换 Skill。期刊表达适配和投稿仍是后续独立状态。

## `zh-en-paper-translator` 用途

- Translating titles, abstracts, introductions, methods, results, discussions, conclusions, captions, and complete manuscripts.
- Preserving facts, numbers, units, equations, citations, claim strength, and paragraph order while reconstructing natural English sentences.
- Enforcing terminology priority: user-confirmed glossary, official English, standards, authoritative literature, then pending candidates.
- Pausing for human confirmation only when terminology or source ambiguity changes scientific meaning.
- Applying target-journal language rules only when supplied and officially verifiable; the journal is not required.
- Auditing numeric tokens, citation markers, DOI, URLs, locked terms, forbidden terms, and residual Chinese text.
- Reading and writing Markdown, DOCX, PDF, and LaTeX manuscripts with format-specific protection rules.
- Translating body text, table content, captions, notes, and natural-language formula labels while preserving mathematical structure.
- Returning same-format Markdown/DOCX/LaTeX output; PDF input returns both an English PDF and editable DOCX.
- Supporting scanned PDFs through an OCR route with mandatory review of OCR prose, tables, numbers, and formulas.
- Preserving embedded figures without translating or editing text inside images.

## Repository layout

```text
chaos-14-paperline/
  README.md
  LICENSE
  .gitignore
  validation-smoke-tests.md
  dist/
    paper-navigator-skill-v1.0.0.zip
    paper-navigator-skill-v1.0.0.zip.sha256
  paper-navigator/
    SKILL.md
    agents/
      openai.yaml
    references/
      citation-support.md
      chinese-writing-rules.md
      experiment-provenance.md
      figure-planning-qa.md
      fulltext-access.md
      literature-discovery.md
      manuscript-finalization-workflow.md
      manuscript-status-quality-gates.md
      module-routing.md
      paper-reading.md
      paper-type-structures.md
      rebuttal-response.md
      reverse-outline-consistency.md
      research-context-passport.md
      review-risk-audit.md
      section-abstract-introduction-related-work.md
      section-discussion-conclusion.md
      section-methods-results.md
      writing-claim-evidence.md
  journal-navigator/
    SKILL.md
    agents/
      openai.yaml
    references/
      contracts-and-handoffs.md
      evidence-and-currentness.md
      journal-selection.md
      writing-profile.md
    scripts/
      validate_journal_artifacts.py
  paperline/
    SKILL.md
    agents/
      openai.yaml
    references/
      pipeline-contract.md
    scripts/
      run_contract_dry_run.py
      validate_pipeline_state.py
  zh-en-paper-translator/
    SKILL.md
    agents/
      openai.yaml
    references/
      docx-workflow.md
      format-routing.md
      human-review-and-output.md
      journal-language-boundary.md
      latex-workflow.md
      markdown-workflow.md
      pdf-workflow.md
      section-language-matrix.md
      tables-formulas.md
      terminology-governance.md
      pipeline-handoff.md
    scripts/
      audit_document_structure.py
      audit_translation.py
      validate_pipeline_handoff.py
      validate_reference_data.py
```

## Installation

Copy the desired skill folder or all four sibling folders into a local Codex skills directory, then restart Codex. The current source-tree work does not perform this installation automatically.

Common locations:

```powershell
~\.codex\skills\paper-navigator
~\.codex\skills\paperline
~\.codex\skills\journal-navigator
~\.codex\skills\zh-en-paper-translator
```

or:

```powershell
~\.agents\skills\paper-navigator
~\.agents\skills\paperline
~\.agents\skills\journal-navigator
~\.agents\skills\zh-en-paper-translator
```

After restart, trigger it with prompts such as:

```text
Use $paperline to take this manuscript from Chinese evidence alignment through journal selection, Chinese S7 lock, faithful English translation, and pre-submission checks.
使用 $paperline 恢复这篇论文的流程，告诉我当前阶段、阻塞项和下一个安全动作。
Use $journal-navigator to compare candidate journals using current official evidence and my APC/indexing constraints.
使用 $journal-navigator 为我已确认的目标期刊建立双轨中文写作契约。
Use paper-navigator to plan the next safe step for this manuscript.
Use $paper-navigator to plan the next safe step for this manuscript.
Use paper-navigator to audit the claim-evidence chain in this Results draft.
Use paper-navigator to prepare a rebuttal plan from these reviewer comments.
使用 $paper-navigator 从已有数据和结果开始，推进到完整的中文论文文字定稿。
使用 $paper-navigator 为这篇工程论文建立引言段落蓝图和逐句功能链。
使用 $paper-navigator 对这份中文稿运行反向提纲和跨章节一致性检查。
Use $zh-en-paper-translator to translate this Chinese Results section into faithful academic English.
Use $zh-en-paper-translator with this approved terminology table to translate the complete manuscript.
Use $zh-en-paper-translator to translate this DOCX and preserve its tables and Word equations.
Use $zh-en-paper-translator to translate this scanned PDF and return an English PDF plus editable DOCX.
Use $zh-en-paper-translator to translate this salt-cavern paper using the bundled salt-cavern and geotechnical-AI terminology reference.
```

## Source validation

The repository-level dry run uses synthetic artifacts to exercise the formal journal decision and writing contract, Chinese S7 lock, P3→P4 translation handoff, P4→P5 pre-submission handoff, file hashes, rollback rules, and negative gates. It does not select a real journal or translate a real manuscript.

```powershell
python paperline/scripts/run_contract_dry_run.py
python journal-navigator/scripts/validate_journal_artifacts.py --self-test
python paperline/scripts/validate_pipeline_state.py --self-test
python zh-en-paper-translator/scripts/validate_pipeline_handoff.py --self-test
python zh-en-paper-translator/scripts/audit_translation.py --self-test
python zh-en-paper-translator/scripts/audit_document_structure.py --self-test
python zh-en-paper-translator/scripts/validate_reference_data.py
```

Skill-structure checks can then be run separately for each of the four source folders with the bundled `skill-creator/scripts/quick_validate.py` validator. On Windows, invoke it with `python -X utf8` so Chinese Markdown is decoded reproducibly, for example:

```powershell
python -X utf8 C:\Users\Windows11\.codex\skills\.system\skill-creator\scripts\quick_validate.py paperline
```

## Release archive verification

The existing `dist/` directory contains the earlier `paper-navigator-skill-v1.0.0` archive and checksum. It was not rebuilt for the current four-Skill source architecture and therefore must not be treated as a package of `paperline` or `journal-navigator`. To verify that legacy archive on Windows:

```powershell
$zip = "dist\paper-navigator-skill-v1.0.0.zip"
Get-FileHash -Algorithm SHA256 $zip
Get-Content "$zip.sha256"
```

The hash printed by `Get-FileHash` should match the first field in `paper-navigator-skill-v1.0.0.zip.sha256`.

`validation-smoke-tests.md` records route-level smoke tests for the major workflow paths. These smoke tests validate that the skill routes to the expected reference modules and preserves evidence-boundary behavior.

## Compatibility notes

- Browser search, web extraction, and multi-agent review depend on the host agent environment. Formal journal selection must refresh time-sensitive claims from official sources when a real case is supplied.
- Closed-access publisher retrieval is optional and requires a separately installed InstSci Skill/CLI plus the user's authorized institution; this repository stores no credentials or subscription state.
- When those tools are unavailable, use the same workflow sequentially: gather sources, build reading cards, audit provenance, then synthesize.
- The skill does not require bundled datasets, model files, API keys, or private materials.
- DOCX and PDF translation require a host runtime with Word/OOXML, PDF extraction, OCR when needed, and page-rendering capabilities.
- PDF output preserves logical content and a reviewed layout, not pixel-identical line breaks or pagination.
- `zh-en-paper-translator` includes a curated, source-linked salt-cavern/geotechnical-AI literature catalogue and bilingual termbase. These resources are reference layers; user-confirmed and author-provided terminology still takes precedence.

## Design principles

- Evidence before prose.
- Explicit research boundaries.
- Provenance for data, code, results, figures, citations, drafts, and decisions.
- Claim-level citation support.
- Figures serve claims.
- Confirmation gates for target venue, validation route, data/code release, author declarations, reviewer responses, and global installation.

## Design inspirations and attribution

This repository is original workflow text. It was informed by public research-skill patterns but does not redistribute upstream source code, scripts, long-form templates, datasets, manuscript text, figures, or reviewer-response templates.

| Source | What was abstracted |
| --- | --- |
| [`Yuan1z0825/nature-skills`](https://github.com/Yuan1z0825/nature-skills) | Modular research skills for writing, figures, citations, reading, data, and responses. |
| [`Imbad0202/academic-research-skills`](https://github.com/Imbad0202/academic-research-skills) | End-to-end academic workflow structure, quality gates, provenance thinking, and claim auditing. |
| [`O0000-code/paper-search-pro`](https://github.com/O0000-code/paper-search-pro) | Multi-source literature discovery, search-depth tiers, metadata outputs, and reproducible search logs. |
| [`Haojae/scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill) | Scientific figure planning, chart-type selection, visual QA, and publication-oriented figure discipline. |
| [`SNL-UCSB/paper-writing-skill`](https://github.com/SNL-UCSB/paper-writing-skill) | Structured paper-writing flow from ideas to sections, with emphasis on claims and section moves. |
| [`Master-cai/Research-Paper-Writing-Skills`](https://github.com/Master-cai/Research-Paper-Writing-Skills) | Paragraph-function planning, reverse outlining, claim-support alignment, and section-level self-review. |
| [`kgraph57/paper-writer-skill`](https://github.com/kgraph57/paper-writer-skill) | Explicit manuscript-section states and hard quality-gate concepts, abstracted without its medical lifecycle. |
| [`M1n-n9/paper-lifecycle`](https://github.com/M1n-n9/paper-lifecycle) | Review/revision/rebuttal lifecycle thinking and reviewer-style risk diagnosis. |
| [`kesslerio/academic-deep-research-clawhub-skill`](https://github.com/kesslerio/academic-deep-research-clawhub-skill) | Deep research framing, evidence grading, and review-oriented synthesis patterns. |

## Reuse boundary

- This repository contains original workflow guidance for `paperline`, `paper-navigator`, `journal-navigator`, and `zh-en-paper-translator`.
- It does not copy upstream files, scripts, prompts, templates, datasets, figures, captions, or long passages.
- Check upstream licenses separately before reusing any upstream material directly.
- Treat unlicensed or non-commercial upstream projects as inspiration only unless you obtain permission.

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE).
