#!/usr/bin/env python3
"""Validate a formal paperline P3-to-P4 translation handoff."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
LOCKED_LEDGER_FIELDS = (
    "locked_thesis_and_contributions",
    "terminology_ledger",
    "locked_numbers_and_units",
    "locked_claim_boundaries",
    "locked_citations_and_cross_references",
)
AUTHOR_LOCK_FIELDS = (
    "lock_id",
    "status",
    "confirmed_by",
    "confirmed_at",
    "manuscript_id",
    "manuscript_revision",
    "manuscript_sha256",
)
REQUIRED_PAYLOAD = (
    "manuscript_id",
    "manuscript_revision",
    "chinese_manuscript_sha256",
    "author_lock_record",
    *LOCKED_LEDGER_FIELDS,
    "target_journal",
    "target_journal_article_type",
    "target_journal_decision_file",
    "target_journal_decision_schema_version",
    "target_journal_decision_sha256",
    "target_journal_contract_file",
    "target_journal_contract_version",
    "target_journal_contract_sha256",
    "target_journal_selection_evidence_version",
    "target_journal_writing_profile_evidence_id",
)


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None and not isinstance(value, bool)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_json_constant(constant: str) -> Any:
    raise ValueError(f"non-standard JSON constant: {constant}")


def _parse_finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"JSON number is outside the supported finite range: {value}")
    return parsed


def load_json_strict(text: str) -> Any:
    """Parse JSON, rejecting duplicate keys and all non-finite results."""
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_object_pairs,
        parse_constant=_reject_nonstandard_json_constant,
        parse_float=_parse_finite_json_float,
    )


def _parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not _nonempty_string(value):
        errors.append(f"{label}: must be a non-empty ISO-8601 timestamp")
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        timestamp = datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{label}: must be a valid ISO-8601 timestamp")
        return None
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        errors.append(f"{label}: must include a UTC offset")
        return None
    if timestamp.date() > datetime.now(timestamp.tzinfo).date():
        errors.append(f"{label}: must not be later than the validation date")
        return None
    return timestamp


def _validate_locked_ledger(value: Any, label: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}: must be an object with exact keys {{inline}} or {{path, sha256}}"]
    keys = set(value)
    if keys == {"inline"}:
        inline = value.get("inline")
        if not isinstance(inline, (str, list, dict)) or not _nonempty(inline):
            return [f"{label}.inline: must be a non-empty string, array, or object"]
        return []
    if keys == {"path", "sha256"}:
        errors: list[str] = []
        if not _nonempty_string(value.get("path")):
            errors.append(f"{label}.path: must be a non-empty string")
        if not _valid_hash(value.get("sha256")):
            errors.append(f"{label}.sha256: must be 64 lowercase hex characters")
        return errors
    return [f"{label}: must have exact keys {{inline}} or {{path, sha256}}"]


def _journal_validator_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "journal-navigator"
        / "scripts"
        / "validate_journal_artifacts.py"
    )


def _load_journal_validator() -> tuple[Any | None, list[str]]:
    path = _journal_validator_path()
    if not path.is_file():
        return None, [f"journal validator: sibling validator not found: {path}"]
    spec = importlib.util.spec_from_file_location("paperline_journal_artifact_validator", path)
    if spec is None or spec.loader is None:
        return None, [f"journal validator: cannot load module spec: {path}"]
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - defensive boundary around sibling code
        return None, [f"journal validator: failed to load {path}: {exc}"]
    required_api = (
        "validate_decision",
        "validate_contract",
        "read_text",
        "parse_frontmatter",
    )
    missing = [name for name in required_api if not callable(getattr(module, name, None))]
    if missing:
        return None, [f"journal validator: incompatible API; missing {', '.join(missing)}"]
    return module, []


def validate_handoff(data: Any) -> list[str]:
    """Validate only the JSON structure and cross-field bindings."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: handoff must be a JSON object"]

    if not _nonempty_string(data.get("handoff_id")):
        errors.append("handoff_id: must be a non-empty string")
    expected_wrapper = {
        "from_stage": "chinese-finalization",
        "to_stage": "english-translation",
        "from_skill": "paper-navigator",
        "to_skill": "zh-en-paper-translator",
    }
    for field, expected in expected_wrapper.items():
        if data.get(field) != expected:
            errors.append(f"{field}: must equal {expected!r}")
    handoff_created_at = _parse_timestamp(data.get("created_at"), "created_at", errors)
    if data.get("open_questions") != []:
        errors.append("open_questions: must be an empty array")
    if data.get("blockers") != []:
        errors.append("blockers: must be an empty array")
    author_decisions = data.get("author_decisions")
    if not isinstance(author_decisions, list) or not author_decisions:
        errors.append("author_decisions: must contain the author lock ID")

    payload = data.get("payload")
    if not isinstance(payload, dict):
        return errors + ["payload: must be an object"]
    expected_payload = {
        "handoff_type": "formal-full-manuscript-translation",
        "handoff_package_schema_version": "1.0",
        "handoff_status": "locked",
        "chinese_manuscript_status": "S7",
        "target_journal_status": "contract-confirmed",
        "target_journal_decision_schema_version": "1.0",
        "target_journal_contract_version": "2.0",
    }
    for field, expected in expected_payload.items():
        if payload.get(field) != expected:
            errors.append(f"payload.{field}: must equal {expected!r}")
    if "handoff_package_version" in payload:
        errors.append(
            "payload.handoff_package_version: legacy field is not allowed; "
            "use handoff_package_schema_version"
        )
    if "target_journal_decision_version" in payload:
        errors.append(
            "payload.target_journal_decision_version: legacy field is not allowed; "
            "use target_journal_decision_schema_version"
        )
    for field in REQUIRED_PAYLOAD:
        value = payload.get(field)
        if field == "author_lock_record" or field in LOCKED_LEDGER_FIELDS:
            if not _nonempty(value):
                errors.append(f"payload.{field}: must be present and non-empty")
        elif not _nonempty_string(value):
            errors.append(f"payload.{field}: must be a non-empty string")
    for field in LOCKED_LEDGER_FIELDS:
        errors.extend(_validate_locked_ledger(payload.get(field), f"payload.{field}"))
    if payload.get("unresolved_blockers") != []:
        errors.append("payload.unresolved_blockers: must be an empty array")
    for field in (
        "chinese_manuscript_sha256",
        "target_journal_decision_sha256",
        "target_journal_contract_sha256",
    ):
        if not _valid_hash(payload.get(field)):
            errors.append(f"payload.{field}: must be 64 lowercase hex characters")
    if Path(str(payload.get("target_journal_decision_file", ""))).name != "target-journal-decision.md":
        errors.append("payload.target_journal_decision_file: wrong formal filename")
    if Path(str(payload.get("target_journal_contract_file", ""))).name != "target-journal-writing-contract.md":
        errors.append("payload.target_journal_contract_file: wrong formal filename")

    author_lock = payload.get("author_lock_record")
    author_confirmed_at: datetime | None = None
    if not isinstance(author_lock, dict):
        errors.append("payload.author_lock_record: must be an object")
    else:
        if set(author_lock) != set(AUTHOR_LOCK_FIELDS):
            errors.append(
                "payload.author_lock_record: must contain exactly "
                f"{sorted(AUTHOR_LOCK_FIELDS)!r}"
            )
        for field in AUTHOR_LOCK_FIELDS[:-1]:
            if not _nonempty_string(author_lock.get(field)):
                errors.append(f"payload.author_lock_record.{field}: must be a non-empty string")
        if not _valid_hash(author_lock.get("manuscript_sha256")):
            errors.append(
                "payload.author_lock_record.manuscript_sha256: must be 64 lowercase hex characters"
            )
        author_confirmed_at = _parse_timestamp(
            author_lock.get("confirmed_at"),
            "payload.author_lock_record.confirmed_at",
            errors,
        )
        expected_lock_binding = {
            "status": "locked",
            "manuscript_id": payload.get("manuscript_id"),
            "manuscript_revision": payload.get("manuscript_revision"),
            "manuscript_sha256": payload.get("chinese_manuscript_sha256"),
        }
        for field, expected in expected_lock_binding.items():
            if author_lock.get(field) != expected:
                errors.append(
                    f"payload.author_lock_record.{field}: must match the locked manuscript payload"
                )
        lock_id = author_lock.get("lock_id")
        if isinstance(author_decisions, list) and lock_id not in author_decisions:
            errors.append(
                "author_decisions: must contain payload.author_lock_record.lock_id"
            )
    if (
        author_confirmed_at is not None
        and handoff_created_at is not None
        and author_confirmed_at > handoff_created_at
    ):
        errors.append(
            "payload.author_lock_record.confirmed_at: must not be later than handoff created_at"
        )

    sources = data.get("source_artifacts")
    if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], dict):
        errors.append("source_artifacts: must contain exactly one Chinese S7 artifact")
    else:
        source = sources[0]
        for field in ("artifact_id", "artifact_type", "path", "version", "sha256"):
            if not _nonempty_string(source.get(field)):
                errors.append(f"source_artifacts[0].{field}: must be a non-empty string")
        if source.get("artifact_type") != "chinese-manuscript-s7":
            errors.append("source_artifacts[0].artifact_type: must equal chinese-manuscript-s7")
        if source.get("version") != payload.get("manuscript_revision"):
            errors.append("source_artifacts[0].version: must match payload manuscript_revision")
        if source.get("sha256") != payload.get("chinese_manuscript_sha256"):
            errors.append("source_artifacts[0].sha256: must match payload Chinese manuscript SHA-256")
        if not _valid_hash(source.get("sha256")):
            errors.append("source_artifacts[0].sha256: must be 64 lowercase hex characters")
        if isinstance(author_lock, dict):
            if author_lock.get("manuscript_revision") != source.get("version"):
                errors.append(
                    "payload.author_lock_record.manuscript_revision: must match the source artifact version"
                )
            if author_lock.get("manuscript_sha256") != source.get("sha256"):
                errors.append(
                    "payload.author_lock_record.manuscript_sha256: must match the source artifact SHA-256"
                )
    return errors


