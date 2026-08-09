# paper-navigator smoke tests

Date: 2026-07-06
Scope: GitHub release readiness for `paper-navigator`.

| ID | Prompt | Expected route | Pass criteria | Result |
| --- | --- | --- | --- | --- |
| S1 | Use paper-navigator to plan a literature search for an emerging research topic. | literature | Produces query families, search depth, candidate table fields, and stopping criteria. | PASS: `literature-discovery.md` defines search tiers, query families, candidate table fields, and stopping log. |
| S2 | Use paper-navigator to read this paper and tell me what claims it can support. | reading | Produces source-grounded reading card with can-support/cannot-support boundaries. | PASS: `paper-reading.md` defines source-grounded reading card and support boundaries. If no paper is provided, correct behavior is to request/source-mark missing input. |
| S3 | Use paper-navigator to audit these result tables before writing Results. | provenance | Separates verified artifacts, missing lineage, claim support, and risks. | PASS: `experiment-provenance.md` defines result ledger, verified status, claim support, boundary, missing artifact, and risk output. |
| S4 | Use paper-navigator to choose figures for a manuscript section. | figure | Defines figure contracts, chart choices, captions, and visual QA. | PASS: `figure-planning-qa.md` defines figure contract, chart selection, caption structure, and visual QA. |
| S5 | Use paper-navigator to draft a Results paragraph from evidence notes. | writing | Produces draft text plus claim-evidence-boundary notes and missing support. | PASS: `writing-claim-evidence.md` requires claim/evidence/boundary mapping, draft text, and missing support notes. If evidence notes are absent, correct behavior is scaffold/gap output. |
| S6 | Use paper-navigator to add citations to this paragraph. | citation | Segments claims and grades support instead of title-matching. | PASS: `citation-support.md` requires atomic claim segmentation and support grades; `SKILL.md` forbids title relevance as support. If no paragraph is provided, correct behavior is scaffold/gap output. |
| S7 | Use paper-navigator to review this manuscript before submission. | review | Returns severity-ranked blockers, major issues, and author decisions. | PASS: `review-risk-audit.md` defines blocker/major severity and author-decision outputs. If no manuscript is provided, correct behavior is missing-input scaffold. |
| S8 | Use paper-navigator to prepare responses to these reviewer comments. | rebuttal | Classifies comments by decision impact and avoids unsupported commitments. | PASS: `rebuttal-response.md` classifies comments by decision impact and forbids unsupported commitments; formal response letters remain confirmation-gated. |

## Agent review notes

- S1-S2 reviewed by read-only smoke agent Russell (`019f363f-09f6-7541-a1fa-70457789ffb4`). Excerpt: S1 routed to `literature` and found search tiers, query families, candidate table fields, and stopping log; S2 routed to `reading` and found source-grounded reading card fields plus can-support/cannot-support boundaries.
- S3-S4 reviewed by read-only smoke agent Poincare (`019f363f-5059-73e1-8f8d-7fb9522ef9f7`). Excerpt: S3 routed to `provenance` and found result ledger, verified status, claim support, boundary, missing artifact, and risk output; S4 routed to `figure` and found figure contract, chart selection, caption structure, and visual QA.
- S5-S6 reviewed by read-only smoke agent Pascal (`019f363f-c6d0-74a2-b03f-7dda3242056c`). Excerpt: S5 routed to `writing` and found claim/evidence/boundary mapping, draft text, and missing support notes; S6 routed to `citation` and found atomic claim segmentation, support grades, and the title-relevance prohibition.
- S7-S8 reviewed by read-only smoke agent Hegel (`019f3640-0817-7c61-943f-feeddd267d21`). Excerpt: S7 routed to `review` and found blocker/major severity plus author-decision outputs; S8 routed to `rebuttal` and found decision-impact classification plus unsupported-commitment guardrails.
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
| T16 | Translate a salt-cavern or geotechnical-AI manuscript without a user glossary. | Load only relevant bundled terms, preserve source priority, and route ambiguous concepts to human review. | PASS: the domain guide defines selective loading; the termbase separates `verified` defaults from `pending` candidates and contains source IDs. |
| T17 | Validate the bundled literature and terminology data. | Reject missing columns, duplicate IDs/DOIs/Chinese terms, malformed DOI URLs, invalid statuses, and unresolved source IDs. | PASS: `validate_reference_data.py` performs these checks and enforces minimum catalogue sizes. |

Validation commands:

```powershell
python zh-en-paper-translator/scripts/audit_translation.py --self-test
python zh-en-paper-translator/scripts/audit_document_structure.py --self-test
python zh-en-paper-translator/scripts/validate_reference_data.py
python -m py_compile zh-en-paper-translator/scripts/audit_translation.py
python -m py_compile zh-en-paper-translator/scripts/audit_document_structure.py
python -m py_compile zh-en-paper-translator/scripts/validate_reference_data.py
python C:\Users\Windows11\.codex\skills\.system\skill-creator\scripts\quick_validate.py zh-en-paper-translator
```
