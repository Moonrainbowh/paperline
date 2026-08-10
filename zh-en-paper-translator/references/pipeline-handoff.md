# Formal Pipeline Handoff

Use this reference only when the user supplies a formal paperline full-manuscript handoff or explicitly selects `pipeline` mode. Ordinary standalone translation remains available without this gate.

## Contents

1. Mode Decision
2. Required Pipeline Package
3. Preflight
4. Translation Boundary
5. Change Handling
6. Pipeline Output Audit

## Mode Decision

Select exactly one mode:

- `standalone`: translate a passage, section, or manuscript directly from the user. Do not require a paper-writing status or target journal.
- `pipeline`: translate the exact full Chinese manuscript carried by a formal handoff package. Enforce the version and lock checks below.

Do not infer `pipeline` from file length or format alone. Do not relabel a supplied formal handoff as `standalone` to avoid a failed gate.

## Required Pipeline Package

Validated JSON packages must use the exact field names below. They reject duplicate keys, non-standard `NaN`/`Infinity` constants, and syntactically finite numbers such as `1e999` that overflow to a non-finite runtime value. If the user supplies an equivalent non-JSON record, normalize it explicitly into this schema before validation; aliases inside the JSON package are not accepted.

The enclosing formal wrapper must also contain a non-empty string `handoff_id`, the exact `paper-navigator → zh-en-paper-translator` stage/Skill mapping, an offset-aware `created_at` whose calendar date is not later than validation, exactly one Chinese S7 source artifact whose identity/path/version/hash fields are non-empty strings, the matching author lock ID in `author_decisions`, and empty `open_questions`/`blockers`. The author-lock timestamp follows the same no-future-date rule.

```text
handoff_type: formal-full-manuscript-translation
handoff_package_schema_version:
handoff_status: locked
chinese_manuscript_status: S7
manuscript_id:
manuscript_revision:
chinese_manuscript_sha256:
author_lock_record:
  lock_id:
  status: locked
  confirmed_by:
  confirmed_at:
  manuscript_id:
  manuscript_revision:
  manuscript_sha256:
locked_thesis_and_contributions:
terminology_ledger:
locked_numbers_and_units:
locked_claim_boundaries:
locked_citations_and_cross_references:
unresolved_blockers: []
target_journal_status: contract-confirmed
target_journal:
target_journal_article_type:
target_journal_decision_file:
target_journal_decision_schema_version:
target_journal_decision_sha256:
target_journal_contract_file:
target_journal_contract_version:
target_journal_contract_sha256:
target_journal_selection_evidence_version:
target_journal_writing_profile_evidence_id:
```

Require `S7`, `handoff_status: locked`, an exact manuscript ID/revision/SHA-256, a structured author lock record tied to those bytes, all lock ledgers, a complete confirmed target-journal group, and no unresolved blockers. `author_lock_record` must contain exactly `lock_id`, `status`, `confirmed_by`, `confirmed_at`, `manuscript_id`, `manuscript_revision`, and `manuscript_sha256`; `status` must be `locked`, its three manuscript identity fields must equal the payload and source artifact, wrapper `author_decisions` must contain the same `lock_id`, and its offset-aware `confirmed_at` must not be later than wrapper `created_at`.

Each of the five lock-ledger fields must use exactly one of these forms:

```json
{"inline": {"any": "non-empty string, array, or object"}}
{"path": "relative/or/absolute/file", "sha256": "64 lowercase hex characters"}
```

Do not accept a scalar path, a mixed inline/file object, or additional union keys. In file form, resolve a relative path from the handoff JSON directory and verify the referenced file bytes under `--verify-files`. A journal-free translation remains available only in `standalone` mode; it is not a completed `paperline` P4 handoff.

## Preflight

Before translating:

1. Recompute the supplied Chinese manuscript SHA-256 and verify that it matches `manuscript_id`, `manuscript_revision` and `chinese_manuscript_sha256` in the package.
2. Verify that the structured author lock applies to this exact manuscript, not an earlier outline, chapter, or S6 package, that wrapper `author_decisions` contains its `lock_id`, and that the author confirmation time does not postdate handoff creation.
3. Verify that the terminology, number/unit, boundary, citation, and cross-reference ledgers cover the locked source. Recompute every `{path, sha256}` ledger reference; inline ledgers require no file read.
4. Verify that `unresolved_blockers` is empty.
5. Recompute the attached decision and contract SHA-256 values. Load the sibling `journal-navigator/scripts/validate_journal_artifacts.py` formal validator and require both `validate_decision` and `validate_contract` to pass. Parse their front matter and cross-check the confirmed status, artifact types, manuscript ID/revision, journal, article type, decision `schema_version`, contract version, selection-evidence version, writing-profile evidence ID, decision link/SHA-256, and empty blocking issues against the payload. Do not infer missing versions or treat the two evidence identifiers as interchangeable.
6. Record the accepted source versions before creating English text.

Pause and return a concise mismatch report when any check fails. Do not partially translate a formal package and then describe it as completed pipeline output.

When the package is JSON, run:

```text
python scripts/validate_pipeline_handoff.py handoff.json --verify-files
```

`STRUCTURALLY_VALID` without file verification is not sufficient to start formal translation.

For a cross-skill runner, import the script and call `validate_handoff(data)` for structure, followed by `verify_files(data, base_dir)` for manuscript/ledger bytes and journal semantics. `base_dir` is the directory against which relative references are resolved.

## Validation Trust Boundary

The validator proves package structure, cross-field identity, referenced bytes, and the semantics enforced by the sibling journal validator. It does not infer provenance or state from arbitrary prose:

- S7 authenticity relies on the upstream author-lock producer; manuscript prose cannot prove or revoke a lock.
- A `{path, sha256}` ledger binds exact bytes but cannot prove role, completeness, or coverage until that ledger type has its own formal content schema.
- Decision/contract prose is accepted only through the sibling journal validator's formal rules; journal-semantic contradictions must be fixed in that producer/validator rather than guessed independently by the translator.

## Translation Boundary

Treat these items as immutable unless the author explicitly unlocks and returns the manuscript to the writing pipeline:

- thesis, contribution order, scientific interpretation, limitations, and extrapolation boundary;
- all numbers, units, signs, uncertainty, comparisons, and statistical qualifiers;
- approved terms, abbreviations, symbols, dataset/model names, citations, and cross-references;
- paragraph and section order, except sentence-level reconstruction already allowed by the translator contract.

Apply target-journal instructions only when they are verified official mechanical language rules, such as spelling convention, nomenclature, capitalization, abbreviations, symbols, units, inclusive language, or prescribed declaration wording already supported by the Chinese source.

Do not perform substantive adaptation during translation. Return these requests upstream: deleting evidence to meet a word limit, reordering sections or contributions, adding missing declarations, changing claim strength, adding citations, rewriting novelty, or altering limitations.

## Change Handling

- If the Chinese manuscript changes after S7, stop and require a new manuscript revision and author lock.
- If a locked term, number, unit, citation, or boundary changes, stop and require an updated handoff package.
- If only the target-journal contract or evidence version changes, apply no new rule until the writing pipeline confirms impact and emits a compatible locked package.
- Preserve the older package as provenance; never overwrite its version record.

## Pipeline Output Audit

After the translation and normal integrity checks, append:

```text
翻译模式：pipeline
输入交接包版本：
中文稿ID、修订版与身份：
作者锁定记录：
术语/数字/边界台账状态：
目标期刊状态：
期刊决策 schema 版本 / 合同版本与SHA-256：
选刊证据版本 / 双轨画像证据ID：
应用的官方机械语言规则：
退回写作流水线的实质适配事项：
英文产物版本：
完整性检查：pass / blocked
```

This audit proves only which locked source was translated and which checks ran. It does not prove journal adaptation, layout compliance, submission readiness, or acceptance.