def _resolve_path(base_dir: Path, raw_path: Any) -> Path:
    path = Path(str(raw_path))
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def _verify_digest(label: str, path: Path, expected: Any) -> list[str]:
    try:
        if not path.is_file():
            return [f"{label}: file not found: {path}"]
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        return [f"{label}: cannot read {path}: {exc}"]
    if observed != expected:
        return [f"{label}: SHA-256 does not match the locked package"]
    return []


def _parse_journal_frontmatter(
    module: Any,
    path: Path,
    label: str,
) -> tuple[dict[str, str], list[str]]:
    try:
        text, read_errors = module.read_text(path, label)
        if read_errors:
            return {}, [f"{label} parser: {error}" for error in read_errors]
        data, parse_errors = module.parse_frontmatter(text, label)
        return data, [f"{label} parser: {error}" for error in parse_errors]
    except Exception as exc:  # pragma: no cover - defensive boundary around sibling code
        return {}, [f"{label} parser: sibling validator raised {exc}"]


def _cross_check(
    observed: dict[str, str],
    expected: dict[str, Any],
    label: str,
) -> list[str]:
    return [
        f"{label}.{field}: artifact value {observed.get(field)!r} does not match payload {value!r}"
        for field, value in expected.items()
        if observed.get(field) != value
    ]


