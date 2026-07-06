# paper-navigator smoke tests

Date: 2026-07-06
Scope: GitHub release readiness for `paper-navigator`.

| ID | Prompt | Expected route | Pass criteria | Result |
| --- | --- | --- | --- | --- |
| S1 | Use paper-navigator to plan a literature search for an emerging research topic. | literature | Produces query families, search depth, candidate table fields, and stopping criteria. | PASS: `literature-discovery.md` defines search tiers, query families, candidate table fields, and stopping log. |
| S2 | Use paper-navigator to read this paper and tell me what claims it can support. | reading | Produces source-grounded reading card with can-support/cannot-support boundaries. | PASS: `paper-reading.md` defines source-grounded reading card and support boundaries. If no paper is provided, correct behavior is to request/source-mark missing input. |
| S3 | Use paper-navigator to audit these result tables before writing Results. | provenance | Separates verified artifacts, missing lineage, claim support, and risks. | PASS: `experiment-provenance.md` defines result ledger, verified status, claim support, boundary, missing artifact, and risk output. |
| S4 | Use paper-navigator to choose figures for a manuscript section. | figure | Defines figure contracts, chart choices, captions, and visual QA. | PASS: `figure-planning-qa.md` defines figure contract, chart selection, caption structure, and visual QA. |
| S5 | Use paper-navigator to draft a Results paragraph from evidence notes. | writing | Produces draft text plus claim-evidence-boundary notes and missing support. | PASS: `writing-claim-evidence.md` requires claim/evidence/boundary mapping, draft text, and missing support notes. If evidence notes are absent, correct behavior is scaffold/gap output. |
| S6 | Use paper-navigator to add citations to this paragraph. | citation | Segments claims and grades support instead of title-matching. | PASS: `citation-support.md` requires atomic claim segmentation and support grades; `SKILL.md` forbids title relevance as support. If no paragraph is provided, correct behavior is scaffold/gap output. |
| S7 | Use paper-navigator to review this manuscript before submission. | review | Returns severity-ranked blockers, major issues, and author decisions. | PASS: `review-risk-audit.md` defines blocker/major severity and author-decision outputs. If no manuscript is provided, correct behavior is missing-input scaffold. |
| S8 | Use paper-navigator to prepare responses to these reviewer comments. | rebuttal | Classifies comments by decision impact and avoids unsupported commitments. | PASS: `rebuttal-response.md` classifies comments by decision impact and forbids unsupported commitments; formal response letters remain confirmation-gated. |

## Agent review notes

- S1-S2 reviewed by read-only smoke agent Russell (`019f363f-09f6-7541-a1fa-70457789ffb4`). Excerpt: S1 routed to `literature` and found search tiers, query families, candidate table fields, and stopping log; S2 routed to `reading` and found source-grounded reading card fields plus can-support/cannot-support boundaries.
- S3-S4 reviewed by read-only smoke agent Poincare (`019f363f-5059-73e1-8f8d-7fb9522ef9f7`). Excerpt: S3 routed to `provenance` and found result ledger, verified status, claim support, boundary, missing artifact, and risk output; S4 routed to `figure` and found figure contract, chart selection, caption structure, and visual QA.
- S5-S6 reviewed by read-only smoke agent Pascal (`019f363f-c6d0-74a2-b03f-7dda3242056c`). Excerpt: S5 routed to `writing` and found claim/evidence/boundary mapping, draft text, and missing support notes; S6 routed to `citation` and found atomic claim segmentation, support grades, and the title-relevance prohibition.
- S7-S8 reviewed by read-only smoke agent Hegel (`019f3640-0817-7c61-943f-feeddd267d21`). Excerpt: S7 routed to `review` and found blocker/major severity plus author-decision outputs; S8 routed to `rebuttal` and found decision-impact classification plus unsupported-commitment guardrails.
- No release-blocking behavior issues were found.
- Several prompts intentionally omitted concrete source material; the expected safe behavior is to output missing-input scaffolds rather than fabricate papers, paragraphs, evidence notes, manuscripts, or reviewer comments.
