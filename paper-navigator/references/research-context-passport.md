# Research Context Passport

Use this file to establish a reusable project ledger before writing, reviewing, searching deeply, or making claims.

## Purpose

The passport prevents a paper workflow from becoming a pile of polished but unsupported text. It records what the work is about, what evidence exists, what remains undecided, and what must not be assumed.

## Minimal Passport

```text
Project title or working label:
Research question:
Intended contribution:
Study object or system:
Data/materials:
Methods or intervention:
Comparators or baselines:
Evaluation criteria:
Main claims:
Evidence for each claim:
Known boundaries:
Missing inputs:
Author decisions:
Target venue status:
Risks:
Next safe action:
```

## Evidence Types

Tag each item with one status:

| Status | Meaning |
| --- | --- |
| `verified-artifact` | Checked in a file, source, log, table, figure, or code output. |
| `user-provided` | Stated by the user but not independently verified in this turn. |
| `literature-supported` | Supported by an identified source. |
| `draft-only` | Present in draft text but not yet supported. |
| `author-decision-needed` | Cannot be inferred by the agent. |
| `missing` | Needed for a strong claim but unavailable. |

## Boundary Checks

Always identify:

- population, system, material, corpus, task, or setting,
- time range or data collection window,
- inclusion/exclusion criteria,
- units and transformations,
- assumptions,
- external validity limits,
- whether the paper claims explanation, prediction, description, method, resource, or review.

## Decision Locks

Do not infer:

- author list or contribution order,
- affiliations, funding, ethics, consent, or conflicts,
- public release policy for data/code,
- final target venue requirements,
- formal response commitments to reviewers,
- acceptability, safety, clinical, legal, or engineering conclusions beyond the provided evidence.

## Output Use

For short tasks, include the passport inline. For longer projects, create or update a local Markdown ledger only when the user asks for a persistent artifact.