def verify_files(data: dict[str, Any], base_dir: Path) -> list[str]:
    """Verify referenced bytes and journal semantics relative to ``base_dir``.

    Call ``validate_handoff`` first. This function is also the reusable API for
    the cross-skill dry-run runner; the CLI passes the handoff file's directory.
    """
    errors: list[str] = []
    payload = data.get("payload")
    sources = data.get("source_artifacts")
    if not isinstance(payload, dict) or not isinstance(sources, list) or not sources:
        return ["cannot verify files before the handoff structure is valid"]
    base = Path(base_dir).resolve()
    manuscript_path = _resolve_path(base, sources[0].get("path"))
    decision_path = _resolve_path(base, payload.get("target_journal_decision_file"))
    contract_path = _resolve_path(base, payload.get("target_journal_contract_file"))
    checks = (
        ("Chinese manuscript", manuscript_path, payload.get("chinese_manuscript_sha256")),
        (
            "target journal decision",
            decision_path,
            payload.get("target_journal_decision_sha256"),
        ),
        (
            "target journal contract",
            contract_path,
            payload.get("target_journal_contract_sha256"),
        ),
    )
    for label, path, expected in checks:
        errors.extend(_verify_digest(label, path, expected))
    for field in LOCKED_LEDGER_FIELDS:
        ledger = payload.get(field)
        if isinstance(ledger, dict) and set(ledger) == {"path", "sha256"}:
            path = _resolve_path(base, ledger.get("path"))
            errors.extend(_verify_digest(f"payload.{field}", path, ledger.get("sha256")))

    journal, load_errors = _load_journal_validator()
    errors.extend(load_errors)
    if journal is None:
        return errors
    if decision_path.is_file():
        try:
            errors.extend(
                f"target journal decision validator: {error}"
                for error in journal.validate_decision(decision_path)
            )
        except Exception as exc:  # pragma: no cover - defensive boundary around sibling code
            errors.append(f"target journal decision validator raised: {exc}")
    if contract_path.is_file():
        try:
            errors.extend(
                f"target journal contract validator: {error}"
                for error in journal.validate_contract(contract_path)
            )
        except Exception as exc:  # pragma: no cover - defensive boundary around sibling code
            errors.append(f"target journal contract validator raised: {exc}")

    decision, decision_parse_errors = _parse_journal_frontmatter(
        journal, decision_path, "target journal decision"
    )
    contract, contract_parse_errors = _parse_journal_frontmatter(
        journal, contract_path, "target journal contract"
    )
    errors.extend(decision_parse_errors + contract_parse_errors)
    errors.extend(_cross_check(
        decision,
        {
            "artifact_type": "target_journal_decision",
            "schema_version": payload.get("target_journal_decision_schema_version"),
            "status": "confirmed",
            "manuscript_id": payload.get("manuscript_id"),
            "manuscript_revision": payload.get("manuscript_revision"),
            "target_journal": payload.get("target_journal"),
            "article_type": payload.get("target_journal_article_type"),
            "evidence_version": payload.get("target_journal_selection_evidence_version"),
            "blocking_issues": "[]",
        },
        "target journal decision",
    ))
    errors.extend(_cross_check(
        contract,
        {
            "artifact_type": "target_journal_writing_contract",
            "contract_version": payload.get("target_journal_contract_version"),
            "status": "confirmed",
            "manuscript_id": payload.get("manuscript_id"),
            "manuscript_revision": payload.get("manuscript_revision"),
            "target_journal": payload.get("target_journal"),
            "article_type": payload.get("target_journal_article_type"),
            "selection_evidence_version": payload.get(
                "target_journal_selection_evidence_version"
            ),
            "writing_profile_evidence_id": payload.get(
                "target_journal_writing_profile_evidence_id"
            ),
            "decision_sha256": payload.get("target_journal_decision_sha256"),
            "blocking_issues": "[]",
        },
        "target journal contract",
    ))
    decision_link = contract.get("decision_file")
    if _nonempty_string(decision_link):
        linked_decision = _resolve_path(contract_path.parent, decision_link)
        if linked_decision != decision_path:
            errors.append(
                "target journal contract.decision_file: must resolve to "
                "payload.target_journal_decision_file"
            )
    return errors


