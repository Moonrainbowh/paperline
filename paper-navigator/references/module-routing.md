# Module Routing

Use this file when the user asks what to do next, gives a mixed research request, or asks for a full paper workflow.

## Routing Order

1. Identify the desired artifact: search log, reading card, result audit, figure plan, manuscript text, citation map, review report, response letter, or next-step plan.
2. Identify the current stage: context, literature, reading, provenance, figure, writing, citation, review, or rebuttal.
3. Check available evidence: user notes, papers, data, code, logs, figures, tables, draft text, author decisions, venue rules, or reviewer comments.
4. Choose one primary module and list any follow-up modules.
5. Produce the smallest safe artifact that moves the work forward.

## Decision Table

| Signal | Primary module | Typical output |
| --- | --- | --- |
| "where should I start", "organize this project", "paper workflow" | context | research ledger, missing inputs, next safe action |
| "find papers", "literature review", "related work" | literature | search strategy, query log, candidate table |
| "read this paper", "extract methods", "what can this source support" | reading | source-grounded reading card |
| "audit results", "data/code/logs", "metrics", "reproduce" | provenance | artifact lineage, result table, risk flags |
| "make a figure", "which chart", "caption", "visual check" | figure | figure contract, chart choice, QA list |
| "write introduction/method/results/discussion", "polish section" | writing | section draft plus claim-evidence-boundary notes |
| "add citations", "verify references", "support this sentence" | citation | segmented claims, support grades, metadata checks |
| "pre-submission", "act as reviewer", "will this be rejected" | review | risk audit, decision blockers, revision priorities |
| "reviewer comments", "rebuttal", "response letter" | rebuttal | comment classification, response strategy, draft replies |

## Multi-Module Defaults

- Full workflow: `context -> literature -> reading -> provenance -> figure -> writing -> citation -> review`.
- Existing results but no draft: `provenance -> figure -> writing -> citation -> review`.
- Existing draft but weak support: `writing -> citation -> review`, with provenance checks for result claims.
- Reviewer comments: `rebuttal`, with `review` and `provenance` checks when comments challenge method, data, results, statistics, or claims.

## Gate Check

Before routing, check whether the request asks you to decide or execute:

- target venue formatting or disclosures,
- new analysis or validation,
- data/code release policy,
- author declarations,
- formal response to real reviewers,
- global installation or publication of a skill.

If yes, state the gate and continue only with safe scaffolding unless the user confirms.

## Routing Output Template

```text
Routing:
- Primary module:
- References to read:
- Current stage:
- Evidence available:
- Gate status:
- Multi-agent useful:

Artifact I can produce now:
- ...

Missing inputs:
- ...

Next safe action:
- ...
```
