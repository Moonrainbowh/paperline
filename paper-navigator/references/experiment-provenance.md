# Experiment and Result Provenance

Use this file for computational experiments, empirical studies, statistical analyses, benchmarks, data processing, and result audits.

## Provenance Goal

The goal is not to make results look better. The goal is to know exactly what produced each result and what claims it can safely support.

## Artifact Inventory

```text
data/material files:
raw source:
processed source:
code/scripts:
configuration:
environment:
randomness or sampling:
run logs:
result tables:
figures:
model/checkpoint/output files:
notes or decisions:
```

## Result Ledger

| Result | Artifact | Method/config | Data/material scope | Metric or outcome | Verified? | Claim supported | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Checks

- Confirm source files exist before citing them as evidence.
- Compare hashes, row counts, sample counts, or document counts when multiple directories claim to contain the same data.
- Record preprocessing and exclusions.
- Separate training, selection, validation, and final evaluation where relevant.
- Keep failed, null, or negative results visible when they affect interpretation.
- Check whether reported metrics match the plotted or tabulated values.
- Identify whether results are descriptive, predictive, causal, mechanistic, diagnostic, or exploratory.

## Common Risks

| Risk | Why it matters |
| --- | --- |
| Data leakage | Inflates apparent performance or confidence. |
| Unclear split or sampling | Blocks reproducibility and external validity. |
| Selection on final evaluation | Makes final metrics optimistic. |
| Missing comparator | Weakens novelty or practical value. |
| Metric mismatch | Claim does not match what was measured. |
| Untracked preprocessing | Results cannot be audited. |
| Overgeneralization | Local evidence is written as universal. |

## Safe Output

If provenance is incomplete, write:

```text
Supported:
Partially supported:
Not yet supported:
Missing artifact:
Risk:
Next verification step:
```

Do not fabricate a clean lineage when files, logs, or decisions are missing.
