# paper-navigator skill

`paper-navigator` is a generic Codex skill for academic paper workflows. It routes research tasks across literature discovery, paper reading, evidence and provenance auditing, figure planning, manuscript writing, citation support, pre-submission review, and rebuttal planning.

This repository contains workflow guidance only. It does not contain datasets, model checkpoints, manuscript drafts, reviewer comments, private notes, or paper-specific intermediate artifacts.

## What it is for

- Planning a paper workflow from rough research materials.
- Building claim-evidence-boundary maps before writing.
- Keeping literature discovery and reading source-grounded.
- Auditing data, code, result, figure, and citation provenance.
- Planning publication figures and captions around claims.
- Running pre-submission risk reviews.
- Structuring revision and rebuttal work from real comments.

## Repository layout

```text
paper-navigator-skill/
  README.md
  LICENSE
  .gitignore
  validation-smoke-tests.md
  dist/
    paper-navigator-skill-v1.0.0.zip
    paper-navigator-skill-v1.0.0.zip.sha256
  paper-navigator/
    SKILL.md
    agents/
      openai.yaml
    references/
      citation-support.md
      experiment-provenance.md
      figure-planning-qa.md
      literature-discovery.md
      module-routing.md
      paper-reading.md
      rebuttal-response.md
      research-context-passport.md
      review-risk-audit.md
      writing-claim-evidence.md
```

## Installation

Copy the `paper-navigator` folder into a local Codex skills directory, then restart Codex.

Common locations:

```powershell
~\.codex\skills\paper-navigator
```

or:

```powershell
~\.agents\skills\paper-navigator
```

After restart, trigger it with prompts such as:

```text
Use paper-navigator to plan the next safe step for this manuscript.
Use $paper-navigator to plan the next safe step for this manuscript.
Use paper-navigator to audit the claim-evidence chain in this Results draft.
Use paper-navigator to prepare a rebuttal plan from these reviewer comments.
```

## Release archive verification

The `dist/` directory contains a versioned zip archive and a SHA-256 checksum. To verify the archive on Windows:

```powershell
$zip = "dist\paper-navigator-skill-v1.0.0.zip"
Get-FileHash -Algorithm SHA256 $zip
Get-Content "$zip.sha256"
```

The hash printed by `Get-FileHash` should match the first field in `paper-navigator-skill-v1.0.0.zip.sha256`.

`validation-smoke-tests.md` records route-level smoke tests for the major workflow paths. These smoke tests validate that the skill routes to the expected reference modules and preserves evidence-boundary behavior.

## Compatibility notes

- Browser search, web extraction, and multi-agent review depend on the host agent environment.
- When those tools are unavailable, use the same workflow sequentially: gather sources, build reading cards, audit provenance, then synthesize.
- The skill does not require bundled datasets, model files, API keys, or private materials.

## Design principles

- Evidence before prose.
- Explicit research boundaries.
- Provenance for data, code, results, figures, citations, drafts, and decisions.
- Claim-level citation support.
- Figures serve claims.
- Confirmation gates for target venue, validation route, data/code release, author declarations, reviewer responses, and global installation.

## Design inspirations and attribution

This repository is original workflow text. It was informed by public research-skill patterns but does not redistribute upstream source code, scripts, long-form templates, datasets, manuscript text, figures, or reviewer-response templates.

| Source | What was abstracted |
| --- | --- |
| [`Yuan1z0825/nature-skills`](https://github.com/Yuan1z0825/nature-skills) | Modular research skills for writing, figures, citations, reading, data, and responses. |
| [`Imbad0202/academic-research-skills`](https://github.com/Imbad0202/academic-research-skills) | End-to-end academic workflow structure, quality gates, provenance thinking, and claim auditing. |
| [`O0000-code/paper-search-pro`](https://github.com/O0000-code/paper-search-pro) | Multi-source literature discovery, search-depth tiers, metadata outputs, and reproducible search logs. |
| [`Haojae/scipilot-figure-skill`](https://github.com/Haojae/scipilot-figure-skill) | Scientific figure planning, chart-type selection, visual QA, and publication-oriented figure discipline. |
| [`SNL-UCSB/paper-writing-skill`](https://github.com/SNL-UCSB/paper-writing-skill) | Structured paper-writing flow from ideas to sections, with emphasis on claims and section moves. |
| [`M1n-n9/paper-lifecycle`](https://github.com/M1n-n9/paper-lifecycle) | Review/revision/rebuttal lifecycle thinking and reviewer-style risk diagnosis. |
| [`kesslerio/academic-deep-research-clawhub-skill`](https://github.com/kesslerio/academic-deep-research-clawhub-skill) | Deep research framing, evidence grading, and review-oriented synthesis patterns. |

## Reuse boundary

- This repository contains original workflow guidance for `paper-navigator`.
- It does not copy upstream files, scripts, prompts, templates, datasets, figures, captions, or long passages.
- Check upstream licenses separately before reusing any upstream material directly.
- Treat unlicensed or non-commercial upstream projects as inspiration only unless you obtain permission.

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE).
