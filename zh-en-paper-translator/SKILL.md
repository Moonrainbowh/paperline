---
name: zh-en-paper-translator
description: Translate Chinese academic manuscripts into faithful, publication-ready academic English while preserving facts, data, tables, equations, citations, claim strength, structure, and document formatting. Use for Chinese-to-English translation of pasted text or complete Markdown (.md), Word (.docx), PDF (.pdf), and LaTeX (.tex) manuscripts, including titles, abstracts, sections, captions, table text, equation-adjacent language, footnotes, and supplementary text; for same-format output, terminology-ledger enforcement, OCR-gated scanned PDFs, translation or document-structure audits, and optional formal full-manuscript handoff from a paper-writing pipeline. Target-journal handling is optional and limited to explicit official language rules.
---

# Chinese-to-English Paper Translator

Translate the manuscript; do not redesign the study or silently rewrite its argument. Reconstruct natural English within sentences while preserving every proposition, qualification, number, citation, and evidential boundary in the Chinese source.

## Load the Required Guidance

- Read `references/section-language-matrix.md` for every translation task. Apply the row matching the section being translated.
- Read `references/terminology-governance.md` whenever technical terms, abbreviations, named methods, materials, software, standards, or a user glossary appear.
- Read `references/polysemy-and-personal-termbases.md` when one Chinese form has multiple technical senses, when creating a personal/project glossary, or when a termbase contains repeated `zh` values.
- Read `references/literature/geotechnical-domain-termbases-guide.md` and load the relevant scoped pack when the manuscript concerns machine learning in geotechnical engineering, geotechnical analogue materials, or salt-cavern construction. Use `references/termbases/geotechnical-machine-learning.tsv`, `references/termbases/geotechnical-analogue-materials.tsv`, or `references/termbases/salt-cavern-construction.tsv` respectively.
- Read `references/literature/salt-cavern-geotech-ai-guide.md` and load relevant rows from the broader `references/termbases/salt-cavern-geotech-ai.tsv` for salt-cavern storage/operation, hydrogen storage, compressed-air energy storage, or general geotechnical AI concepts not covered by the scoped packs.
- Read `references/human-review-and-output.md` for every substantial passage or complete manuscript.
- Read `references/pipeline-handoff.md` when a formal paperline handoff package is supplied or the user explicitly requests pipeline mode.
- Read `references/journal-language-boundary.md` only when the user provides a target journal or explicitly requests journal-language compliance.
- Read `references/format-routing.md` whenever the input is a file.
- Read exactly one matching format guide: `references/markdown-workflow.md`, `references/docx-workflow.md`, `references/pdf-workflow.md`, or `references/latex-workflow.md`.
- Read `references/tables-formulas.md` whenever a manuscript contains a table or equation.

## Establish the Translation Contract

Identify, without demanding unnecessary metadata:

- the Chinese source text and its section type;
- any user-approved glossary or previously translated passages;
- the intended output unit: passage, section, or complete manuscript;
- the source format and required output artifacts;
- an optional target journal;
- the translation mode: `standalone` by default, or `pipeline` only for an explicit formal full-manuscript handoff.

Infer the section from headings or context when safe. Ask only if the section is genuinely ambiguous and the choice would materially change the translation. Do not require a target journal.

Do not infer `pipeline` merely because the input is a complete file. Standalone passages, sections, and manuscripts do not require an `S7` writing status. If a formal paperline handoff package is present, do not bypass its gates by relabeling the task as standalone.

Treat the default contract as:

- translate only;
- preserve paragraph order and argumentative structure;
- allow clause reordering, subject selection, sentence splitting, and sentence merging only when needed for idiomatic English;
- do not add, remove, generalize, narrow, explain, or strengthen scientific content;
- do not turn association into causation, possibility into certainty, or local evidence into a general claim.

For files, preserve the source and write new outputs with `-en` before the extension. Use same-format output for Markdown, DOCX, and LaTeX. For PDF, always deliver both `source-en.pdf` and the editable companion `source-en.docx`. Never overwrite the source.

## Execute the Workflow

### 0. Validate an optional pipeline handoff

For `pipeline` mode, read `references/pipeline-handoff.md` before translation. Require an `S7` author-locked Chinese manuscript, an exact locked-package and manuscript version, the exact seven-field `author_lock_record` with `status: locked` bound to the manuscript bytes and wrapper decision, a confirmed target-journal contract, and locked terminology, numbers, units, claim boundaries, and author decisions. Express each locked ledger explicitly as `{inline: ...}` or `{path: ..., sha256: ...}`. Bind the translation to those versions. Pause on a missing field, version mismatch, unresolved blocker, or evidence/contract change that invalidates the lock.

For a JSON handoff, run `python scripts/validate_pipeline_handoff.py handoff.json --verify-files`. This mode verifies the manuscript and referenced-ledger bytes, loads the sibling `journal-navigator` formal validator, and cross-checks the parsed confirmed decision and contract against the payload. A result without `--verify-files` is structural only and must not authorize translation.

For `standalone` mode, proceed without `S7`; preserve the same semantic safeguards and report source ambiguities normally.

### 1. Freeze protected content

Extract or mentally mark all protected elements before drafting:

- numbers, signs, ranges, units, uncertainty, and statistical values;
- equations, symbols, subscripts, superscripts, and variable names;
- citations, DOI, URLs, figure/table/equation identifiers, and cross-references;
- proper nouns, dataset/model/software names, abbreviations, and quoted text;
- headings, paragraph order, table geometry, equation objects or environments, captions, footnotes, endnotes, labels, reference keys, and cross-references;
- negation, comparison direction, causal strength, modal strength, scope, and limitations.

