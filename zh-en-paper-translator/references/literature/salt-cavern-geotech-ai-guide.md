# Salt-Cavern and Geotechnical-AI Reference Pack

## Contents

- [Purpose](#purpose)
- [Files](#files)
- [How to use the termbase](#how-to-use-the-termbase)
- [Evidence boundary](#evidence-boundary)
- [Search ledger](#search-ledger)
- [Coverage map](#coverage-map)
- [Maintenance](#maintenance)

## Purpose

Use this pack as a source-grounded starting point when translating Chinese manuscripts about salt-cavern storage or the intersection of artificial intelligence and geotechnical engineering. It is a reference pack, not a universal glossary and not a substitute for the author's own terminology.

Apply the mandatory precedence unchanged:

`user-confirmed glossary > author-provided or official English > standard/specification > authoritative domain literature > pending candidate`

## Files

- `salt-cavern-geotech-ai-sources.tsv`: structured source catalogue with standards and DOI-verified articles.
- `../termbases/salt-cavern-geotech-ai.tsv`: UTF-8 bilingual terminology ledger accepted by `scripts/audit_translation.py`.

## How to use the termbase

1. Detect the manuscript's actual domain and concepts.
2. Load only rows relevant to those concepts; do not force the complete broad termbase onto every manuscript.
3. Overlay any user-confirmed or author-provided glossary and mark those document-specific choices `locked`.
4. Treat `verified` as a source-supported default, not permission to ignore context.
5. Treat `pending` as a human-review candidate. If choosing among alternatives changes the physical object, mechanism, variable, or claim, ask the user before translating dependent text.
6. Export the document-specific subset as a separate TSV and pass that subset to `audit_translation.py`.

The `source_id` column maps every term to one or more entries in the source catalogue. Multiple IDs are separated by `|`.

## Evidence boundary

- `official_page_verified`: the standard title and scope were checked on the issuing organization's page; the pack does not reproduce paywalled standard definitions.
- `doi_verified`: title, venue, year, and DOI were resolved through Crossref on 2026-08-09.
- `abstract_checked`: the publisher abstract or official article page was also inspected for the term or usage.
- `metadata_only`: the paper identity is verified, but its full text was not read page by page. Such a row supports discovery and terminology triage, not a manuscript claim about the paper's results.

The source catalogue is a curated v1 seed database, not a systematic review and not a claim of exhaustive coverage.

## Search ledger

Search date: 2026-08-09.

| Query ID | Database | Query | Hit count | Retrieved | Notes |
| --- | --- | --- | ---: | ---: | --- |
| Q01 | OpenAlex | `salt cavern underground gas storage geomechanical stability creep` | not captured | 12 requested | One Windows GBK console error after partial output; rerun strategy used UTF-8. |
| Q02 | OpenAlex | `underground hydrogen storage salt caverns review` | not captured | 12 requested | Review and classic seeds retained after DOI screening. |
| Q03 | OpenAlex | `compressed air energy storage salt cavern stability` | not captured | 12 requested | Non-salt electrical-storage reviews excluded. |
| Q04 | OpenAlex | `solution mining salt cavern shape sonar survey` | not captured | 15 requested | Construction, shape, seepage, and monitoring seeds retained. |
| Q05 | OpenAlex | `salt cavern hydrogen storage thermomechanical cycling integrity` | not captured | 15 requested | Hydrogen-specific cycling and integrity candidates retained. |
| Q06 | OpenAlex | `salt cavern natural gas storage creep dilatancy permeability` | not captured | 15 requested | Creep, dilatancy, seepage, and rock-salt records retained. |
| Q07 | OpenAlex | `machine learning geotechnical engineering surrogate model physics informed` | not captured | 12 requested | Geotechnical ML terminology seeds retained. |
| Q08 | OpenAlex | `geotechnical engineering machine learning review uncertainty explainable artificial intelligence` | not captured | 15 requested | Broad civil-only or unrelated AI records excluded. |
| Q09 | Web search | Official API RP 1170, ASTM D653, and ISO/IEC 22989 pages | not applicable | 3 standards | Used only for standard identity and scope. |
| Q10 | Crossref REST API | Batch DOI lookup for retained records | 34 requested | 34 resolved | One initially suggested Ozarslan DOI was rejected because Crossref resolved it to a different paper; the correct DOI was then verified. |

Deduplication order: DOI exact match, then normalized title plus year and first author. Conference material, reports without stable article metadata, generic energy-storage reviews, and results unrelated to salt caverns or geotechnical AI were excluded from this v1 pack.

## Coverage map

| Area | Representative source IDs |
| --- | --- |
| General safety and integrity | SC01, S01 |
| Gas pressure and operation | SC02, SC06 |
| Dilatancy, tensile failure, and cyclic criteria | SC03–SC05, SC07 |
| Compressed-air energy storage | SC08, SC16 |
| Hydrogen storage and cycling | SC10–SC15 |
| Shape, horizontal caverns, and deep formations | SC17–SC19 |
| Seepage, construction, solution mining, and rock salt | SC20–SC24 |
| AI and neural networks in geotechnics | AI01, AI02, AI10, S03 |
| Constitutive and physics-informed learning | AI03–AI05, AI07 |
| Uncertainty, data fusion, and surrogate models | AI06, AI08, AI09 |

## Maintenance

- Add a new source only after resolving its DOI or checking the official standard page.
- Never upgrade `metadata_only` to full-text evidence without opening and checking the paper.
- Add term variants as separate context-scoped rows when the same Chinese form has different technical meanings.
- Promote a `pending` entry to `verified` only with a supporting standard, official source, or authoritative domain paper.
- Promote an entry to `locked` only after the user or author confirms it for the manuscript at hand.
