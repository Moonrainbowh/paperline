# Terminology Governance

## Mandatory Priority

Resolve every technical term using this order:

1. **User-confirmed glossary** — Treat the approved English as locked.
2. **Author-provided or official English** — Use English supplied by the original author, official organization, product, dataset, software, project, or source document.
3. **Standard or specification** — Prefer the exact term used in the applicable national, international, industry, or reporting standard.
4. **Authoritative domain literature** — Select the established field term supported by relevant primary or authoritative sources.
5. **Pending candidate** — Mark an inferred translation as pending; do not present it as verified.

Never let a lower-priority source override a higher-priority decision without the user's approval.

## Bundled Domain Reference

For machine learning in geotechnical engineering, geotechnical analogue materials, and salt-cavern construction, read `literature/geotechnical-domain-termbases-guide.md` and load the matching scoped TSV pack. For broader salt-cavern storage/operation, hydrogen storage, compressed-air energy storage, and general geotechnical AI/ML, use `literature/salt-cavern-geotech-ai-guide.md` and `termbases/salt-cavern-geotech-ai.tsv`. No bundled row is automatically `locked` for a new manuscript.

Create a document-specific subset rather than passing the entire broad termbase to the audit script. Apply higher-priority user and author choices over that subset, record the override source, and keep the original reference pack unchanged unless the user explicitly asks to update the reusable resource.

## Ledger Schema

Use a Markdown table or a UTF-8 TSV file with these columns:

| Field | Meaning |
| --- | --- |
| `zh` | Exact Chinese source term |
| `en` | Approved or candidate English term |
| `status` | `locked`, `verified`, `recommended`, `context-dependent`, `pending`, or `rejected` |
| `authority` | `user`, `official`, `standard`, `literature`, `corpus`, or `inferred` |
| `source` | Source title, standard identifier, URL, DOI, file, or user decision |
| `forbidden` | Disallowed English alternatives separated by `|` |
| `notes` | Scope, capitalization, singular/plural, abbreviation, or context restrictions |

For a multi-sense or personal termbase, also use the optional fields below. Read `polysemy-and-personal-termbases.md` for the selection rules.

| Field | Meaning |
| --- | --- |
| `sense_id` | Stable identifier for one technical sense of the Chinese form |
| `domain` | Broad field such as `geotechnical-ml` or `physical-modelling` |
| `context` | Short definition of when this English term is valid |
| `context_cues` | Non-exhaustive source-language cues separated by `|` |
| `selection` | Blank in a master termbase; `selected` in a document-specific subset |
| `decision_scope` | `occurrence`, `paragraph`, `section`, `document`, `project`, or `personal` |
| `confirmed_by` | User/author identifier or `context-inference` |
| `confirmed_at` | ISO date for a human-confirmed decision |

The audit script accepts the same column names. At minimum, provide `zh` and `en`.

## Locking Rules

- Apply `locked` and `verified` terms consistently whenever the same concept is meant.
- Do not replace a locked term with a stylistic synonym.
- Distinguish genuine synonyms from different technical concepts.
- Preserve official capitalization, hyphens, symbols, model names, and trademarked spellings.
- Define an abbreviation at first use in the relevant document scope, then use it consistently.
- Do not expand an abbreviation when its official form is intentionally unexpanded.
- Record context-specific translations separately when one Chinese term legitimately maps to different English concepts.
- Give each distinct concept a stable `sense_id`; never collapse different concepts merely because their Chinese surface form is identical.
- In a master termbase, retain all supported senses with blank `selection`. In the document-specific audit subset, mark exactly one applicable sense `selected` when the same `zh` has different English realizations.
- A contextual AI decision may select a sense for the current occurrence or document without promoting it to a personal `locked` decision.
- Reuse a confirmed decision only within its recorded `decision_scope`. Ask again only when a later occurrence falls outside that scope or contradicts its context rule.

## Human-Confirmation Trigger

Treat a term as critical and pause when an alternative would change any of these:

- physical object, mechanism, material, geological structure, process stage, model, metric, or statistical meaning;
- causal interpretation or evidence strength;
- standard compliance or reproducibility;
- distinction between input, state, control, label, observation, or prediction;
- scope of an acronym or named method.

Batch questions in this form:

| Chinese term | Candidate A | Candidate B | Context | Difference affecting meaning | Recommended choice and basis |
| --- | --- | --- | --- | --- | --- |

Ask the user to confirm the English term, then mark it `locked` at the narrowest valid scope. For ordinary lexical choices that do not change technical meaning, translate directly and do not interrupt. During terminology-library construction, defer these questions to one final review batch. During manuscript translation, continue unrelated passages but do not finalize a meaning-dependent passage until the sense is resolved.
