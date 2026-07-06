# Literature Discovery

Use this file for literature searches, related-work planning, evidence discovery, and reproducible search logs.

## Search Depth Tiers

| Tier | Use when | Output |
| --- | --- | --- |
| `quick` | User needs orientation or a few seed sources. | 5-10 candidate sources plus query notes. |
| `standard` | User is preparing related work or background. | Search strategy, candidate table, screening notes. |
| `deep` | User needs broad coverage or a defensible review base. | Multi-source search log, inclusion logic, method clusters. |
| `audit` | User must justify completeness or verify citation support. | Reproducible query ledger, excluded sources, uncertainty list. |

Ask before starting long network-heavy searches. If browsing is required, follow the active web-access rules and prioritize primary sources.

## Query Planning

Create query families rather than one query:

```text
core concept:
method terms:
application/context terms:
outcome terms:
synonyms:
negative terms:
date range:
source types:
```

## Candidate Table

Use this structure unless the user requests another format:

| ID | Source | Year | Type | Why it matters | Evidence target | Access/status | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

`Evidence target` should say what the source might support: background, method, dataset, metric, mechanism, limitation, or competing claim.

## Search Log

Record enough detail to reproduce the search:

```text
date:
source/database:
query:
filters:
results inspected:
included:
excluded:
reason for stopping:
```

## Screening Rules

- Prefer primary papers, official datasets, standards, and source documentation.
- Mark reviews as background unless they directly support a review-style statement.
- Do not treat a title or abstract match as enough support for a specific claim.
- Keep negative or conflicting evidence visible.
- Separate "found" from "read" and "read" from "supports this claim".

## Handoff

After discovery, route to:

- `paper-reading.md` for close reading,
- `citation-support.md` for claim-level support,
- `writing-claim-evidence.md` for related-work synthesis.