Never normalize a protected element unless the user explicitly authorizes it.

### 2. Resolve terminology

Build or update a terminology ledger using the mandatory priority order:

`user-confirmed glossary > author-provided or official English > standard/specification > authoritative domain literature > pending candidate`

Lock an approved term across the document. Do not vary it merely to avoid repetition. Batch unresolved critical terms for human confirmation before translating dependent passages. Continue without interruption for ordinary wording choices and report them afterward only if materially uncertain.

For the three scoped geotechnical domains, load the matching focused pack first and use the older combined pack only to fill concepts outside its scope. Treat every bundled termbase as a source-supported starting layer. Select only context-relevant rows, overlay higher-priority user/author terms, and create a document-specific subset before auditing. Never treat a bundled `verified` row as user-confirmed, and never enforce a `pending` row without human review.

Allow one Chinese surface form to have multiple sense-scoped rows. Select a sense from the local sentence, paragraph, section, variable definitions, figures/tables, and project glossary when the evidence is sufficient. Do not ask merely because multiple rows exist. If the evidence cannot distinguish materially different senses, continue safe independent work and batch the unresolved sense for confirmation before finalizing the affected translation. Persist the confirmed choice at the narrowest valid scope and do not ask again within that scope unless later context conflicts.

### 3. Reconstruct meaning before prose

Recover the source propositions and their relations: contrast, cause, condition, purpose, sequence, exception, and limitation. Translate propositions rather than matching Chinese clauses word for word. Make implicit grammatical subjects explicit only when the source supports the choice.

### 4. Route the document format

Use `references/format-routing.md` and the matching format guide. Translate all in-scope scholarly text, including headings, body paragraphs, table headers and cells, table notes, captions, footnotes, endnotes, headers, and footers when present. Preserve embedded figures byte-for-byte or as unchanged placed objects; do not translate or edit text inside images.

### 5. Apply section-specific English

Use `references/section-language-matrix.md`. Choose tense and voice by rhetorical function, not by a rigid active-versus-passive rule. Keep Results observational and Discussion interpretive. Keep Methods reproducible. Keep Abstract claims compact but fully bounded.

### 6. Protect tables and formulas

Use `references/tables-formulas.md`. Translate human-readable table content without changing row/column structure, merged cells, numbers, units, or statistical symbols. Preserve mathematical operators, variables, indices, equation numbering, and equation structure. Translate only natural-language labels or prose inside formula text containers, and require human review when the boundary is unclear.

### 7. Apply optional journal rules

When no target journal is supplied, use neutral international academic English and remain internally consistent in spelling and mechanics. When a journal is supplied, apply only verified official hard-language rules according to `references/journal-language-boundary.md`. Never imitate recurring phrases from published papers as a substitute for accurate translation.

In `pipeline` mode, require `target_journal_status: contract-confirmed` and apply target-journal contract content only when the handoff records the same decision path, decision schema version and SHA-256, contract path/version/SHA-256, selection-evidence version, and writing-profile evidence ID. Apply only official mechanical language rules; return substantive restructuring, claim, evidence, section, disclosure, or word-limit changes to the writing pipeline instead of performing them during translation.

### 8. Run integrity checks

Compare the English against the Chinese source sentence by sentence. Check protected elements, terminology, claim strength, logical relations, and omissions. When files are available, run:

```text
python scripts/audit_translation.py --source source.txt --translation translation.txt --termbase terms.tsv
python scripts/audit_document_structure.py --source manuscript-zh.docx --translation manuscript-zh-en.docx
```

Treat the script as a deterministic safety net, not proof that the translation is semantically correct.

For DOCX and PDF outputs, render every final page to PNG and inspect every page at 100% zoom. Do not deliver a DOCX or PDF with clipped text, broken tables, missing equations, missing glyphs, overlaps, or displaced headers and footers. For PDF, text extraction is never a layout-fidelity check.

## Stop Conditions

Pause and request human confirmation when any of these conditions holds:

- a core term has multiple materially different English meanings;
- the source is internally contradictory or grammatically ambiguous in a way that changes the scientific meaning;
- an official English name cannot be distinguished from an unofficial translation;
- the source appears to contain a numerical, unit, citation, or cross-reference error;
- fluent English would require adding an unstated causal link, actor, condition, or conclusion.
- DOCX contains unresolved tracked changes, comments, protected content controls, or unsupported equation objects that make the visible source ambiguous;
- PDF extraction order is unreliable, a scan requires OCR, or an OCR result changes table or equation meaning;
- a formula contains natural-language text whose translation boundary cannot be separated safely from its mathematical structure.
- pipeline mode lacks `S7`, an author-locked package, an exact manuscript SHA-256, a confirmed journal binding, or any locked terminology/number/boundary field required by `references/pipeline-handoff.md`;
- the supplied manuscript, handoff package, or target-journal contract version differs from the locked versions;
- a requested journal change would require substantive adaptation rather than official mechanical language compliance.

Do not silently select the most plausible scientific interpretation.

## Output

Return the English translation first. Then provide only the supporting items required by `references/human-review-and-output.md`: terminology decisions, questions requiring confirmation, and integrity warnings. Do not clutter a clean translation with generic style commentary.

For `pipeline` mode, also return the compact handoff audit defined in `references/pipeline-handoff.md`; do not claim that translation completes journal adaptation, formatting, or submission.