def _valid_fixture(
    manuscript_digest: str,
    decision_digest: str,
    contract_digest: str,
    ledger_digest: str,
    decision: dict[str, str],
    contract: dict[str, str],
) -> dict[str, Any]:
    lock_id = "author-lock-001"
    return {
        "handoff_id": "h-cn-en-001",
        "from_stage": "chinese-finalization",
        "to_stage": "english-translation",
        "from_skill": "paper-navigator",
        "to_skill": "zh-en-paper-translator",
        "created_at": "2026-08-10T15:30:00+08:00",
        "source_artifacts": [{
            "artifact_id": "ms-001-cn-r1",
            "artifact_type": "chinese-manuscript-s7",
            "path": "manuscript-cn.md",
            "version": "r1",
            "sha256": manuscript_digest,
        }],
        "payload": {
            "handoff_type": "formal-full-manuscript-translation",
            "handoff_package_schema_version": "1.0",
            "handoff_status": "locked",
            "chinese_manuscript_status": "S7",
            "manuscript_id": "ms-001",
            "manuscript_revision": "r1",
            "chinese_manuscript_sha256": manuscript_digest,
            "author_lock_record": {
                "lock_id": lock_id,
                "status": "locked",
                "confirmed_by": "author-001",
                "confirmed_at": "2026-08-10T15:25:00+08:00",
                "manuscript_id": "ms-001",
                "manuscript_revision": "r1",
                "manuscript_sha256": manuscript_digest,
            },
            "locked_thesis_and_contributions": {
                "inline": {"thesis": "locked", "contributions": ["C1"]}
            },
            "terminology_ledger": {"path": "terms.tsv", "sha256": ledger_digest},
            "locked_numbers_and_units": {"inline": ["N=1", "unit=m"]},
            "locked_claim_boundaries": {"inline": "No causal claim."},
            "locked_citations_and_cross_references": {"inline": ["[1]", "Fig. 1"]},
            "unresolved_blockers": [],
            "target_journal_status": "contract-confirmed",
            "target_journal": decision["target_journal"],
            "target_journal_article_type": decision["article_type"],
            "target_journal_decision_file": "target-journal-decision.md",
            "target_journal_decision_schema_version": decision["schema_version"],
            "target_journal_decision_sha256": decision_digest,
            "target_journal_contract_file": "target-journal-writing-contract.md",
            "target_journal_contract_version": contract["contract_version"],
            "target_journal_contract_sha256": contract_digest,
            "target_journal_selection_evidence_version": decision["evidence_version"],
            "target_journal_writing_profile_evidence_id": contract[
                "writing_profile_evidence_id"
            ],
        },
        "author_decisions": [lock_id],
        "open_questions": [],
        "blockers": [],
    }


