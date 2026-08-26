# Polysemy and Personal Termbases

## Purpose

Preserve multiple technical senses for the same Chinese surface form and let context determine which English realization applies. Separate reusable candidate knowledge from document-specific selection and human-confirmed personal preferences.

## Storage Layers

Use three overlays, from broadest to narrowest:

1. **Shared domain termbase** — source-backed senses useful across users.
2. **Personal termbase** — choices explicitly confirmed by one author/user.
3. **Project/document termbase** — manuscript-specific names, variables, stages, and selected senses.

Do not edit a shared row to represent a personal preference. Add a higher-priority overlay row and retain provenance.

## Sense Model

The same `zh` value may appear in multiple rows when the underlying concepts differ. Every such row must have:

- a unique `sense_id`;
- a concise `context` defining the concept rather than merely repeating the English term;
- useful but non-exclusive `context_cues`;
- independent source/provenance;
- blank `selection` in the reusable master termbase.

Example:

| zh | en | sense_id | context | context_cues |
| --- | --- | --- | --- | --- |
| 扩容 | dilatancy | rock-damage-dilatancy | Inelastic volumetric expansion of geomaterial | 体积应变\|损伤\|扩容准则 |
| 扩容 | cavern enlargement | cavern-construction-enlargement | Deliberate increase in cavern dimensions or volume | 水溶\|注水\|采卤\|腔体体积 |

Context cues guide retrieval; they are not a keyword-only classifier.

## Contextual Selection

When translating an occurrence:

1. Retrieve every row matching the exact Chinese form and relevant aliases.
2. Examine the sentence, adjacent paragraph, section purpose, definitions, variables, figure/table labels, and project glossary.
3. Eliminate senses contradicted by the physical object, mechanism, unit, operation, or grammatical role.
4. Select directly when one sense is materially better supported. Record `selection=selected`, `confirmed_by=context-inference`, and the narrowest defensible `decision_scope` in the document-specific subset.
5. If materially different senses remain plausible, defer the affected span, continue independent work, and ask one batched question with the smallest sufficient context.

Do not use a numeric confidence threshold as a substitute for semantic evidence. The reason for selection must be inspectable.

## Question and Persistence Rules

- Ask once per unresolved sense and valid scope, not once per occurrence.
- Reuse a document-scoped decision throughout that document when the concept is unchanged.
- Reuse a project- or personal-scoped decision only when the stored context rule still matches.
- Ask again when a later occurrence has a different physical object, mechanism, unit, definition, or explicitly conflicting usage.
- Store an AI contextual choice separately from a human-confirmed `locked` preference.
- During termbase creation, collect all conflicts first and present one final review table.

Final review fields:

| zh | sense candidates | evidence and frequency | context distinction | recommendation | requested decision scope |
| --- | --- | --- | --- | --- | --- |

## Audit Subset

Never pass an unresolved multi-sense master termbase directly to deterministic term enforcement. Build a document-specific subset:

- keep only relevant terms;
- for a repeated `zh` with different `en` values, mark exactly one row `selection=selected` for the applicable sense;
- omit unrelated senses or leave them unselected only if the audit tool is expected to report the ambiguity;
- retain `sense_id`, source, and decision scope for traceability.

`audit_translation.py` reports `TERM_SENSE_UNRESOLVED` when the source contains a Chinese form mapped to multiple English values without exactly one selected row.
