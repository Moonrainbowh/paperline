---
name: paper-navigator
description: Use when planning, organizing, auditing, writing, reviewing, citing, visualizing, or revising academic research papers across disciplines. Trigger for literature discovery, paper reading, experiment/result provenance, claim-evidence mapping, manuscript sections, publication figures, citation support, pre-submission review, reviewer-style critique, revision planning, rebuttal drafting, research workflow orchestration, or evidence-grounded academic notes.
---

# Paper Navigator

Use this skill as a generic router and quality-control layer for academic paper work. It does not replace domain expertise or author decisions. It turns a research request into the smallest evidence-grounded artifact that can safely move the paper forward.

## Core Principles

- Put evidence before prose. Do not write strong claims without support from data, figures, code results, source text, or credible literature.
- Make boundaries explicit. State the study object, population or system, conditions, units, assumptions, scope, and extrapolation limits.
- Preserve provenance. Track where data, results, figures, citations, drafts, reviewer comments, and author decisions came from.
- Align figures with claims. Every figure should answer a specific research question or support a specific claim.
- Cite at claim level. Use citations to support exact statements, not broad topic similarity.
- Separate drafting from verification. A polished sentence is still unsafe if the evidence chain is weak.
- Route lightly, read narrowly. Use this `SKILL.md` for routing and gates; read only the reference files needed for the current task.
- Keep the skill general. Do not inherit field-specific examples, model names, datasets, journals, or manuscript details unless the user provides them for the current task.

## Quick Routing

First identify the user's desired artifact, then read the smallest relevant reference:

| User intent | Read |
| --- | --- |
| Unsure where to start, coordinate a paper workflow, choose the next safe action | `references/module-routing.md` |
| Define the project, evidence inventory, boundaries, and author decisions | `references/research-context-passport.md` |
| Find literature, build a search strategy, compare search depth, log reproducible queries | `references/literature-discovery.md` |
| Read papers, extract methods/results/figures, build source-grounded reading cards | `references/paper-reading.md` |
| Audit data, code, experiments, results, metrics, or computational provenance | `references/experiment-provenance.md` |
| Plan or review publication figures, chart types, captions, and visual QA | `references/figure-planning-qa.md` |
| Draft or revise manuscript sections with claim-evidence-boundary discipline | `references/writing-claim-evidence.md` |
| Add or audit citations, grade support, prepare reference metadata | `references/citation-support.md` |
| Run pre-submission review, reviewer-style critique, or revision triage | `references/review-risk-audit.md` |
| Classify reviewer/editor comments and draft response or rebuttal materials | `references/rebuttal-response.md` |

For multi-stage requests, default to:

`context -> literature -> reading -> provenance -> figures -> writing -> citation -> review -> rebuttal`

Skip stages that are irrelevant or already complete. If the user asks for a concrete artifact, enter that module directly and list any missing evidence instead of restarting the whole pipeline.

## Default Input Check

Before producing conclusions, try to identify:

- Research question and intended contribution.
- Study object, data source, population, system, setting, or corpus.
- Materials provided by the user: papers, PDFs, notes, data files, code, logs, figures, tables, drafts, comments, or target venue instructions.
- Evidence status: verified result, draft result, literature claim, author decision, reviewer claim, or missing source.
- Current stage: search, read, experiment, figure, write, cite, review, revise, rebut.
- Desired output: table, reading card, provenance ledger, figure plan, paragraph draft, citation map, risk review, response letter, or next-step plan.

If core inputs are missing, do not invent them. Produce a scaffold with explicit gaps or ask the user only when continuing would fabricate evidence or commit to an author-level decision.

## Confirmation Gates

Proceed with safe analysis, scaffolding, and auditing by default. Pause for explicit confirmation before actions that change evidence, policy, or shared state:

- `target venue`: final formatting, word limits, reference style, figure limits, reporting checklists, or required disclosures.
- `validation route`: new experiments, new data collection, new splits, re-analysis, statistical tests, sensitivity analysis, or metric recomputation.
- `data/code availability`: public release, repository creation, license, restricted access, embargo, or supplemental package contents.
- `author declarations`: author list, affiliations, funding, acknowledgements, conflict of interest, ethics, consent, CRediT, or AI/tool disclosure.
- `reviewer/editor comments`: formal response letters, rebuttal matrices, or revision commitments based on real editorial material.
- `global skill installation`: installing, overwriting, migrating, or publishing this skill outside the current working copy.

When a gate is triggered, output:

```text
Gate:
Decision needed:
Safe work I can do now:
Risk if assumed:
```

## Research Ledger

For substantial tasks, maintain a compact ledger in the answer or output file:

```text
Research task:
Current stage:
Artifacts checked:
Main claim:
Evidence:
Boundary:
Missing inputs:
Risks:
Next safe action:
```

For writing, review, or rebuttal tasks, always include `Main claim`, `Evidence`, `Boundary`, and `Risks`.

## Multi-Agent Protocol

Use read-only multi-agent work when the task contains independent material that can be reviewed in parallel, such as many papers, several datasets, multiple figure panels, or different reviewer perspectives.

Suitable uses:

- Multiple independent literature sources or databases.
- Several PDFs or long documents that need reading cards.
- Independent provenance checks over data, code, results, and figures.
- Pre-submission review from different perspectives: domain, method, statistics, writing, citation, and editorial risk.

Avoid multi-agent work when:

- The task is a small single-file edit.
- Later work depends on earlier results.
- Multiple agents would write the same file or mutate the same artifact.

Require subagents to return structured output:

```text
agent_role:
scope:
inputs_checked:
findings:
evidence:
uncertainties:
conflicts:
recommended_action:
sources_or_files:
```

The main agent must merge only verified evidence, abstract rules, and source anchors. Mark conflicts as `needs manual check` instead of silently choosing a side.

## Output Defaults

Use the user's language unless the requested artifact has a different target language. For academic prose, distinguish:

- Draft text that can be edited into a manuscript.
- Evidence notes that should not be pasted into the manuscript.
- Missing evidence that blocks a strong claim.
- Author decisions that require confirmation.

Prefer tables for comparisons, ledgers for provenance, and short next-step lists for workflow routing.

## Quality Floor

- Do not fabricate results, citations, DOI, source text, reviewer comments, author decisions, or journal rules.
- Do not use title relevance as citation support.
- Do not smooth over weak evidence with confident language.
- Do not let target-journal style override evidence boundaries.
- Do not copy upstream skill text, copyrighted templates, figures, captions, or reviewer responses; abstract workflow ideas and write original guidance.
- Do not install, publish, or overwrite global skill locations unless the user explicitly confirms that action.
