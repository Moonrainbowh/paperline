# Human Review and Output

## Review Gates

Use human review to resolve meaning, not to offload routine translation decisions.

### Gate 1: Critical terminology

Before translating dependent passages, batch only unresolved terms whose alternatives materially change technical meaning. Show context, alternatives, the difference, and a recommended choice with its authority level.

### Gate 2: Source ambiguity

Pause when the Chinese permits multiple scientific interpretations, contradicts itself, or appears to contain an error. Quote the smallest relevant Chinese span and explain the translation consequence. Do not repair the source silently.

For scanned or hybrid PDFs, also pause when OCR cannot reliably distinguish prose, table geometry, a number/unit, citation, or equation symbol. Treat OCR-derived tables and formulas as requiring human review even when no obvious error is detected.

### Gate 3: Final integrity review

After translation, list only material warnings: unresolved terminology, possible omissions, protected-element mismatches, claim-strength changes, or source ambiguities. A clean passage needs no ceremonial approval gate.

## Default Output Order

1. **English translation or final translated artifact(s)**
2. **Terminology decisions** — include only new, changed, pending, or source-backed terms
3. **Questions requiring confirmation** — omit when none
4. **Integrity warnings** — omit when none

For a full manuscript, provide the terminology ledger as a reusable companion artifact when the environment supports files. Return Markdown, DOCX, and LaTeX in the same source format. Return both an English PDF and an editable English DOCX for PDF input.

## Translation Boundary

Allowed without extra confirmation:

- reorder clauses within a sentence;
- select a natural grammatical subject supported by the source;
- split or merge sentences to recover readable English;
- replace Chinese rhetorical repetition with non-repetitive English when no proposition is lost;
- choose active or passive voice by information focus;
- adjust tense to the section and rhetorical function.

Not allowed without explicit confirmation:

- reorder paragraphs or manuscript sections;
- add explanations, mechanisms, motivations, limitations, citations, or conclusions;
- delete inconvenient repetition when it carries emphasis or a distinct proposition;
- correct data, units, equations, citations, or factual claims;
- strengthen or weaken uncertainty, causality, novelty, generality, or recommendation force;
- perform target-journal substantive rewriting.

## Final Semantic Checklist

Compare source and translation for:

- same actors, objects, conditions, direction, and sequence;
- same numbers, units, signs, intervals, and statistical qualifiers;
- same negation, exception, modality, causality, and claim strength;
- same citation and cross-reference attachment;
- same technical concept for every repeated term;
- no unexplained Chinese text remaining in the English body.
