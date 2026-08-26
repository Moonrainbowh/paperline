# Geotechnical Domain Termbases

This resource contains three scoped Chinese-to-English terminology packs:

- `termbases/geotechnical-machine-learning.tsv` — machine learning applied to geotechnical engineering;
- `termbases/geotechnical-analogue-materials.tsv` — similitude, model materials, mix design, testing, and full-field measurement;
- `termbases/salt-cavern-construction.tsv` — geology, solution mining, leaching strings, blanket control, cavern geometry, monitoring, and construction evaluation.

The shared evidence catalogue is `geotechnical-domain-termbases-sources.tsv`. These packs are reusable translation references, not user-confirmed glossaries and not systematic reviews.

## Load Only What the Manuscript Needs

1. Load the relevant scoped pack before the older broad `salt-cavern-geotech-ai.tsv` pack.
2. Select rows that match the manuscript domain, section, definitions, units, and local context.
3. Overlay the user/project glossary, author-provided English, official names, and applicable standards using the mandatory priority order.
4. Build a document-specific subset and mark exactly one row `selection=selected` when a repeated Chinese form has materially different English senses.
5. Do not enforce every row in a master pack against every document.

The older broad pack remains useful for salt-cavern storage operation, hydrogen storage, compressed-air energy storage, and general geotechnical AI terms outside these three focused packs.

## Evidence and Status

- `verified`: directly supported by an official/standard source or a strong title-level/domain usage match.
- `recommended`: source-supported preferred translation, but still subordinate to user, author, official, and applicable standard terminology.
- `context-dependent`: multiple legitimate translations exist; use `sense_id`, `context`, `context_cues`, units, definitions, and section-level evidence to choose.
- `pending`: candidate requiring stronger evidence or human review before reuse.
- `locked`: reserved for an explicit user/author decision or an exact official name in its valid scope.

Metadata or title verification does not prove that a paid full text defines a term. Do not promote a title-supported candidate to a quoted definition without inspecting the source text.

## CNKI Boundary

On 2026-08-26 the CNKI translation homepage could be reached inconsistently, while the query endpoint returned authorization or human-verification barriers. No reliable term-frequency values were obtained. Therefore:

- every current row uses `cnki_frequency=not-collected`;
- `cnki_evidence` records the access boundary;
- no general search-result count is substituted for CNKI frequency;
- a later human-controlled CNKI session may add query, subject, frequency, example sentence, source title, and retrieval date without replacing higher-priority terminology evidence.

## High-Risk Sense Groups

Always resolve these from context rather than the Chinese surface form alone:

| Domain | Chinese form | Distinctions |
| --- | --- | --- |
| Geotechnical ML | 特征 | ML input `feature` vs material `property` |
| Geotechnical ML | 残差 | `PDE residual` vs `prediction residual` |
| Geotechnical ML | 准确率 / 精确率 | classification `accuracy` vs `precision` |
| Geotechnical analogue materials | 相似材料 | Chinese-paper `similar material` vs international `analogue material` vs `rock-like material` |
| Geotechnical analogue materials | 相似比 | author-defined `similarity ratio` vs quantity-specific `scale factor` |
| Geotechnical analogue materials | 渗透率 / 渗透系数 | `intrinsic permeability` for m², D, mD vs `hydraulic conductivity` for m/s |
| Geotechnical analogue materials | 精度 | closeness to truth `accuracy` vs repeat-measurement `precision` |
| Salt-cavern construction | 造腔 | engineering activity `cavern construction` vs geometry evolution `cavern development` |
| Salt-cavern construction | 溶腔 | verb `leach a cavern` vs noun `solution-mined cavern` |
| Salt-cavern construction | 采卤 / 排卤 | product `brine production`, process return `brine withdrawal`, commissioning `debrining` |
| Salt-cavern construction | 夹层 | mechanical `interlayer` vs stratigraphic `interbed` |
| Salt-cavern construction | 气垫 | leaching `gas blanket`, never storage-operation `cushion gas` by default |
| Cross-domain | 扩腔 / 扩容 | cavern geometry `cavern enlargement` vs rock-mechanics `dilatancy` |

If the evidence is sufficient, the translator selects the sense directly and records `confirmed_by=context-inference` at the narrowest valid scope. If two senses remain plausible and would change scientific meaning, translate independent content, add the alternatives to one consolidated review table, and ask once before finalizing the affected text.

## Validation

Run from the repository root:

```text
python zh-en-paper-translator/scripts/validate_domain_termbases.py
```

The validator checks schema, source IDs, DOI shape, duplicate senses, status/authority values, CNKI evidence markers, minimum pack sizes, and source requirements.
