---
name: zh-en-paper-translator
description: Translate Chinese academic manuscripts into faithful, publication-ready academic English while preserving facts, data, equations, citations, claim strength, and paragraph order. Use for Chinese-to-English translation of paper titles, abstracts, introductions, methods, results, discussions, conclusions, captions, tables, supplementary text, or complete manuscripts; for terminology-ledger creation and enforcement; and for translation consistency audits. Target-journal handling is optional and limited to explicit official language rules.
---

# Chinese-to-English Paper Translator

Translate the manuscript; do not redesign the study or silently rewrite its argument. Reconstruct natural English within sentences while preserving every proposition, qualification, number, citation, and evidential boundary in the Chinese source.

## Load the Required Guidance

- Read `references/section-language-matrix.md` for every translation task. Apply the row matching the section being translated.
- Read `references/terminology-governance.md` whenever technical terms, abbreviations, named methods, materials, software, standards, or a user glossary appear.
- Read `references/human-review-and-output.md` for every substantial passage or complete manuscript.
- Read `references/journal-language-boundary.md` only when the user provides a target journal or explicitly requests journal-language compliance.

## Establish the Translation Contract

Identify, without demanding unnecessary metadata:

- the Chinese source text and its section type;
- any user-approved glossary or previously translated passages;
- the intended output unit: passage, section, or complete manuscript;
- an optional target journal.

Infer the section from headings or context when safe. Ask only if the section is genuinely ambiguous and the choice would materially change the translation. Do not require a target journal.

Treat the default contract as:

- translate only;
- preserve paragraph order and argumentative structure;
- allow clause reordering, subject selection, sentence splitting, and sentence merging only when needed for idiomatic English;
- do not add, remove, generalize, narrow, explain, or strengthen scientific content;
- do not turn association into causation, possibility into certainty, or local evidence into a general claim.

## Execute the Workflow

### 1. Freeze protected content

Extract or mentally mark all protected elements before drafting:

- numbers, signs, ranges, units, uncertainty, and statistical values;
- equations, symbols, subscripts, superscripts, and variable names;
- citations, DOI, URLs, figure/table/equation identifiers, and cross-references;
- proper nouns, dataset/model/software names, abbreviations, and quoted text;
- negation, comparison direction, causal strength, modal strength, scope, and limitations.

Never normalize a protected element unless the user explicitly authorizes it.

### 2. Resolve terminology

Build or update a terminology ledger using the mandatory priority order:

`user-confirmed glossary > author-provided or official English > standard/specification > authoritative domain literature > pending candidate`

Lock an approved term across the document. Do not vary it merely to avoid repetition. Batch unresolved critical terms for human confirmation before translating dependent passages. Continue without interruption for ordinary wording choices and report them afterward only if materially uncertain.

### 3. Reconstruct meaning before prose

Recover the source propositions and their relations: contrast, cause, condition, purpose, sequence, exception, and limitation. Translate propositions rather than matching Chinese clauses word for word. Make implicit grammatical subjects explicit only when the source supports the choice.

### 4. Apply section-specific English

Use `references/section-language-matrix.md`. Choose tense and voice by rhetorical function, not by a rigid active-versus-passive rule. Keep Results observational and Discussion interpretive. Keep Methods reproducible. Keep Abstract claims compact but fully bounded.

### 5. Apply optional journal rules

When no target journal is supplied, use neutral international academic English and remain internally consistent in spelling and mechanics. When a journal is supplied, apply only verified official hard-language rules according to `references/journal-language-boundary.md`. Never imitate recurring phrases from published papers as a substitute for accurate translation.

### 6. Run integrity checks

Compare the English against the Chinese source sentence by sentence. Check protected elements, terminology, claim strength, logical relations, and omissions. When files are available, run:

```text
python scripts/audit_translation.py --source source.txt --translation translation.txt --termbase terms.tsv
```

Treat the script as a deterministic safety net, not proof that the translation is semantically correct.

## Stop Conditions

Pause and request human confirmation when any of these conditions holds:

- a core term has multiple materially different English meanings;
- the source is internally contradictory or grammatically ambiguous in a way that changes the scientific meaning;
- an official English name cannot be distinguished from an unofficial translation;
- the source appears to contain a numerical, unit, citation, or cross-reference error;
- fluent English would require adding an unstated causal link, actor, condition, or conclusion.

Do not silently select the most plausible scientific interpretation.

## Output

Return the English translation first. Then provide only the supporting items required by `references/human-review-and-output.md`: terminology decisions, questions requiring confirmation, and integrity warnings. Do not clutter a clean translation with generic style commentary.
