# Independent Translation Review

Use an independent review agent as a second-pass critic when a translation contains unfamiliar-domain terminology, rare technical expressions, multiple context-dependent senses, a complete abstract or manuscript section, or when the user explicitly requests review. This reviewer discovers risks; it does not replace source research or author decisions.

## Independence

Give the reviewer the Chinese source, English draft, section type, protected elements, and the relevant document-specific terminology subset. Do not provide the translator's stylistic rationale or tell the reviewer which wording it is expected to approve. The reviewer must compare source and translation rather than polish the English in isolation.

If an independent agent is unavailable, perform the same checklist as a clearly labelled second pass. Do not claim independent review in that case.

## Review Scope

Check, in this order:

1. **Scientific meaning** — actors, objects, mechanisms, conditions, direction, sequence, negation, comparison, causality, scope, and claim strength.
2. **Terminology** — domain identification, selected `sense_id`, units and definitions, official names, abbreviations, repeated-term consistency, and conflicts with higher-priority terminology.
3. **Protected content** — numbers, signs, ranges, units, equations, variables, citations, identifiers, model/software names, and statistical notation.
4. **Section language** — tense, voice, information order, and compression appropriate to the abstract, methods, results, discussion, or other section.
5. **English quality** — grammatical correctness, idiomatic academic phrasing, ambiguity introduced by syntax, and unnecessary repetition.

Do not use fluency as evidence of scientific correctness. Do not replace an unfamiliar term merely because a more common English phrase sounds smoother.

## Evidence Boundary

- User-confirmed, author-provided, official, standard, and authoritative-literature terminology retain their established priority.
- CNKI examples and frequency are corpus evidence. They can support usage comparison but cannot override a higher-priority source or establish author intent.
- If terminology research is incomplete, mark the item `evidence_needed`; do not invent a source, frequency, or consensus.
- If two translations remain scientifically plausible, mark `requires_user_confirmation=true`. The reviewer may recommend one candidate but may not lock it.

## Review Output

Return only actionable findings, ordered by severity:

| Field | Required content |
| --- | --- |
| `severity` | `blocker`, `major`, or `minor` |
| `source_span` | Smallest Chinese span that supports the finding |
| `draft_span` | Corresponding English span |
| `issue` | Concrete semantic, terminological, protected-content, section-language, or English-quality problem |
| `recommended_revision` | Minimal correction that preserves the source |
| `basis` | Source context, terminology authority, unit/definition, or section rule |
| `requires_user_confirmation` | `true` only when author intent or scientific meaning cannot be resolved |

Use these severities:

- `blocker`: could change scientific meaning, a protected value, the physical object/mechanism, or the conclusion and cannot be safely finalized.
- `major`: substantive mistranslation, inconsistent core terminology, or material claim-strength/section-function problem with a supported correction.
- `minor`: local grammar or phrasing issue whose correction does not change scientific meaning.

If no actionable issue remains, return `PASS` and optionally list no more than three verified strengths. Do not manufacture comments to justify the review stage.

## Integration

The primary translator evaluates every finding against the Chinese source and terminology hierarchy. Apply supported corrections, reject unsupported stylistic preferences, and consolidate all `requires_user_confirmation=true` findings into one user-review table. Run deterministic integrity checks after revisions, not before the final reviewer-driven corrections.
