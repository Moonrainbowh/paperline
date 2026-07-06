# Figure Planning and Visual QA

Use this file for planning, creating, reviewing, or captioning academic figures.

## Figure Contract

Before choosing a chart, define:

```text
figure_id:
claim_or_question:
audience:
data/material:
variables:
comparison:
required annotation:
target size or venue constraints:
caption message:
```

If the claim is unclear, propose a figure contract before plotting.

## Chart Selection

| Goal | Prefer | Avoid |
| --- | --- | --- |
| Show relationship | scatter, line with uncertainty, model fit with residuals | decorative 3D, unlabelled trend lines |
| Compare groups | dot/strip, box, violin, interval plot, table if few values | mean-only bars for small samples |
| Show change over ordered variable | line, slopegraph, heatmap for dense grids | connecting unordered categories |
| Show composition | stacked bar or table when categories are few | pie charts for precise comparison |
| Show method/workflow | clean schematic with inputs, process, outputs, evidence links | ornamental diagrams with no claim |
| Show uncertainty | confidence/credible intervals, bootstrap bands, distribution plots | hiding variance behind single numbers |

## Caption Structure

```text
Panel or figure purpose:
Data/material scope:
Encoding:
Key observation:
Statistical or measurement note:
Boundary:
```

Do not let a caption claim more than the figure and underlying evidence show.

## Visual QA

Check before calling a figure ready:

- text legible at target size,
- axes labelled with units where applicable,
- legend clear and not overlapping,
- colors distinguishable and grayscale-tolerant when needed,
- annotations do not hide data,
- panel labels consistent,
- values match source table,
- uncertainty/statistics described,
- file format and resolution suitable for the next use,
- caption matches the actual visual.

## Review Output

```text
Figure:
Claim served:
Chart choice:
Strengths:
Issues:
Required fixes:
Caption risk:
Ready status:
```
