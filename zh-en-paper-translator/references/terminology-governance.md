# Terminology Governance

## Mandatory Priority

Resolve every technical term using this order:

1. **User-confirmed glossary** — Treat the approved English as locked.
2. **Author-provided or official English** — Use English supplied by the original author, official organization, product, dataset, software, project, or source document.
3. **Standard or specification** — Prefer the exact term used in the applicable national, international, industry, or reporting standard.
4. **Authoritative domain literature** — Select the established field term supported by relevant primary or authoritative sources.
5. **Pending candidate** — Mark an inferred translation as pending; do not present it as verified.

Never let a lower-priority source override a higher-priority decision without the user's approval.

## Ledger Schema

Use a Markdown table or a UTF-8 TSV file with these columns:

| Field | Meaning |
| --- | --- |
| `zh` | Exact Chinese source term |
| `en` | Approved or candidate English term |
| `status` | `locked`, `verified`, `pending`, or `rejected` |
| `authority` | `user`, `official`, `standard`, `literature`, or `inferred` |
| `source` | Source title, standard identifier, URL, DOI, file, or user decision |
| `forbidden` | Disallowed English alternatives separated by `|` |
| `notes` | Scope, capitalization, singular/plural, abbreviation, or context restrictions |

The audit script accepts the same column names. At minimum, provide `zh` and `en`.

## Locking Rules

- Apply `locked` and `verified` terms consistently whenever the same concept is meant.
- Do not replace a locked term with a stylistic synonym.
- Distinguish genuine synonyms from different technical concepts.
- Preserve official capitalization, hyphens, symbols, model names, and trademarked spellings.
- Define an abbreviation at first use in the relevant document scope, then use it consistently.
- Do not expand an abbreviation when its official form is intentionally unexpanded.
- Record context-specific translations separately when one Chinese term legitimately maps to different English concepts.

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

Ask the user to confirm the English term, then mark it `locked`. For ordinary lexical choices that do not change technical meaning, translate directly and do not interrupt.
