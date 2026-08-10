#!/usr/bin/env python3
"""Validate a paperline pipeline state using only the Python standard library."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


STAGES = (
    "chinese-evidence-profile",
    "journal-contract",
    "chinese-finalization",
    "english-translation",
    "pre-submission-check",
)
STATUSES = {"pending", "active", "waiting-human", "blocked", "complete"}
SKILLS = {"paperline", "paper-navigator", "journal-navigator", "zh-en-paper-translator"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VENUE_BINDING_FIELDS = (
    "target_journal",
    "article_type",
    "decision_path",
    "decision_schema_version",
    "decision_hash",
    "contract_path",
    "contract_version",
    "contract_hash",
    "selection_evidence_version",
    "writing_profile_evidence_id",
)
STAGE_ARTIFACT_SCHEMAS = {
    "english-translation": {
        "artifact_type": "english-translation-package",
        "artifact_schema_version": "1.0",
    },
    "pre-submission-check": {
        "artifact_type": "pre-submission-check-report",
        "artifact_schema_version": "1.0",
    },
}
DEPENDENCIES = {
    "chinese-evidence-profile": (),
    "journal-contract": ("chinese-evidence-profile",),
    "chinese-finalization": ("chinese-evidence-profile", "journal-contract"),
    "english-translation": ("journal-contract", "chinese-finalization"),
    "pre-submission-check": ("journal-contract", "chinese-finalization", "english-translation"),
}
FORMAL_HANDOFF_SKILLS = {
    ("journal-contract", "chinese-finalization"): ("journal-navigator", "paper-navigator"),
    ("chinese-finalization", "english-translation"): ("paper-navigator", "zh-en-paper-translator"),
    ("english-translation", "pre-submission-check"): ("zh-en-paper-translator", "paperline"),
}
LOCKED_LEDGER_FIELDS = (
    "locked_thesis_and_contributions",
    "terminology_ledger",
    "locked_numbers_and_units",
    "locked_claim_boundaries",
    "locked_citations_and_cross_references",
)
BYPASS_STAGE_NAMES = (
    "chinese-finalization",
    "english-translation",
    "pre-submission-check",
)
BYPASS_KEYS = {
    "authorized_at",
    "reason",
    "resume_stage",
    "baseline_stage_revisions",
    "invalidate_on_lock",
}
VENUE_PENDING_CHINESE_STATUSES = {f"S{index}" for index in range(7)}


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_hash(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _has_content(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    return value is not None and not isinstance(value, bool)


def _reject_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_json_constant(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _parse_finite_json_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"JSON number is outside the supported finite range: {value}")
    return parsed


def load_json_strict(text: str) -> Any:
    """Parse strict JSON, rejecting duplicate keys and non-finite results."""
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_object_pairs,
        parse_constant=_reject_nonfinite_json_constant,
        parse_float=_parse_finite_json_float,
    )


def _parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not _is_nonempty_string(value):
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
        errors.append(
            f"{label}: local calendar date must not be later than the validation date"
        )
        return None
    return timestamp


def _validate_locked_ledger(value: Any, label: str) -> list[str]:
    """Validate the producer-side shape; the translator verifies referenced files."""
    if not isinstance(value, dict):
        return [f"{label}: must be an object with exact keys {{inline}} or {{path, sha256}}"]
    keys = set(value)
    if keys == {"inline"}:
        inline = value.get("inline")
        if not isinstance(inline, (str, list, dict)) or not _has_content(inline):
            return [f"{label}.inline: must be a non-empty string, array, or object"]
        return []
    if keys == {"path", "sha256"}:
        errors: list[str] = []
        if not _is_nonempty_string(value.get("path")):
            errors.append(f"{label}.path: must be a non-empty string")
        if not _valid_hash(value.get("sha256")):
            errors.append(f"{label}.sha256: must be 64 lowercase hex characters")
        return errors
    return [f"{label}: must have exact keys {{inline}} or {{path, sha256}}"]


def _validate_translation_payload(
    payload: dict[str, Any],
    prefix: str,
    state: dict[str, Any],
    venue: dict[str, Any],
    source_output: dict[str, Any] | None,
    sources: list[Any] | None,
    author_decisions: Any,
    p3_content_state: Any,
    handoff_created_at: datetime | None,
) -> list[str]:
    errors: list[str] = []
    expected = {
        "handoff_type": "formal-full-manuscript-translation",
        "handoff_package_schema_version": "1.0",
        "handoff_status": "locked",
        "chinese_manuscript_status": "S7",
        "target_journal_status": "contract-confirmed",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            errors.append(f"{prefix}.payload.{field}: must equal {value!r}")
    if "handoff_package_version" in payload:
        errors.append(
            f"{prefix}.payload.handoff_package_version: legacy field is not allowed; "
            "use handoff_package_schema_version"
        )
    if "target_journal_decision_version" in payload:
        errors.append(
            f"{prefix}.payload.target_journal_decision_version: legacy field is not allowed; "
            "use target_journal_decision_schema_version"
        )
    required_content = (
        "manuscript_id",
        "manuscript_revision",
        "chinese_manuscript_sha256",
        "locked_thesis_and_contributions",
        "terminology_ledger",
        "locked_numbers_and_units",
        "locked_claim_boundaries",
        "locked_citations_and_cross_references",
        "target_journal_decision_file",
        "target_journal_decision_schema_version",
        "target_journal_decision_sha256",
        "target_journal_contract_file",
        "target_journal_contract_version",
        "target_journal_contract_sha256",
        "target_journal_selection_evidence_version",
        "target_journal_writing_profile_evidence_id",
        "target_journal",
        "target_journal_article_type",
    )
    for field in required_content:
        if not _has_content(payload.get(field)):
            errors.append(f"{prefix}.payload.{field}: must be present and non-empty")
    for field in LOCKED_LEDGER_FIELDS:
        errors.extend(_validate_locked_ledger(payload.get(field), f"{prefix}.payload.{field}"))

    author_lock = payload.get("author_lock_record")
    if not isinstance(author_lock, dict):
        errors.append(f"{prefix}.payload.author_lock_record: must be an object")
    else:
        expected_lock_keys = {
            "lock_id",
            "status",
            "confirmed_by",
            "confirmed_at",
            "manuscript_id",
            "manuscript_revision",
            "manuscript_sha256",
        }
        if set(author_lock) != expected_lock_keys:
            errors.append(
                f"{prefix}.payload.author_lock_record: must contain exactly {sorted(expected_lock_keys)!r}"
            )
        expected_author_lock = {
            "status": "locked",
            "manuscript_id": state.get("manuscript_id"),
            "manuscript_revision": state.get("manuscript_revision"),
            "manuscript_sha256": source_output.get("sha256") if isinstance(source_output, dict) else None,
        }
        for field, expected_value in expected_author_lock.items():
            if author_lock.get(field) != expected_value:
                errors.append(
                    f"{prefix}.payload.author_lock_record.{field}: must match the current locked P3 manuscript"
                )
        for field in ("lock_id", "confirmed_by", "confirmed_at"):
            if not _is_nonempty_string(author_lock.get(field)):
                errors.append(f"{prefix}.payload.author_lock_record.{field}: must be a non-empty string")
        lock_time = _parse_timestamp(
            author_lock.get("confirmed_at"),
            f"{prefix}.payload.author_lock_record.confirmed_at",
            errors,
        )
        if (
            lock_time is not None
            and handoff_created_at is not None
            and lock_time > handoff_created_at
        ):
            errors.append(
                f"{prefix}.payload.author_lock_record.confirmed_at: must not be later than handoff created_at"
            )
        lock_id = author_lock.get("lock_id")
        if not isinstance(author_decisions, list) or lock_id not in author_decisions:
            errors.append(
                f"{prefix}.author_decisions: must contain payload.author_lock_record.lock_id"
            )
        binding = p3_content_state.get("author_lock_binding") if isinstance(p3_content_state, dict) else None
        if not isinstance(binding, dict):
            errors.append(
                f"{prefix}.payload.author_lock_record: current P3 content_state.author_lock_binding is required"
            )
        else:
            for field in (
                "lock_id",
                "status",
                "confirmed_by",
                "confirmed_at",
                "manuscript_id",
                "manuscript_revision",
                "manuscript_sha256",
            ):
                if author_lock.get(field) != binding.get(field):
                    errors.append(
                        f"{prefix}.payload.author_lock_record.{field}: must match current P3 author_lock_binding"
                    )
    blockers = payload.get("unresolved_blockers")
    if blockers != []:
        errors.append(f"{prefix}.payload.unresolved_blockers: must be an empty array")
    for field in (
        "chinese_manuscript_sha256",
        "target_journal_decision_sha256",
        "target_journal_contract_sha256",
    ):
        if not _valid_hash(payload.get(field)):
            errors.append(f"{prefix}.payload.{field}: must be 64 lowercase hex characters")

    if payload.get("manuscript_id") != state.get("manuscript_id"):
        errors.append(f"{prefix}.payload.manuscript_id: must match pipeline manuscript_id")
    if payload.get("manuscript_revision") != state.get("manuscript_revision"):
        errors.append(f"{prefix}.payload.manuscript_revision: must match pipeline manuscript_revision")

    venue_mapping = {
        "target_journal": "target_journal",
        "target_journal_article_type": "article_type",
        "target_journal_decision_file": "decision_path",
        "target_journal_decision_schema_version": "decision_schema_version",
        "target_journal_decision_sha256": "decision_hash",
        "target_journal_contract_file": "contract_path",
        "target_journal_contract_version": "contract_version",
        "target_journal_contract_sha256": "contract_hash",
        "target_journal_selection_evidence_version": "selection_evidence_version",
        "target_journal_writing_profile_evidence_id": "writing_profile_evidence_id",
    }
    for payload_key, venue_key in venue_mapping.items():
        if payload.get(payload_key) != venue.get(venue_key):
            errors.append(f"{prefix}.payload.{payload_key}: must match venue.{venue_key}")

    if isinstance(source_output, dict):
        if payload.get("chinese_manuscript_sha256") != source_output.get("sha256"):
            errors.append(f"{prefix}.payload.chinese_manuscript_sha256: must match current P3 output")
        if payload.get("manuscript_revision") != source_output.get("version"):
            errors.append(f"{prefix}.payload.manuscript_revision: must match current P3 output version")
        if sources != [source_output]:
            errors.append(f"{prefix}.source_artifacts: must be exactly the current P3 output")
    return errors


def _validate_presubmission_payload(
    payload: dict[str, Any],
    prefix: str,
    state: dict[str, Any],
    venue: dict[str, Any],
    source_output: dict[str, Any] | None,
    sources: list[Any] | None,
    author_decisions: Any,
    p3_output: dict[str, Any] | None,
    p3_content_state: Any,
    handoff_created_at: datetime | None,
) -> list[str]:
    errors: list[str] = []
    expected = {
        "handoff_type": "formal-pre-submission-check",
        "handoff_package_schema_version": "1.0",
        "handoff_status": "locked",
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            errors.append(f"{prefix}.payload.{field}: must equal {value!r}")
    if "handoff_package_version" in payload:
        errors.append(
            f"{prefix}.payload.handoff_package_version: legacy field is not allowed; "
            "use handoff_package_schema_version"
        )

    required = (
        "manuscript_id",
        "manuscript_revision",
        "chinese_manuscript_sha256",
        "author_lock_id",
        "english_translation_artifact_id",
        "english_translation_artifact_type",
        "english_translation_artifact_schema_version",
        "english_translation_version",
        "english_translation_sha256",
        "target_journal_contract_sha256",
    )
    for field in required:
        if not _has_content(payload.get(field)):
            errors.append(f"{prefix}.payload.{field}: must be present and non-empty")
    for field in (
        "chinese_manuscript_sha256",
        "english_translation_sha256",
        "target_journal_contract_sha256",
    ):
        if not _valid_hash(payload.get(field)):
            errors.append(f"{prefix}.payload.{field}: must be 64 lowercase hex characters")
    if payload.get("unresolved_blockers") != []:
        errors.append(f"{prefix}.payload.unresolved_blockers: must be an empty array")

    if payload.get("manuscript_id") != state.get("manuscript_id"):
        errors.append(f"{prefix}.payload.manuscript_id: must match pipeline manuscript_id")
    if payload.get("manuscript_revision") != state.get("manuscript_revision"):
        errors.append(f"{prefix}.payload.manuscript_revision: must match pipeline manuscript_revision")
    if isinstance(p3_output, dict) and payload.get("chinese_manuscript_sha256") != p3_output.get("sha256"):
        errors.append(f"{prefix}.payload.chinese_manuscript_sha256: must match current P3 output")
    if payload.get("target_journal_contract_sha256") != venue.get("contract_hash"):
        errors.append(f"{prefix}.payload.target_journal_contract_sha256: must match venue.contract_hash")

    binding = p3_content_state.get("author_lock_binding") if isinstance(p3_content_state, dict) else None
    lock_id = binding.get("lock_id") if isinstance(binding, dict) else None
    if payload.get("author_lock_id") != lock_id:
        errors.append(f"{prefix}.payload.author_lock_id: must match current P3 author lock")
    if not isinstance(author_decisions, list) or lock_id not in author_decisions:
        errors.append(f"{prefix}.author_decisions: must contain the current P3 author lock_id")
    if isinstance(binding, dict):
        lock_time = _parse_timestamp(
            binding.get("confirmed_at"),
            f"{prefix}.current_author_lock.confirmed_at",
            errors,
        )
        if (
            lock_time is not None
            and handoff_created_at is not None
            and lock_time > handoff_created_at
        ):
            errors.append(
                f"{prefix}.current_author_lock.confirmed_at: must not be later than handoff created_at"
            )

    if isinstance(source_output, dict):
        if sources != [source_output]:
            errors.append(f"{prefix}.source_artifacts: must be the exact current P4 output")
        payload_mapping = {
            "english_translation_artifact_id": "artifact_id",
            "english_translation_artifact_type": "artifact_type",
            "english_translation_artifact_schema_version": "artifact_schema_version",
            "english_translation_version": "version",
            "english_translation_sha256": "sha256",
        }
        for payload_key, output_key in payload_mapping.items():
            if payload.get(payload_key) != source_output.get(output_key):
                errors.append(f"{prefix}.payload.{payload_key}: must match current P4 output")
    return errors


def validate_state(data: Any) -> list[str]:
    """Return validation errors; an empty list means structurally valid."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: must be a JSON object"]

    if data.get("schema_version") != "1.0":
        errors.append("schema_version: must equal '1.0'")
    if not _is_nonempty_string(data.get("pipeline_id")):
        errors.append("pipeline_id: must be a non-empty string")
    if not _is_nonempty_string(data.get("manuscript_id")):
        errors.append("manuscript_id: must be a non-empty string")
    if not _is_nonempty_string(data.get("manuscript_revision")):
        errors.append("manuscript_revision: must be a non-empty string")
    if not isinstance(data.get("revision"), int) or isinstance(data.get("revision"), bool) or data.get("revision", 0) < 1:
        errors.append("revision: must be an integer >= 1")
    if data.get("current_stage") not in STAGES:
        errors.append("current_stage: unknown stage")

    stages = data.get("stages")
    if not isinstance(stages, dict):
        errors.append("stages: must be an object containing all five stages")
        stages = {}
    missing = [name for name in STAGES if name not in stages]
    extra = [name for name in stages if name not in STAGES]
    if missing:
        errors.append(f"stages: missing {', '.join(missing)}")
    if extra:
        errors.append(f"stages: unknown {', '.join(extra)}")

    active: list[str] = []
    focus: list[str] = []
    for name in STAGES:
        stage = stages.get(name)
        if not isinstance(stage, dict):
            if name in stages:
                errors.append(f"stages.{name}: must be an object")
            continue
        status = stage.get("status")
        if status not in STATUSES:
            errors.append(f"stages.{name}.status: invalid status")
        elif status == "active":
            active.append(name)
        if status in {"active", "waiting-human", "blocked"}:
            focus.append(name)
        revision = stage.get("revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
            errors.append(f"stages.{name}.revision: must be an integer >= 0")
        inputs = stage.get("input_versions")
        if not isinstance(inputs, dict):
            errors.append(f"stages.{name}.input_versions: must be an object")
        else:
            for upstream, version in inputs.items():
                if upstream not in STAGES:
                    errors.append(f"stages.{name}.input_versions: unknown stage {upstream!r}")
                if not isinstance(version, int) or isinstance(version, bool) or version < 0:
                    errors.append(f"stages.{name}.input_versions.{upstream}: must be an integer >= 0")
        for field in ("blocked_by", "invalidated_by"):
            if not isinstance(stage.get(field), list):
                errors.append(f"stages.{name}.{field}: must be an array")
        if status in {"waiting-human", "blocked"} and not stage.get("blocked_by"):
            errors.append(f"stages.{name}.blocked_by: required for {status}")

        output = stage.get("output")
        if status == "complete" and not isinstance(output, dict):
            errors.append(f"stages.{name}.output: required when complete")
        if status == "complete" and stage.get("invalidated_by"):
            errors.append(f"stages.{name}: complete stage cannot be invalidated")
        if status == "complete" and stage.get("blocked_by"):
            errors.append(f"stages.{name}: complete stage cannot have blockers")
        if isinstance(output, dict):
            for field in ("artifact_id", "artifact_type", "path", "version"):
                if not _is_nonempty_string(output.get(field)):
                    errors.append(f"stages.{name}.output.{field}: must be a non-empty string")
            if not _valid_hash(output.get("sha256")):
                errors.append(f"stages.{name}.output.sha256: must be 64 lowercase hex characters")
            semantic_schema = STAGE_ARTIFACT_SCHEMAS.get(name)
            if status == "complete" and semantic_schema:
                for field, expected in semantic_schema.items():
                    if output.get(field) != expected:
                        errors.append(f"stages.{name}.output.{field}: must equal {expected!r}")
            if (
                name == "chinese-finalization"
                and status == "complete"
                and output.get("artifact_type") != "chinese-manuscript-s7"
            ):
                errors.append("stages.chinese-finalization.output.artifact_type: complete P3 must be chinese-manuscript-s7")
            if (
                name == "chinese-finalization"
                and status == "complete"
                and output.get("version") != data.get("manuscript_revision")
            ):
                errors.append("stages.chinese-finalization.output.version: must match manuscript_revision")

        if name == "chinese-finalization" and status == "complete":
            content_state = stage.get("content_state")
            if not isinstance(content_state, dict):
                errors.append("stages.chinese-finalization.content_state: required when complete")
            else:
                if content_state.get("generic_chinese_status") != "S7":
                    errors.append("stages.chinese-finalization.content_state.generic_chinese_status: must equal S7")
                if not isinstance(content_state.get("affected_sections"), list):
                    errors.append("stages.chinese-finalization.content_state.affected_sections: must be an array")

    if len(active) > 1:
        errors.append("stages: at most one stage may be active")
    if active and data.get("current_stage") != active[0]:
        errors.append("current_stage: must equal the active stage")
    if len(focus) > 1:
        errors.append("stages: at most one stage may be active, waiting-human, or blocked")
    if focus and data.get("current_stage") != focus[0]:
        errors.append("current_stage: must equal the active/waiting/blocked stage")
    all_complete = all(
        isinstance(stages.get(name), dict) and stages[name].get("status") == "complete"
        for name in STAGES
    )
    if not focus and not all_complete:
        errors.append("stages: unfinished pipeline requires exactly one active/waiting/blocked current stage")

    venue = data.get("venue")
    if not isinstance(venue, dict):
        errors.append("venue: must be an object")
        venue = {}
    mode = venue.get("mode")
    journal_contract = stages.get("journal-contract")
    journal_contract_status = (
        journal_contract.get("status") if isinstance(journal_contract, dict) else None
    )
    if mode not in {"unselected", "locked", "venue-pending"}:
        errors.append("venue.mode: must be 'unselected', 'locked', or 'venue-pending'")
    elif mode == "locked":
        if journal_contract_status != "complete":
            errors.append("stages.journal-contract.status: must be complete when venue.mode is locked")
        for field in VENUE_BINDING_FIELDS:
            if not _is_nonempty_string(venue.get(field)):
                errors.append(f"venue.{field}: required when locked")
        for field in ("decision_hash", "contract_hash"):
            if not _valid_hash(venue.get(field)):
                errors.append(f"venue.{field}: required as SHA-256 when locked")
        if Path(str(venue.get("decision_path", ""))).name != "target-journal-decision.md":
            errors.append("venue.decision_path: must end with target-journal-decision.md")
        if Path(str(venue.get("contract_path", ""))).name != "target-journal-writing-contract.md":
            errors.append("venue.contract_path: must end with target-journal-writing-contract.md")
        if venue.get("decision_schema_version") != "1.0":
            errors.append("venue.decision_schema_version: must equal journal decision schema 1.0")
        if venue.get("contract_version") != "2.0":
            errors.append("venue.contract_version: must equal journal contract version 2.0")
        if venue.get("bypass") is not None:
            errors.append("venue.bypass: must be null when locked")
    elif mode == "unselected":
        if journal_contract_status == "complete":
            errors.append("stages.journal-contract.status: must not be complete when venue.mode is unselected")
        for field in (*VENUE_BINDING_FIELDS, "bypass"):
            if venue.get(field) is not None:
                errors.append(f"venue.{field}: must be null in unselected mode")
        for name in ("chinese-finalization", "english-translation", "pre-submission-check"):
            status = stages.get(name, {}).get("status") if isinstance(stages.get(name), dict) else None
            if status in {"active", "complete"}:
                errors.append(f"stages.{name}: cannot be {status} while venue is unselected")
    elif mode == "venue-pending":
        if journal_contract_status == "complete":
            errors.append("stages.journal-contract.status: must not be complete when venue.mode is venue-pending")
        for field in VENUE_BINDING_FIELDS:
            if venue.get(field) is not None:
                errors.append(f"venue.{field}: must be null in venue-pending mode")
        bypass = venue.get("bypass")
        if not isinstance(bypass, dict):
            errors.append("venue.bypass: required in venue-pending mode")
        else:
            if set(bypass) != BYPASS_KEYS:
                errors.append(
                    f"venue.bypass: must contain exactly {sorted(BYPASS_KEYS)!r}"
                )
            _parse_timestamp(
                bypass.get("authorized_at"),
                "venue.bypass.authorized_at",
                errors,
            )
            if not _is_nonempty_string(bypass.get("reason")):
                errors.append("venue.bypass.reason: must be a non-empty string")
            if bypass.get("resume_stage") != "journal-contract":
                errors.append("venue.bypass.resume_stage: must equal 'journal-contract'")
            baselines = bypass.get("baseline_stage_revisions")
            if not isinstance(baselines, dict):
                errors.append("venue.bypass.baseline_stage_revisions: must be an object")
            else:
                expected_baseline_keys = set(BYPASS_STAGE_NAMES)
                if set(baselines) != expected_baseline_keys:
                    errors.append(
                        "venue.bypass.baseline_stage_revisions: "
                        f"must contain exactly {sorted(expected_baseline_keys)!r}"
                    )
                for name in BYPASS_STAGE_NAMES:
                    baseline = baselines.get(name)
                    if (
                        not isinstance(baseline, int)
                        or isinstance(baseline, bool)
                        or baseline < 0
                    ):
                        errors.append(
                            f"venue.bypass.baseline_stage_revisions.{name}: "
                            "must be an integer >= 0"
                        )
                        continue
                    stage = stages.get(name)
                    current_revision = stage.get("revision") if isinstance(stage, dict) else None
                    if not isinstance(current_revision, int) or isinstance(current_revision, bool):
                        continue
                    if baseline > current_revision:
                        errors.append(
                            f"venue.bypass.baseline_stage_revisions.{name}: "
                            "must not exceed the current stage revision"
                        )
                    elif name != "chinese-finalization" and baseline != current_revision:
                        errors.append(
                            f"venue.bypass.baseline_stage_revisions.{name}: "
                            "must equal the stage revision recorded when the bypass is established"
                        )
            invalidates = bypass.get("invalidate_on_lock")
            required_invalidations = set(BYPASS_STAGE_NAMES)
            exact_invalidations = (
                isinstance(invalidates, list)
                and len(invalidates) == len(BYPASS_STAGE_NAMES)
                and all(isinstance(item, str) for item in invalidates)
                and set(invalidates) == required_invalidations
            )
            if not exact_invalidations:
                errors.append(
                    "venue.bypass.invalidate_on_lock: must contain exactly one each of P3, P4, and P5"
                )
        pending_p3 = stages.get("chinese-finalization")
        if isinstance(pending_p3, dict):
            if pending_p3.get("status") == "complete":
                errors.append(
                    "stages.chinese-finalization.status: must not be complete while venue.mode is venue-pending"
                )
            pending_content_state = pending_p3.get("content_state")
            if isinstance(pending_content_state, dict):
                pending_generic_status = pending_content_state.get("generic_chinese_status")
                if (
                    pending_generic_status is not None
                    and (
                        not isinstance(pending_generic_status, str)
                        or pending_generic_status not in VENUE_PENDING_CHINESE_STATUSES
                    )
                ):
                    errors.append(
                        "stages.chinese-finalization.content_state.generic_chinese_status: "
                        "must be between S0 and S6 while venue.mode is venue-pending"
                    )
                if pending_content_state.get("author_lock_binding") is not None:
                    errors.append(
                        "stages.chinese-finalization.content_state.author_lock_binding: "
                        "must be null while venue.mode is venue-pending"
                    )
            pending_output = pending_p3.get("output")
            if (
                isinstance(pending_output, dict)
                and pending_output.get("artifact_type") == "chinese-manuscript-s7"
            ):
                errors.append(
                    "stages.chinese-finalization.output.artifact_type: "
                    "must not claim chinese-manuscript-s7 while venue.mode is venue-pending"
                )
        for name in ("english-translation", "pre-submission-check"):
            status = stages.get(name, {}).get("status") if isinstance(stages.get(name), dict) else None
            if status in {"active", "complete"}:
                errors.append(f"stages.{name}: cannot be {status} while venue is pending")

    p3_author_lock_time: datetime | None = None
    p3 = stages.get("chinese-finalization")
    if isinstance(p3, dict) and p3.get("status") == "complete":
        content_state = p3.get("content_state")
        output = p3.get("output")
        if isinstance(content_state, dict) and isinstance(output, dict):
            binding = content_state.get("author_lock_binding")
            if mode == "locked":
                if content_state.get("journal_adaptation_status") != "contract-applied":
                    errors.append("stages.chinese-finalization.content_state.journal_adaptation_status: must be contract-applied")
                if not isinstance(binding, dict):
                    errors.append("stages.chinese-finalization.content_state.author_lock_binding: required when venue is locked")
                else:
                    expected_binding_keys = {
                        "lock_id",
                        "status",
                        "confirmed_by",
                        "confirmed_at",
                        "manuscript_id",
                        "manuscript_revision",
                        "manuscript_sha256",
                        "contract_version",
                        "contract_sha256",
                    }
                    if set(binding) != expected_binding_keys:
                        errors.append(
                            "stages.chinese-finalization.content_state.author_lock_binding: "
                            f"must contain exactly {sorted(expected_binding_keys)!r}"
                        )
                    binding_time = _parse_timestamp(
                        binding.get("confirmed_at"),
                        "stages.chinese-finalization.content_state.author_lock_binding.confirmed_at",
                        errors,
                    )
                    if (
                        content_state.get("journal_adaptation_status") == "contract-applied"
                        and binding.get("contract_sha256") == venue.get("contract_hash")
                    ):
                        p3_author_lock_time = binding_time
                    expected_binding = {
                        "lock_id": binding.get("lock_id"),
                        "status": "locked",
                        "confirmed_at": binding.get("confirmed_at"),
                        "manuscript_id": data.get("manuscript_id"),
                        "manuscript_revision": data.get("manuscript_revision"),
                        "manuscript_sha256": output.get("sha256"),
                        "contract_version": venue.get("contract_version"),
                        "contract_sha256": venue.get("contract_hash"),
                    }
                    for field in ("lock_id", "confirmed_by"):
                        if not _is_nonempty_string(binding.get(field)):
                            errors.append(
                                f"stages.chinese-finalization.content_state.author_lock_binding.{field}: must be a non-empty string"
                            )
                    for field, expected in expected_binding.items():
                        if binding.get(field) != expected:
                            errors.append(
                                f"stages.chinese-finalization.content_state.author_lock_binding.{field}: must match current manuscript/contract"
                            )
            elif mode == "venue-pending":
                if content_state.get("journal_adaptation_status") != "venue-pending":
                    errors.append("stages.chinese-finalization.content_state.journal_adaptation_status: must be venue-pending")
                if binding is not None:
                    errors.append("stages.chinese-finalization.content_state.author_lock_binding: must be null while venue is pending")

    for name in STAGES:
        stage = stages.get(name)
        if not isinstance(stage, dict) or stage.get("status") not in {"active", "waiting-human", "complete"}:
            continue
        dependencies = DEPENDENCIES[name]
        if name == "chinese-finalization" and mode == "venue-pending":
            dependencies = ("chinese-evidence-profile",)
        inputs = stage.get("input_versions") if isinstance(stage.get("input_versions"), dict) else {}
        for dependency in dependencies:
            upstream = stages.get(dependency)
            if not isinstance(upstream, dict) or upstream.get("status") != "complete":
                errors.append(f"stages.{name}: requires complete upstream stage {dependency}")
                continue
            upstream_revision = upstream.get("revision")
            if inputs.get(dependency) != upstream_revision:
                errors.append(
                    f"stages.{name}.input_versions.{dependency}: must equal upstream revision {upstream_revision}"
                )

    current = stages.get(data.get("current_stage"))
    if isinstance(current, dict) and current.get("status") == "complete":
        if any(isinstance(stages.get(name), dict) and stages[name].get("status") != "complete" for name in STAGES):
            errors.append("current_stage: cannot point to a complete stage while later work remains")

    handoffs = data.get("handoffs")
    handoff_pair_counts = {pair: 0 for pair in FORMAL_HANDOFF_SKILLS}
    formal_handoff_times: dict[tuple[str, str], list[datetime]] = {
        pair: [] for pair in FORMAL_HANDOFF_SKILLS
    }
    if not isinstance(handoffs, list):
        errors.append("handoffs: must be an array")
    else:
        seen: set[str] = set()
        for index, handoff in enumerate(handoffs):
            prefix = f"handoffs[{index}]"
            if not isinstance(handoff, dict):
                errors.append(f"{prefix}: must be an object")
                continue
            handoff_id = handoff.get("handoff_id")
            if not _is_nonempty_string(handoff_id):
                errors.append(f"{prefix}.handoff_id: must be a non-empty string")
            elif handoff_id in seen:
                errors.append(f"{prefix}.handoff_id: duplicate")
            else:
                seen.add(handoff_id)
            for field in ("from_stage", "to_stage"):
                if handoff.get(field) not in STAGES:
                    errors.append(f"{prefix}.{field}: unknown stage")
            for field in ("from_skill", "to_skill"):
                if handoff.get(field) not in SKILLS:
                    errors.append(f"{prefix}.{field}: unknown skill")
            pair = (handoff.get("from_stage"), handoff.get("to_stage"))
            expected_skills = FORMAL_HANDOFF_SKILLS.get(pair)
            if expected_skills is not None:
                handoff_pair_counts[pair] += 1
                expected_from_skill, expected_to_skill = expected_skills
                if handoff.get("from_skill") != expected_from_skill:
                    errors.append(f"{prefix}.from_skill: must equal {expected_from_skill!r}")
                if handoff.get("to_skill") != expected_to_skill:
                    errors.append(f"{prefix}.to_skill: must equal {expected_to_skill!r}")
            handoff_created_at = _parse_timestamp(
                handoff.get("created_at"),
                f"{prefix}.created_at",
                errors,
            )
            if expected_skills is not None and handoff_created_at is not None:
                formal_handoff_times[pair].append(handoff_created_at)
            sources = handoff.get("source_artifacts")
            if not isinstance(sources, list) or not sources:
                errors.append(f"{prefix}.source_artifacts: must be a non-empty array")
            else:
                source_ids: set[str] = set()
                source_by_type: dict[str, dict[str, Any]] = {}
                for source_index, source in enumerate(sources):
                    source_prefix = f"{prefix}.source_artifacts[{source_index}]"
                    if not isinstance(source, dict):
                        errors.append(f"{source_prefix}: must be an object")
                        continue
                    for field in ("artifact_id", "artifact_type", "path", "version"):
                        if not _is_nonempty_string(source.get(field)):
                            errors.append(f"{source_prefix}.{field}: must be a non-empty string")
                    if not _valid_hash(source.get("sha256")):
                        errors.append(f"{source_prefix}.sha256: invalid SHA-256")
                    if _is_nonempty_string(source.get("artifact_id")):
                        if source["artifact_id"] in source_ids:
                            errors.append(f"{source_prefix}.artifact_id: duplicate within handoff")
                        else:
                            source_ids.add(source["artifact_id"])
                    if _is_nonempty_string(source.get("artifact_type")):
                        if source["artifact_type"] in source_by_type:
                            errors.append(f"{source_prefix}.artifact_type: duplicate within handoff")
                        source_by_type[source["artifact_type"]] = source
                if (
                    handoff.get("from_stage") == "journal-contract"
                    and handoff.get("to_stage") == "chinese-finalization"
                ):
                    expected_journal_sources = {
                        "target_journal_decision": {
                            "path": venue.get("decision_path"),
                            "version": venue.get("decision_schema_version"),
                            "sha256": venue.get("decision_hash"),
                        },
                        "target_journal_writing_contract": {
                            "path": venue.get("contract_path"),
                            "version": venue.get("contract_version"),
                            "sha256": venue.get("contract_hash"),
                        },
                    }
                    for artifact_type, expected in expected_journal_sources.items():
                        source = source_by_type.get(artifact_type)
                        if source is None:
                            errors.append(f"{prefix}.source_artifacts: missing {artifact_type}")
                            continue
                        for field, expected_value in expected.items():
                            if source.get(field) != expected_value:
                                errors.append(
                                    f"{prefix}.source_artifacts.{artifact_type}.{field}: must match venue binding"
                                )
            payload = handoff.get("payload")
            if not isinstance(payload, dict):
                errors.append(f"{prefix}.payload: must be an object")
            elif (
                handoff.get("from_stage") == "chinese-finalization"
                and handoff.get("to_stage") == "english-translation"
            ):
                source_output = stages.get("chinese-finalization", {}).get("output")
                errors.extend(_validate_translation_payload(
                    payload,
                    prefix,
                    data,
                    venue,
                    source_output if isinstance(source_output, dict) else None,
                    sources if isinstance(sources, list) else None,
                    handoff.get("author_decisions"),
                    stages.get("chinese-finalization", {}).get("content_state"),
                    handoff_created_at,
                ))
            elif (
                handoff.get("from_stage") == "english-translation"
                and handoff.get("to_stage") == "pre-submission-check"
            ):
                source_output = stages.get("english-translation", {}).get("output")
                p3_output = stages.get("chinese-finalization", {}).get("output")
                errors.extend(_validate_presubmission_payload(
                    payload,
                    prefix,
                    data,
                    venue,
                    source_output if isinstance(source_output, dict) else None,
                    sources if isinstance(sources, list) else None,
                    handoff.get("author_decisions"),
                    p3_output if isinstance(p3_output, dict) else None,
                    stages.get("chinese-finalization", {}).get("content_state"),
                    handoff_created_at,
                ))
            for field in ("author_decisions", "open_questions", "blockers"):
                if not isinstance(handoff.get(field), list):
                    errors.append(f"{prefix}.{field}: must be an array")
            if (
                handoff.get("from_stage"), handoff.get("to_stage")
            ) in {
                ("journal-contract", "chinese-finalization"),
                ("chinese-finalization", "english-translation"),
                ("english-translation", "pre-submission-check"),
            }:
                if handoff.get("open_questions") != []:
                    errors.append(f"{prefix}.open_questions: formal handoff must have no open questions")
                if handoff.get("blockers") != []:
                    errors.append(f"{prefix}.blockers: formal handoff must have no blockers")
                if not isinstance(handoff.get("author_decisions"), list) or not handoff.get("author_decisions"):
                    errors.append(f"{prefix}.author_decisions: formal handoff requires recorded author decision(s)")

    for pair, count in handoff_pair_counts.items():
        if count > 1:
            errors.append(
                f"handoffs: at most one formal {pair[0]} to {pair[1]} handoff is allowed"
            )

    def single_handoff_time(pair: tuple[str, str]) -> datetime | None:
        times = formal_handoff_times[pair]
        return times[0] if len(times) == 1 else None

    ordered_formal_events = (
        (
            "P2->P3.created_at",
            single_handoff_time(("journal-contract", "chinese-finalization")),
        ),
        ("P3 author_lock.confirmed_at", p3_author_lock_time),
        (
            "P3->P4.created_at",
            single_handoff_time(("chinese-finalization", "english-translation")),
        ),
        (
            "P4->P5.created_at",
            single_handoff_time(("english-translation", "pre-submission-check")),
        ),
    )
    for (earlier_label, earlier), (later_label, later) in zip(
        ordered_formal_events,
        ordered_formal_events[1:],
    ):
        if earlier is not None and later is not None and earlier > later:
            errors.append(
                f"formal event order: {earlier_label} must be <= {later_label}"
            )

    p3_status = stages.get("chinese-finalization", {}).get("status") if isinstance(stages.get("chinese-finalization"), dict) else None
    p4_status = stages.get("english-translation", {}).get("status") if isinstance(stages.get("english-translation"), dict) else None
    if mode == "locked" and p3_status in {"active", "waiting-human", "complete"}:
        if handoff_pair_counts[("journal-contract", "chinese-finalization")] != 1:
            errors.append("handoffs: locked-venue P3 requires exactly one P2 to P3 formal journal handoff")
    if p4_status in {"active", "waiting-human", "complete"}:
        if handoff_pair_counts[("chinese-finalization", "english-translation")] != 1:
            errors.append("handoffs: P4 requires exactly one formal P3 to P4 S7 translation handoff")
    p5_status = stages.get("pre-submission-check", {}).get("status") if isinstance(stages.get("pre-submission-check"), dict) else None
    if p5_status in {"active", "waiting-human", "complete"}:
        if handoff_pair_counts[("english-translation", "pre-submission-check")] != 1:
            errors.append("handoffs: P5 requires exactly one formal P4 to P5 handoff matching current P4 output")

    return errors


def validate_files(data: dict[str, Any], state_path: Path) -> list[str]:
    """Verify outputs, handoff sources, and path-based locked ledgers against SHA-256."""
    errors: list[str] = []
    base = state_path.resolve().parent
    records: list[tuple[str, dict[str, Any]]] = []
    stages = data.get("stages")
    if isinstance(stages, dict):
        for name, stage in stages.items():
            if isinstance(stage, dict) and isinstance(stage.get("output"), dict):
                records.append((f"stages.{name}.output", stage["output"]))
    handoffs = data.get("handoffs")
    if isinstance(handoffs, list):
        for index, handoff in enumerate(handoffs):
            if not isinstance(handoff, dict):
                continue
            sources = handoff.get("source_artifacts")
            if isinstance(sources, list):
                for source_index, source in enumerate(sources):
                    if isinstance(source, dict):
                        records.append((f"handoffs[{index}].source_artifacts[{source_index}]", source))
            if (
                handoff.get("from_stage") == "chinese-finalization"
                and handoff.get("to_stage") == "english-translation"
                and isinstance(handoff.get("payload"), dict)
            ):
                payload = handoff["payload"]
                for field in LOCKED_LEDGER_FIELDS:
                    ledger = payload.get(field)
                    if isinstance(ledger, dict) and set(ledger) == {"path", "sha256"}:
                        records.append((f"handoffs[{index}].payload.{field}", ledger))

    for label, record in records:
        raw_path = record.get("path")
        if not _is_nonempty_string(raw_path):
            continue
        artifact_path = Path(raw_path)
        if not artifact_path.is_absolute():
            artifact_path = base / artifact_path
        try:
            actual = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        except FileNotFoundError:
            errors.append(f"{label}.path: file not found: {artifact_path}")
            continue
        except OSError as exc:
            errors.append(f"{label}.path: cannot read {artifact_path}: {exc}")
            continue
        if actual != record.get("sha256"):
            errors.append(f"{label}.sha256: does not match file bytes")
    return errors


def _valid_example() -> dict[str, Any]:
    stages: dict[str, Any] = {}
    for name in STAGES:
        stages[name] = {
            "status": "pending",
            "revision": 0,
            "input_versions": {},
            "output": None,
            "blocked_by": [],
            "invalidated_by": [],
        }
    stages["chinese-evidence-profile"]["status"] = "active"
    return {
        "schema_version": "1.0",
        "pipeline_id": "self-test",
        "manuscript_id": "ms-001",
        "manuscript_revision": "r1",
        "revision": 1,
        "current_stage": "chinese-evidence-profile",
        "venue": {
            "mode": "unselected",
            "target_journal": None,
            "article_type": None,
            "decision_path": None,
            "decision_schema_version": None,
            "decision_hash": None,
            "contract_path": None,
            "contract_version": None,
            "contract_hash": None,
            "selection_evidence_version": None,
            "writing_profile_evidence_id": None,
            "bypass": None,
        },
        "stages": stages,
        "handoffs": [],
    }


def _valid_pending_example() -> dict[str, Any]:
    state = _valid_example()
    state["venue"] = {
        "mode": "venue-pending",
        "target_journal": None,
        "article_type": None,
        "decision_path": None,
            "decision_schema_version": None,
        "decision_hash": None,
        "contract_path": None,
        "contract_version": None,
        "contract_hash": None,
        "selection_evidence_version": None,
        "writing_profile_evidence_id": None,
        "bypass": {
            "authorized_at": "2026-08-10T12:00:00+08:00",
            "reason": "self-test",
            "resume_stage": "journal-contract",
            "baseline_stage_revisions": {
                "chinese-finalization": 0,
                "english-translation": 0,
                "pre-submission-check": 0,
            },
            "invalidate_on_lock": [
                "chinese-finalization",
                "english-translation",
                "pre-submission-check",
            ],
        },
    }
    return state


def _valid_locked_example() -> dict[str, Any]:
    state = _valid_example()
    digest = "a" * 64
    state["revision"] = 6
    state["current_stage"] = "pre-submission-check"
    state["venue"] = {
        "mode": "locked",
        "target_journal": "Example Journal",
        "article_type": "Research Article",
        "decision_path": "artifacts/target-journal-decision.md",
        "decision_schema_version": "1.0",
        "decision_hash": digest,
        "contract_path": "artifacts/target-journal-writing-contract.md",
        "contract_version": "2.0",
        "contract_hash": digest,
        "selection_evidence_version": "ev-001",
        "writing_profile_evidence_id": "profile-001",
        "bypass": None,
    }
    for index, name in enumerate(STAGES, start=1):
        dependencies = DEPENDENCIES[name]
        state["stages"][name] = {
            "status": "complete",
            "revision": 1,
            "input_versions": {dependency: 1 for dependency in dependencies},
            "output": {
                "artifact_id": f"artifact-{index}",
                "artifact_type": (
                    "chinese-manuscript-s7"
                    if name == "chinese-finalization"
                    else STAGE_ARTIFACT_SCHEMAS.get(name, {}).get("artifact_type", f"stage-{index}-output")
                ),
                "path": f"artifacts/stage-{index}.json",
                "version": "r1" if name == "chinese-finalization" else "1.0",
                "sha256": digest,
            },
            "blocked_by": [],
            "invalidated_by": [],
        }
        if name in STAGE_ARTIFACT_SCHEMAS:
            state["stages"][name]["output"]["artifact_schema_version"] = (
                STAGE_ARTIFACT_SCHEMAS[name]["artifact_schema_version"]
            )
    state["stages"]["chinese-finalization"]["content_state"] = {
        "generic_chinese_status": "S7",
        "journal_adaptation_status": "contract-applied",
        "author_lock_binding": {
            "lock_id": "author-lock-001",
            "status": "locked",
            "confirmed_by": "author-001",
            "confirmed_at": "2026-08-10T12:40:00+08:00",
            "manuscript_id": "ms-001",
            "manuscript_revision": "r1",
            "manuscript_sha256": digest,
            "contract_version": "2.0",
            "contract_sha256": digest,
        },
        "affected_sections": [],
    }
    state["handoffs"] = [
        {
            "handoff_id": "h-journal-to-chinese",
            "from_stage": "journal-contract",
            "to_stage": "chinese-finalization",
            "from_skill": "journal-navigator",
            "to_skill": "paper-navigator",
            "created_at": "2026-08-10T12:30:00+08:00",
            "source_artifacts": [
                {
                    "artifact_id": "journal-decision-r1",
                    "artifact_type": "target_journal_decision",
                    "path": "artifacts/target-journal-decision.md",
                    "version": "1.0",
                    "sha256": digest,
                },
                {
                    "artifact_id": "journal-contract-r1",
                    "artifact_type": "target_journal_writing_contract",
                    "path": "artifacts/target-journal-writing-contract.md",
                    "version": "2.0",
                    "sha256": digest,
                },
            ],
            "payload": {},
            "author_decisions": ["author-selected-example-journal"],
            "open_questions": [],
            "blockers": [],
        }
        ,
        {
            "handoff_id": "h-chinese-to-english",
            "from_stage": "chinese-finalization",
            "to_stage": "english-translation",
            "from_skill": "paper-navigator",
            "to_skill": "zh-en-paper-translator",
            "created_at": "2026-08-10T12:45:00+08:00",
            "source_artifacts": [
                {
                    "artifact_id": "artifact-3",
                    "artifact_type": "chinese-manuscript-s7",
                    "path": "artifacts/stage-3.json",
                    "version": "r1",
                    "sha256": digest,
                }
            ],
            "payload": {
                "handoff_type": "formal-full-manuscript-translation",
                "handoff_package_schema_version": "1.0",
                "handoff_status": "locked",
                "chinese_manuscript_status": "S7",
                "manuscript_id": "ms-001",
                "manuscript_revision": "r1",
                "chinese_manuscript_sha256": digest,
                "author_lock_record": {
                    "lock_id": "author-lock-001",
                    "status": "locked",
                    "confirmed_by": "author-001",
                    "confirmed_at": "2026-08-10T12:40:00+08:00",
                    "manuscript_id": "ms-001",
                    "manuscript_revision": "r1",
                    "manuscript_sha256": digest,
                },
                "locked_thesis_and_contributions": {"inline": ["thesis-001", "contribution-001"]},
                "terminology_ledger": {"path": "artifacts/terms.tsv", "sha256": digest},
                "locked_numbers_and_units": {"inline": {"status": "locked"}},
                "locked_claim_boundaries": {"inline": "boundaries locked"},
                "locked_citations_and_cross_references": {"inline": ["citation-ledger-001"]},
                "unresolved_blockers": [],
                "target_journal_status": "contract-confirmed",
                "target_journal": "Example Journal",
                "target_journal_article_type": "Research Article",
                "target_journal_decision_file": "artifacts/target-journal-decision.md",
                "target_journal_decision_schema_version": "1.0",
                "target_journal_decision_sha256": digest,
                "target_journal_contract_file": "artifacts/target-journal-writing-contract.md",
                "target_journal_contract_version": "2.0",
                "target_journal_contract_sha256": digest,
                "target_journal_selection_evidence_version": "ev-001",
                "target_journal_writing_profile_evidence_id": "profile-001",
            },
            "author_decisions": ["author-lock-001"],
            "open_questions": [],
            "blockers": [],
        },
        {
            "handoff_id": "h-english-to-preflight",
            "from_stage": "english-translation",
            "to_stage": "pre-submission-check",
            "from_skill": "zh-en-paper-translator",
            "to_skill": "paperline",
            "created_at": "2026-08-10T13:00:00+08:00",
            "source_artifacts": [
                {
                    "artifact_id": "artifact-4",
                    "artifact_type": "english-translation-package",
                    "artifact_schema_version": "1.0",
                    "path": "artifacts/stage-4.json",
                    "version": "1.0",
                    "sha256": digest,
                }
            ],
            "payload": {
                "handoff_type": "formal-pre-submission-check",
                "handoff_package_schema_version": "1.0",
                "handoff_status": "locked",
                "manuscript_id": "ms-001",
                "manuscript_revision": "r1",
                "chinese_manuscript_sha256": digest,
                "author_lock_id": "author-lock-001",
                "english_translation_artifact_id": "artifact-4",
                "english_translation_artifact_type": "english-translation-package",
                "english_translation_artifact_schema_version": "1.0",
                "english_translation_version": "1.0",
                "english_translation_sha256": digest,
                "target_journal_contract_sha256": digest,
                "unresolved_blockers": [],
            },
            "author_decisions": ["author-lock-001"],
            "open_questions": [],
            "blockers": [],
        },
    ]
    return state


def run_self_test() -> int:
    valid = _valid_example()
    pending = _valid_pending_example()
    locked = _valid_locked_example()

    pending_progress = json.loads(json.dumps(pending))
    pending_progress["revision"] = 2
    pending_progress["current_stage"] = "chinese-finalization"
    pending_progress["stages"]["chinese-evidence-profile"] = json.loads(
        json.dumps(locked["stages"]["chinese-evidence-profile"])
    )
    pending_progress["stages"]["chinese-finalization"].update({
        "status": "active",
        "revision": 1,
        "input_versions": {"chinese-evidence-profile": 1},
        "output": None,
        "blocked_by": [],
        "invalidated_by": [],
    })

    locked_rollback = json.loads(json.dumps(locked))
    current_digest = "b" * 64
    locked_rollback["venue"]["decision_hash"] = current_digest
    locked_rollback["venue"]["contract_hash"] = current_digest
    locked_rollback["current_stage"] = "chinese-finalization"
    locked_rollback["stages"]["chinese-finalization"].update({
        "status": "active",
        "blocked_by": [],
        "invalidated_by": ["target-journal-contract-changed"],
    })
    for name in ("english-translation", "pre-submission-check"):
        locked_rollback["stages"][name]["status"] = "pending"
        locked_rollback["stages"][name]["blocked_by"] = []
        locked_rollback["stages"][name]["invalidated_by"] = [
            "target-journal-contract-changed"
        ]
    locked_rollback["stages"]["chinese-finalization"]["content_state"][
        "author_lock_binding"
    ]["confirmed_at"] = "2026-08-10T12:00:00+08:00"
    locked_rollback["handoffs"] = [locked_rollback["handoffs"][0]]
    for source in locked_rollback["handoffs"][0]["source_artifacts"]:
        source["sha256"] = current_digest

    checks: list[tuple[str, dict[str, Any], bool]] = [
        ("valid unselected state", valid, True),
        ("valid venue-pending state", pending, True),
        ("valid venue-pending P3 progress with an older baseline revision", pending_progress, True),
        ("valid completed locked-venue state", locked, True),
        ("valid locked rollback retaining a stale historical P3 author lock", locked_rollback, True),
    ]

    duplicate_active = json.loads(json.dumps(valid))
    duplicate_active["stages"]["journal-contract"]["status"] = "active"
    checks.append(("reject duplicate active stages", duplicate_active, False))

    premature_translation = json.loads(json.dumps(pending))
    premature_translation["stages"]["chinese-evidence-profile"]["status"] = "pending"
    premature_translation["stages"]["english-translation"]["status"] = "active"
    premature_translation["current_stage"] = "english-translation"
    checks.append(("reject translation during venue-pending bypass", premature_translation, False))

    unselected_with_completed_p2 = json.loads(json.dumps(locked_rollback))
    unselected_with_completed_p2["venue"] = json.loads(json.dumps(valid["venue"]))
    unselected_with_completed_p2["handoffs"] = []
    unselected_with_completed_p2["stages"]["chinese-finalization"].update({
        "status": "blocked",
        "output": None,
        "blocked_by": ["venue-unselected"],
        "invalidated_by": [],
    })
    unselected_with_completed_p2["stages"]["chinese-finalization"].pop(
        "content_state",
        None,
    )
    for name in ("english-translation", "pre-submission-check"):
        unselected_with_completed_p2["stages"][name].update({
            "status": "pending",
            "output": None,
            "blocked_by": [],
            "invalidated_by": [],
        })
    checks.append((
        "reject complete P2 while venue mode is unselected",
        unselected_with_completed_p2,
        False,
    ))

    pending_with_completed_p2 = json.loads(json.dumps(pending_progress))
    pending_with_completed_p2["stages"]["journal-contract"] = json.loads(
        json.dumps(locked["stages"]["journal-contract"])
    )
    checks.append((
        "reject complete P2 while venue mode is venue-pending",
        pending_with_completed_p2,
        False,
    ))

    locked_without_completed_p2 = json.loads(json.dumps(valid))
    locked_without_completed_p2["venue"] = json.loads(json.dumps(locked["venue"]))
    checks.append((
        "reject locked venue mode without complete P2",
        locked_without_completed_p2,
        False,
    ))

    empty_bypass = json.loads(json.dumps(pending))
    empty_bypass["venue"]["bypass"] = {}
    checks.append(("reject empty venue-pending bypass", empty_bypass, False))

    bypass_with_unknown_key = json.loads(json.dumps(pending))
    bypass_with_unknown_key["venue"]["bypass"]["authorized_by"] = "author-001"
    checks.append(("reject venue-pending bypass with an unknown key", bypass_with_unknown_key, False))

    empty_bypass_reason = json.loads(json.dumps(pending))
    empty_bypass_reason["venue"]["bypass"]["reason"] = ""
    checks.append(("reject venue-pending bypass with an empty reason", empty_bypass_reason, False))

    offsetless_bypass_time = json.loads(json.dumps(pending))
    offsetless_bypass_time["venue"]["bypass"]["authorized_at"] = "2026-08-10T12:00:00"
    checks.append((
        "reject venue-pending bypass authorization without a UTC offset",
        offsetless_bypass_time,
        False,
    ))

    missing_baseline_stage = json.loads(json.dumps(pending))
    missing_baseline_stage["venue"]["bypass"]["baseline_stage_revisions"].pop(
        "pre-submission-check"
    )
    checks.append(("reject venue-pending baseline missing P5", missing_baseline_stage, False))

    extra_baseline_stage = json.loads(json.dumps(pending))
    extra_baseline_stage["venue"]["bypass"]["baseline_stage_revisions"][
        "journal-contract"
    ] = 0
    checks.append(("reject venue-pending baseline with an extra stage", extra_baseline_stage, False))

    string_baseline_revision = json.loads(json.dumps(pending))
    string_baseline_revision["venue"]["bypass"]["baseline_stage_revisions"][
        "chinese-finalization"
    ] = "0"
    checks.append(("reject string venue-pending baseline revision", string_baseline_revision, False))

    future_baseline_revision = json.loads(json.dumps(pending))
    future_baseline_revision["venue"]["bypass"]["baseline_stage_revisions"][
        "chinese-finalization"
    ] = 1
    checks.append(("reject venue-pending baseline newer than current P3", future_baseline_revision, False))

    stale_p4_baseline = json.loads(json.dumps(pending))
    stale_p4_baseline["stages"]["english-translation"]["revision"] = 1
    checks.append(("reject venue-pending P4 revision diverging from its baseline", stale_p4_baseline, False))

    duplicate_invalidation = json.loads(json.dumps(pending))
    duplicate_invalidation["venue"]["bypass"]["invalidate_on_lock"] = [
        "chinese-finalization",
        "english-translation",
        "english-translation",
    ]
    checks.append(("reject duplicate venue-pending invalidation stage", duplicate_invalidation, False))

    extra_invalidation = json.loads(json.dumps(pending))
    extra_invalidation["venue"]["bypass"]["invalidate_on_lock"].append(
        "journal-contract"
    )
    checks.append(("reject extra venue-pending invalidation stage", extra_invalidation, False))

    pending_completed_p3 = json.loads(json.dumps(pending_progress))
    pending_completed_p3["stages"]["chinese-finalization"]["status"] = "complete"
    checks.append(("reject complete P3 while venue mode is venue-pending", pending_completed_p3, False))

    pending_s7_claim = json.loads(json.dumps(pending_progress))
    pending_s7_claim["stages"]["chinese-finalization"]["content_state"] = {
        "generic_chinese_status": "S7",
        "journal_adaptation_status": "venue-pending",
        "author_lock_binding": None,
        "affected_sections": [],
    }
    checks.append(("reject S7 claim while venue mode is venue-pending", pending_s7_claim, False))

    pending_author_lock_claim = json.loads(json.dumps(pending_progress))
    pending_author_lock_claim["stages"]["chinese-finalization"]["content_state"] = {
        "generic_chinese_status": "S6",
        "journal_adaptation_status": "venue-pending",
        "author_lock_binding": json.loads(json.dumps(
            locked["stages"]["chinese-finalization"]["content_state"]["author_lock_binding"]
        )),
        "affected_sections": [],
    }
    checks.append((
        "reject structured P3 author lock while venue mode is venue-pending",
        pending_author_lock_claim,
        False,
    ))

    bad_hash = json.loads(json.dumps(valid))
    bad_hash["stages"]["chinese-evidence-profile"].update(
        {
            "status": "complete",
            "revision": 1,
            "output": {
                "artifact_id": "profile",
                "artifact_type": "research-profile",
                "path": "profile.json",
                "version": "1.0",
                "sha256": "not-a-hash",
            },
        }
    )
    checks.append(("reject invalid artifact hash", bad_hash, False))

    incomplete_journal_handoff = json.loads(json.dumps(locked))
    incomplete_journal_handoff["handoffs"][0]["source_artifacts"].pop()
    checks.append(("reject incomplete formal journal handoff", incomplete_journal_handoff, False))

    duplicate_journal_source_id = json.loads(json.dumps(locked))
    duplicate_journal_source_id["handoffs"][0]["source_artifacts"][1]["artifact_id"] = (
        duplicate_journal_source_id["handoffs"][0]["source_artifacts"][0]["artifact_id"]
    )
    checks.append((
        "reject P2 decision and contract sharing one source artifact_id",
        duplicate_journal_source_id,
        False,
    ))

    missing_s7 = json.loads(json.dumps(locked))
    missing_s7["handoffs"][1]["payload"]["chinese_manuscript_status"] = "S6"
    checks.append(("reject formal translation handoff without S7", missing_s7, False))

    missing_translation_handoff = json.loads(json.dumps(locked))
    missing_translation_handoff["handoffs"].pop(1)
    checks.append(("reject P4 without formal translation handoff", missing_translation_handoff, False))

    stale_after_journal_change = json.loads(json.dumps(locked))
    stale_after_journal_change["stages"]["journal-contract"]["revision"] = 2
    checks.append(("reject stale downstream state after journal change", stale_after_journal_change, False))

    wrong_manuscript_revision = json.loads(json.dumps(locked))
    wrong_manuscript_revision["handoffs"][1]["payload"]["manuscript_revision"] = "r0"
    checks.append(("reject translation payload for a different manuscript revision", wrong_manuscript_revision, False))

    non_hash_identity = json.loads(json.dumps(locked))
    non_hash_identity["handoffs"][1]["payload"]["chinese_manuscript_sha256"] = "latest-file"
    checks.append(("reject non-hash Chinese manuscript identity", non_hash_identity, False))

    wrong_contract_binding = json.loads(json.dumps(locked))
    wrong_contract_binding["handoffs"][1]["payload"]["target_journal_contract_version"] = "1.0"
    checks.append(("reject translation payload bound to wrong contract version", wrong_contract_binding, False))

    stale_source = json.loads(json.dumps(locked))
    stale_source["handoffs"][1]["source_artifacts"][0]["version"] = "r0"
    checks.append(("reject stale P3 source version in translation handoff", stale_source, False))

    wrapper_blocker = json.loads(json.dumps(locked))
    wrapper_blocker["handoffs"][1]["blockers"] = ["unresolved"]
    checks.append(("reject formal handoff with wrapper blocker", wrapper_blocker, False))

    wrapper_question = json.loads(json.dumps(locked))
    wrapper_question["handoffs"][1]["open_questions"] = ["which term"]
    checks.append(("reject formal handoff with open question", wrapper_question, False))

    completed_with_blocker = json.loads(json.dumps(locked))
    completed_with_blocker["stages"]["chinese-finalization"]["blocked_by"] = ["author"]
    checks.append(("reject completed stage with blocker", completed_with_blocker, False))

    changed_contract_hash = json.loads(json.dumps(locked))
    changed_contract_hash["venue"]["contract_hash"] = "b" * 64
    checks.append(("reject old P3/P4 bindings after contract bytes change", changed_contract_hash, False))

    string_author_lock = json.loads(json.dumps(locked))
    string_author_lock["handoffs"][1]["payload"]["author_lock_record"] = "author-lock-001"
    checks.append(("reject scalar author lock record", string_author_lock, False))

    wrong_author_lock_manuscript = json.loads(json.dumps(locked))
    wrong_author_lock_manuscript["handoffs"][1]["payload"]["author_lock_record"]["manuscript_id"] = "ms-other"
    checks.append(("reject author lock bound to another manuscript", wrong_author_lock_manuscript, False))

    wrong_author_lock_revision = json.loads(json.dumps(locked))
    wrong_author_lock_revision["handoffs"][1]["payload"]["author_lock_record"]["manuscript_revision"] = "r0"
    checks.append(("reject author lock bound to another revision", wrong_author_lock_revision, False))

    wrong_author_lock_hash = json.loads(json.dumps(locked))
    wrong_author_lock_hash["handoffs"][1]["payload"]["author_lock_record"]["manuscript_sha256"] = "b" * 64
    checks.append(("reject author lock bound to another manuscript hash", wrong_author_lock_hash, False))

    missing_wrapper_lock = json.loads(json.dumps(locked))
    missing_wrapper_lock["handoffs"][1]["author_decisions"] = ["another-lock"]
    checks.append(("reject author lock absent from wrapper decisions", missing_wrapper_lock, False))

    stale_p3_lock = json.loads(json.dumps(locked))
    stale_p3_lock["stages"]["chinese-finalization"]["content_state"]["author_lock_binding"]["lock_id"] = "old-lock"
    checks.append(("reject author lock not bound to current P3 content state", stale_p3_lock, False))

    invalid_lock_time = json.loads(json.dumps(locked))
    invalid_lock_time["stages"]["chinese-finalization"]["content_state"]["author_lock_binding"]["confirmed_at"] = "not-a-time"
    invalid_lock_time["handoffs"][1]["payload"]["author_lock_record"]["confirmed_at"] = "not-a-time"
    checks.append(("reject author lock without an offset-aware timestamp", invalid_lock_time, False))

    future_lock_time = json.loads(json.dumps(locked))
    future_lock_time["stages"]["chinese-finalization"]["content_state"]["author_lock_binding"]["confirmed_at"] = "2099-01-01T00:00:00+08:00"
    future_lock_time["handoffs"][1]["payload"]["author_lock_record"]["confirmed_at"] = "2099-01-01T00:00:00+08:00"
    checks.append(("reject author lock created after its formal handoff", future_lock_time, False))

    coherent_future_timeline = json.loads(json.dumps(locked))
    coherent_future_timeline["handoffs"][0]["created_at"] = "2099-01-01T12:30:00+08:00"
    coherent_future_timeline["stages"]["chinese-finalization"]["content_state"][
        "author_lock_binding"
    ]["confirmed_at"] = "2099-01-01T12:40:00+08:00"
    coherent_future_timeline["handoffs"][1]["payload"]["author_lock_record"][
        "confirmed_at"
    ] = "2099-01-01T12:40:00+08:00"
    coherent_future_timeline["handoffs"][1]["created_at"] = "2099-01-01T12:45:00+08:00"
    coherent_future_timeline["handoffs"][2]["created_at"] = "2099-01-01T13:00:00+08:00"
    checks.append((
        "reject a chronologically ordered formal timeline dated in 2099",
        coherent_future_timeline,
        False,
    ))

    p2_handoff_after_lock = json.loads(json.dumps(locked))
    p2_handoff_after_lock["handoffs"][0]["created_at"] = "2026-08-10T12:41:00+08:00"
    checks.append((
        "reject P2 to P3 handoff created after the P3 author lock",
        p2_handoff_after_lock,
        False,
    ))

    lock_after_p3_p4_handoff = json.loads(json.dumps(locked))
    lock_after_p3_p4_handoff["stages"]["chinese-finalization"]["content_state"][
        "author_lock_binding"
    ]["confirmed_at"] = "2026-08-10T12:46:00+08:00"
    lock_after_p3_p4_handoff["handoffs"][1]["payload"]["author_lock_record"][
        "confirmed_at"
    ] = "2026-08-10T12:46:00+08:00"
    checks.append((
        "reject P3 author lock confirmed after the P3 to P4 handoff",
        lock_after_p3_p4_handoff,
        False,
    ))

    p3_p4_after_p4_p5_handoff = json.loads(json.dumps(locked))
    p3_p4_after_p4_p5_handoff["handoffs"][1]["created_at"] = "2026-08-10T13:01:00+08:00"
    checks.append((
        "reject P3 to P4 handoff created after the P4 to P5 handoff",
        p3_p4_after_p4_p5_handoff,
        False,
    ))

    wrong_formal_skills = json.loads(json.dumps(locked))
    wrong_formal_skills["handoffs"][0]["from_skill"] = "paperline"
    wrong_formal_skills["handoffs"][0]["to_skill"] = "journal-navigator"
    checks.append(("reject formal handoff with wrong producer and consumer skills", wrong_formal_skills, False))

    extra_p3_source = json.loads(json.dumps(locked))
    extra_p3_source["handoffs"][1]["source_artifacts"].append({
        "artifact_id": "unlocked-extra",
        "artifact_type": "supplementary-note",
        "path": "artifacts/extra.txt",
        "version": "1.0",
        "sha256": "a" * 64,
    })
    checks.append(("reject P3 to P4 handoff with an extra source artifact", extra_p3_source, False))

    old_decision_version_name = json.loads(json.dumps(locked))
    value = old_decision_version_name["handoffs"][1]["payload"].pop("target_journal_decision_schema_version")
    old_decision_version_name["handoffs"][1]["payload"]["target_journal_decision_version"] = value
    checks.append(("reject legacy target journal decision version field", old_decision_version_name, False))

    conflicting_decision_version_name = json.loads(json.dumps(locked))
    conflicting_decision_version_name["handoffs"][1]["payload"]["target_journal_decision_version"] = "0.9"
    checks.append((
        "reject coexisting legacy target journal decision version field",
        conflicting_decision_version_name,
        False,
    ))

    conflicting_handoff_package_version = json.loads(json.dumps(locked))
    conflicting_handoff_package_version["handoffs"][1]["payload"]["handoff_package_version"] = "0.9"
    checks.append((
        "reject coexisting legacy handoff package version field",
        conflicting_handoff_package_version,
        False,
    ))

    omitted_p4_output_field = json.loads(json.dumps(locked))
    omitted_p4_output_field["stages"]["english-translation"]["output"]["producer_metadata"] = "locked"
    checks.append((
        "reject P4 to P5 source omitting a current output field",
        omitted_p4_output_field,
        False,
    ))

    invalid_inline_ledger = json.loads(json.dumps(locked))
    invalid_inline_ledger["handoffs"][1]["payload"]["locked_claim_boundaries"] = {"inline": ""}
    checks.append(("reject empty inline locked ledger", invalid_inline_ledger, False))

    scalar_locked_ledger = json.loads(json.dumps(locked))
    scalar_locked_ledger["handoffs"][1]["payload"]["locked_numbers_and_units"] = "numbers.md"
    checks.append(("reject scalar locked ledger", scalar_locked_ledger, False))

    extra_ledger_key = json.loads(json.dumps(locked))
    extra_ledger_key["handoffs"][1]["payload"]["terminology_ledger"]["format"] = "tsv"
    checks.append(("reject locked ledger with non-contract key", extra_ledger_key, False))

    invalid_ledger_reference = json.loads(json.dumps(locked))
    invalid_ledger_reference["handoffs"][1]["payload"]["terminology_ledger"]["sha256"] = "latest"
    checks.append(("reject locked ledger reference without SHA-256", invalid_ledger_reference, False))

    wrong_p4_artifact_type = json.loads(json.dumps(locked))
    wrong_p4_artifact_type["stages"]["english-translation"]["output"]["artifact_type"] = "stage-4-output"
    checks.append(("reject non-semantic P4 artifact type", wrong_p4_artifact_type, False))

    missing_p4_artifact_schema = json.loads(json.dumps(locked))
    missing_p4_artifact_schema["stages"]["english-translation"]["output"].pop("artifact_schema_version")
    checks.append(("reject P4 artifact without schema version", missing_p4_artifact_schema, False))

    wrong_p5_artifact_schema = json.loads(json.dumps(locked))
    wrong_p5_artifact_schema["stages"]["pre-submission-check"]["output"]["artifact_schema_version"] = "0.9"
    checks.append(("reject P5 artifact with wrong schema version", wrong_p5_artifact_schema, False))

    wrong_p5_artifact_type = json.loads(json.dumps(locked))
    wrong_p5_artifact_type["stages"]["pre-submission-check"]["output"]["artifact_type"] = "stage-5-output"
    checks.append(("reject non-semantic P5 artifact type", wrong_p5_artifact_type, False))

    missing_p5_handoff_complete = json.loads(json.dumps(locked))
    missing_p5_handoff_complete["handoffs"].pop(2)
    checks.append(("reject complete P5 without P4 to P5 handoff", missing_p5_handoff_complete, False))

    missing_p5_handoff_active = json.loads(json.dumps(locked))
    missing_p5_handoff_active["handoffs"].pop(2)
    missing_p5_handoff_active["stages"]["pre-submission-check"]["status"] = "active"
    missing_p5_handoff_active["stages"]["pre-submission-check"]["output"] = None
    checks.append(("reject active P5 without P4 to P5 handoff", missing_p5_handoff_active, False))

    duplicate_p4_p5_handoff = json.loads(json.dumps(locked))
    copied_p4_p5_handoff = json.loads(json.dumps(duplicate_p4_p5_handoff["handoffs"][2]))
    copied_p4_p5_handoff["handoff_id"] = "h-english-to-preflight-copy"
    duplicate_p4_p5_handoff["handoffs"].append(copied_p4_p5_handoff)
    checks.append((
        "reject duplicate exact P4 to P5 formal handoff with a distinct handoff_id",
        duplicate_p4_p5_handoff,
        False,
    ))

    stale_p4_source = json.loads(json.dumps(locked))
    stale_p4_source["handoffs"][2]["source_artifacts"][0]["sha256"] = "b" * 64
    checks.append(("reject P5 handoff with stale P4 source", stale_p4_source, False))

    wrong_p5_payload_binding = json.loads(json.dumps(locked))
    wrong_p5_payload_binding["handoffs"][2]["payload"]["english_translation_artifact_id"] = "artifact-old"
    checks.append(("reject P5 handoff payload bound to another P4 artifact", wrong_p5_payload_binding, False))

    failures = 0
    file_checks = 0
    with tempfile.TemporaryDirectory(prefix="paperline-self-test-") as tmp:
        for index, (label, state, expected_valid) in enumerate(checks):
            path = Path(tmp) / f"case-{index}.json"
            path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            loaded = load_json_strict(path.read_text(encoding="utf-8"))
            errors = validate_state(loaded)
            observed_valid = not errors
            if observed_valid != expected_valid:
                failures += 1
                print(f"FAIL: {label}: {errors or 'unexpectedly valid'}")
            else:
                print(f"PASS: {label}")
        duplicate_lock_json = json.dumps(locked).replace(
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
        nonfinite_inline_json = json.dumps(locked).replace(
            '"boundaries locked"',
            "Infinity",
            1,
        )
        file_checks += 1
        try:
            load_json_strict(nonfinite_inline_json)
        except ValueError:
            print("PASS: reject nested Infinity in an inline locked ledger")
        else:
            failures += 1
            print("FAIL: reject nested Infinity in an inline locked ledger")
        overflow_inline_json = json.dumps(locked).replace(
            '"locked_numbers_and_units": {"inline": {"status": "locked"}}',
            '"locked_numbers_and_units": {"inline": [1e999]}',
            1,
        )
        file_checks += 1
        try:
            load_json_strict(overflow_inline_json)
        except ValueError:
            print("PASS: reject finite-syntax JSON number that overflows to infinity")
        else:
            failures += 1
            print("FAIL: reject finite-syntax JSON number that overflows to infinity")
        root = Path(tmp)
        artifacts = root / "artifacts"
        artifacts.mkdir(exist_ok=True)
        file_bytes = b"paperline-file-verification-self-test"
        file_digest = hashlib.sha256(file_bytes).hexdigest()
        for name in (
            "stage-1.json",
            "stage-2.json",
            "stage-3.json",
            "stage-4.json",
            "stage-5.json",
            "target-journal-decision.md",
            "target-journal-writing-contract.md",
            "terms.tsv",
        ):
            (artifacts / name).write_bytes(file_bytes)
        file_state = json.loads(json.dumps(locked).replace("a" * 64, file_digest))
        file_state_path = root / "file-state.json"
        file_state_path.write_text(json.dumps(file_state, ensure_ascii=False), encoding="utf-8")
        file_checks += 1
        file_errors = validate_state(file_state) + validate_files(file_state, file_state_path)
        if file_errors:
            failures += 1
            print(f"FAIL: verify matching artifact files: {file_errors}")
        else:
            print("PASS: verify matching artifact files")

        terms_path = artifacts / "terms.tsv"
        terms_path.unlink()
        file_checks += 1
        missing_ledger_errors = validate_files(file_state, file_state_path)
        expected_missing_ledger_error = (
            "handoffs[1].payload.terminology_ledger.path: "
            f"file not found: {terms_path}"
        )
        if missing_ledger_errors != [expected_missing_ledger_error]:
            failures += 1
            print(
                "FAIL: reject missing locked ledger file: "
                f"{missing_ledger_errors or 'unexpectedly valid'}"
            )
        else:
            print("PASS: reject missing locked ledger file")

        terms_path.write_bytes(b"changed-after-ledger-lock")
        file_checks += 1
        changed_ledger_errors = validate_files(file_state, file_state_path)
        expected_changed_ledger_error = (
            "handoffs[1].payload.terminology_ledger.sha256: does not match file bytes"
        )
        if changed_ledger_errors != [expected_changed_ledger_error]:
            failures += 1
            print(
                "FAIL: reject locked ledger changed after handoff: "
                f"{changed_ledger_errors or 'unexpectedly valid'}"
            )
        else:
            print("PASS: reject locked ledger changed after handoff")

        terms_path.write_bytes(file_bytes)
        (artifacts / "stage-3.json").write_bytes(b"changed-after-lock")
        file_checks += 1
        if not validate_files(file_state, file_state_path):
            failures += 1
            print("FAIL: reject file changed after lock: unexpectedly valid")
        else:
            print("PASS: reject file changed after lock")
    if failures:
        print(f"self-test: {failures} failure(s)")
        return 1
    print(f"self-test: {len(checks) + file_checks} checks passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a paperline pipeline-state JSON file.")
    parser.add_argument("state", nargs="?", type=Path, help="path to pipeline-state.json")
    parser.add_argument("--self-test", action="store_true", help="run built-in positive and negative checks")
    parser.add_argument(
        "--verify-files",
        action="store_true",
        help="also read every recorded output/source path and verify its SHA-256",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()
    if args.state is None:
        parser.error("provide a state JSON file or use --self-test")
    try:
        data = load_json_strict(args.state.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.state}", file=sys.stderr)
        return 2
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: cannot read valid UTF-8 JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate_state(data)
    if args.verify_files and not errors:
        errors.extend(validate_files(data, args.state))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"INVALID: {len(errors)} error(s)")
        return 1
    if args.verify_files:
        print(f"VALID_WITH_FILES: {args.state}")
    else:
        print(f"STRUCTURALLY_VALID: {args.state} (rerun with --verify-files before advancing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