def _fixture_path(root: Path, artifacts: dict[str, Any], key: str) -> Path:
    path = Path(str(artifacts[key]))
    return path if path.is_absolute() else root / path


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="translation-handoff-self-test-") as tmp:
        root = Path(tmp)
        journal, load_errors = _load_journal_validator()
        if journal is None:
            print(f"FAIL: load sibling journal validator: {load_errors}")
            return 1
        writer = getattr(journal, "write_valid_fixture", None)
        if not callable(writer):
            print("FAIL: sibling journal validator lacks write_valid_fixture(root)")
            return 1
        try:
            artifacts = writer(root)
        except Exception as exc:
            print(f"FAIL: sibling journal fixture generation raised: {exc}")
            return 1
        if not isinstance(artifacts, dict) or not {
            "evidence", "decision", "journal_profile", "field_blueprint", "contract"
        }.issubset(artifacts):
            print("FAIL: sibling journal fixture has an incompatible return shape")
            return 1
        decision_path = _fixture_path(root, artifacts, "decision")
        contract_path = _fixture_path(root, artifacts, "contract")
        decision, decision_errors = _parse_journal_frontmatter(
            journal, decision_path, "self-test decision"
        )
        contract, contract_errors = _parse_journal_frontmatter(
            journal, contract_path, "self-test contract"
        )
        if decision_errors or contract_errors:
            print(f"FAIL: parse sibling fixture: {decision_errors + contract_errors}")
            return 1

        manuscript = root / "manuscript-cn.md"
        manuscript_bytes = b"locked synthetic Chinese manuscript"
        manuscript.write_bytes(manuscript_bytes)
        manuscript_digest = hashlib.sha256(manuscript_bytes).hexdigest()
        ledger = root / "terms.tsv"
        ledger_bytes = b"zh\ten\tstatus\nterm\tterm\tlocked\n"
        ledger.write_bytes(ledger_bytes)
        ledger_digest = hashlib.sha256(ledger_bytes).hexdigest()
        decision_bytes = decision_path.read_bytes()
        contract_bytes = contract_path.read_bytes()
        decision_digest = hashlib.sha256(decision_bytes).hexdigest()
        contract_digest = hashlib.sha256(contract_bytes).hexdigest()
        valid = _valid_fixture(
            manuscript_digest,
            decision_digest,
            contract_digest,
            ledger_digest,
            decision,
            contract,
        )
        handoff_path = root / "handoff.json"
        handoff_path.write_text(json.dumps(valid, ensure_ascii=False), encoding="utf-8")

        checks: list[tuple[str, dict[str, Any], bool]] = [("valid locked handoff", valid, True)]
        for label, field, value in (
            ("reject S6", "chinese_manuscript_status", "S6"),
            ("reject wrong contract version", "target_journal_contract_version", "1.0"),
            ("reject non-hash manuscript identity", "chinese_manuscript_sha256", "latest"),
        ):
            case = json.loads(json.dumps(valid))
            case["payload"][field] = value
            checks.append((label, case, False))
        blocked = json.loads(json.dumps(valid))
        blocked["blockers"] = ["unresolved"]
        checks.append(("reject wrapper blocker", blocked, False))
        missing_handoff_id = json.loads(json.dumps(valid))
        missing_handoff_id.pop("handoff_id")
        checks.append(("reject missing formal handoff ID", missing_handoff_id, False))
        numeric_source_identity = json.loads(json.dumps(valid))
        numeric_source_identity["source_artifacts"][0]["artifact_id"] = 1
        checks.append(("reject non-string source artifact identity", numeric_source_identity, False))
        legacy_decision_version = json.loads(json.dumps(valid))
        legacy_decision_version["payload"]["target_journal_decision_version"] = (
            legacy_decision_version["payload"].pop("target_journal_decision_schema_version")
        )
        checks.append(("reject legacy decision-version field", legacy_decision_version, False))
        conflicting_decision_version = json.loads(json.dumps(valid))
        conflicting_decision_version["payload"]["target_journal_decision_version"] = "0.9"
        checks.append((
            "reject coexisting legacy decision-version field",
            conflicting_decision_version,
            False,
        ))
        conflicting_package_version = json.loads(json.dumps(valid))
        conflicting_package_version["payload"]["handoff_package_version"] = "0.9"
        checks.append((
            "reject coexisting legacy handoff-package version field",
            conflicting_package_version,
            False,
        ))
        scalar_ledger = json.loads(json.dumps(valid))
        scalar_ledger["payload"]["terminology_ledger"] = "terms.tsv"
        checks.append(("reject ambiguous scalar ledger", scalar_ledger, False))
        empty_inline_ledger = json.loads(json.dumps(valid))
        empty_inline_ledger["payload"]["locked_numbers_and_units"] = {"inline": []}
        checks.append(("reject empty inline ledger", empty_inline_ledger, False))
        malformed_ledger = json.loads(json.dumps(valid))
        malformed_ledger["payload"]["terminology_ledger"] = {
            "path": "terms.tsv", "sha256": ledger_digest, "inline": ["term"]
        }
        checks.append(("reject mixed ledger union", malformed_ledger, False))
        unstructured_lock = json.loads(json.dumps(valid))
        unstructured_lock["payload"]["author_lock_record"] = "author-lock-001"
        checks.append(("reject unstructured author lock", unstructured_lock, False))
        incomplete_lock = json.loads(json.dumps(valid))
        incomplete_lock["payload"]["author_lock_record"].pop("confirmed_by")
        checks.append(("reject author lock with missing key", incomplete_lock, False))
        draft_lock = json.loads(json.dumps(valid))
        draft_lock["payload"]["author_lock_record"]["status"] = "draft"
        checks.append(("reject author lock without locked status", draft_lock, False))
        future_lock = json.loads(json.dumps(valid))
        future_lock["payload"]["author_lock_record"]["confirmed_at"] = (
            "2026-08-10T15:31:00+08:00"
        )
        checks.append(("reject author lock created after handoff", future_lock, False))
        far_future_lock = json.loads(json.dumps(valid))
        far_future_lock["payload"]["author_lock_record"]["confirmed_at"] = (
            "2099-01-01T15:25:00+08:00"
        )
        far_future_lock["created_at"] = "2099-01-01T15:30:00+08:00"
        checks.append(("reject internally ordered future author lock", far_future_lock, False))
        extended_lock = json.loads(json.dumps(valid))
        extended_lock["payload"]["author_lock_record"]["note"] = "extra"
        checks.append(("reject author lock with extra keys", extended_lock, False))
        stale_lock = json.loads(json.dumps(valid))
        stale_lock["payload"]["author_lock_record"]["manuscript_sha256"] = "b" * 64
        checks.append(("reject author lock for different manuscript bytes", stale_lock, False))
        wrong_wrapper_lock = json.loads(json.dumps(valid))
        wrong_wrapper_lock["author_decisions"] = ["author-lock-other"]
        checks.append(("reject wrapper without matching lock ID", wrong_wrapper_lock, False))

        failures = 0
        for label, case, expected in checks:
            observed = not validate_handoff(case)
            if observed != expected:
                failures += 1
                print(f"FAIL: {label}: {validate_handoff(case) or 'unexpectedly valid'}")
            else:
                print(f"PASS: {label}")

        file_checks = 0
        duplicate_lock_json = json.dumps(valid).replace(
            '"status": "locked"',
            '"status": "draft", "status": "locked"',
            1,
        )
        file_checks += 1
        try:
            load_json_strict(duplicate_lock_json)
        except ValueError:
            print("PASS: reject duplicate JSON key hiding an unlocked author record")
        else:
            failures += 1
            print("FAIL: reject duplicate JSON key hiding an unlocked author record")

        nonfinite_case = json.loads(json.dumps(valid))
        nonfinite_case["payload"]["locked_numbers_and_units"] = {
            "inline": [float("nan")]
        }
        nonfinite_json = json.dumps(nonfinite_case, allow_nan=True)
        file_checks += 1
        try:
            load_json_strict(nonfinite_json)
        except ValueError:
            print("PASS: reject non-standard NaN inside locked inline ledger")
        else:
            failures += 1
            print("FAIL: reject non-standard NaN inside locked inline ledger")

        overflow_json = json.dumps(valid).replace('"N=1"', "1e999", 1)
        file_checks += 1
        try:
            load_json_strict(overflow_json)
        except ValueError:
            print("PASS: reject finite-syntax JSON number that overflows to infinity")
        else:
            failures += 1
            print("FAIL: reject finite-syntax JSON number that overflows to infinity")

        def expect_file_result(label: str, case: dict[str, Any], expected: bool) -> None:
            nonlocal failures, file_checks
            file_checks += 1
            file_errors = verify_files(case, root)
            observed = not file_errors
            if observed != expected:
                failures += 1
                print(f"FAIL: {label}: {file_errors or 'unexpectedly valid'}")
            else:
                print(f"PASS: {label}")

        expect_file_result("verify matching files and journal semantics", valid, True)

        manuscript.write_bytes(b"changed")
        expect_file_result("reject changed manuscript bytes", valid, False)
        manuscript.write_bytes(manuscript_bytes)

        ledger.write_bytes(b"changed")
        expect_file_result("reject changed ledger bytes", valid, False)
        ledger.write_bytes(ledger_bytes)

        missing_ledger = json.loads(json.dumps(valid))
        missing_ledger["payload"]["terminology_ledger"]["path"] = "missing-terms.tsv"
        expect_file_result("reject missing referenced ledger", missing_ledger, False)

        payload_mismatch = json.loads(json.dumps(valid))
        payload_mismatch["payload"]["target_journal"] = "Different Journal"
        expect_file_result("reject journal artifact and payload mismatch", payload_mismatch, False)

        contract_text = contract_bytes.decode("utf-8")
        invalid_contract_text = contract_text.replace(
            'status: "confirmed"', 'status: "draft"', 1
        )
        contract_path.write_text(invalid_contract_text, encoding="utf-8")
        invalid_contract = json.loads(json.dumps(valid))
        invalid_contract["payload"]["target_journal_contract_sha256"] = hashlib.sha256(
            contract_path.read_bytes()
        ).hexdigest()
        expect_file_result("reject semantically invalid contract with matching hash", invalid_contract, False)
        contract_path.write_bytes(contract_bytes)

        decision_text = decision_bytes.decode("utf-8")
        invalid_decision_text = decision_text.replace(
            'status: "confirmed"', 'status: "draft"', 1
        )
        decision_path.write_text(invalid_decision_text, encoding="utf-8")
        invalid_decision_digest = hashlib.sha256(decision_path.read_bytes()).hexdigest()
        rebound_contract = contract_bytes.decode("utf-8").replace(
            decision_digest, invalid_decision_digest
        )
        contract_path.write_text(rebound_contract, encoding="utf-8")
        invalid_decision = json.loads(json.dumps(valid))
        invalid_decision["payload"]["target_journal_decision_sha256"] = invalid_decision_digest
        invalid_decision["payload"]["target_journal_contract_sha256"] = hashlib.sha256(
            contract_path.read_bytes()
        ).hexdigest()
        expect_file_result("reject semantically invalid decision with rebound hashes", invalid_decision, False)
        decision_path.write_bytes(decision_bytes)
        contract_path.write_bytes(contract_bytes)

        if failures:
            print(f"self-test: {failures} failure(s)")
            return 1
        print(f"self-test: {len(checks) + file_checks} checks passed")
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a formal paperline translation handoff JSON.")
    parser.add_argument("handoff", nargs="?", type=Path)
    parser.add_argument("--verify-files", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.handoff is None:
        parser.error("provide a handoff JSON file or use --self-test")
    try:
        data = load_json_strict(args.handoff.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: cannot read handoff JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate_handoff(data)
    if args.verify_files and not errors:
        errors.extend(verify_files(data, args.handoff.resolve().parent))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"INVALID: {len(errors)} error(s)")
        return 1
    label = "VALID_WITH_FILES" if args.verify_files else "STRUCTURALLY_VALID"
    print(f"{label}: {args.handoff}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
