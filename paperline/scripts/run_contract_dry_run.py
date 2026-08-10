#!/usr/bin/env python3
"""Run the source-tree paperline cross-skill contract dry run."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _find_handoff(state: dict, from_stage: str, to_stage: str) -> dict:
    matches = [
        handoff
        for handoff in state.get("handoffs", [])
        if isinstance(handoff, dict)
        and handoff.get("from_stage") == from_stage
        and handoff.get("to_stage") == to_stage
    ]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {from_stage} to {to_stage} handoff")
    return matches[0]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _frontmatter(module: ModuleType, path: Path, label: str) -> dict[str, str]:
    data, errors = module.parse_frontmatter(path.read_text(encoding="utf-8-sig"), label)
    if errors:
        raise RuntimeError(f"cannot parse {label}: {errors}")
    return data


def _bind_real_fixture(
    state: dict,
    journal: ModuleType,
    pipeline: ModuleType,
    root: Path,
) -> tuple[dict, Path, dict[str, Path]]:
    """Bind one pipeline fixture to real, mutually consistent artifact bytes."""
    artifacts = root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    journal_paths = journal.write_valid_fixture(artifacts)
    decision = _frontmatter(journal, journal_paths["decision"], "decision")
    contract = _frontmatter(journal, journal_paths["contract"], "contract")

    output_hashes: dict[str, str] = {}
    for index, stage in enumerate(pipeline.STAGES, start=1):
        path = artifacts / f"stage-{index}.json"
        path.write_text(
            json.dumps({"stage": stage, "fixture": "paperline-semantic-dry-run"}),
            encoding="utf-8",
        )
        output_hashes[stage] = _sha256(path)
        state["stages"][stage]["output"]["sha256"] = output_hashes[stage]

    terms = artifacts / "terms.tsv"
    terms.write_text("中文术语\tEnglish term\tlocked\n", encoding="utf-8")
    terms_hash = _sha256(terms)
    decision_hash = _sha256(journal_paths["decision"])
    contract_hash = _sha256(journal_paths["contract"])

    state["venue"].update({
        "target_journal": decision["target_journal"],
        "article_type": decision["article_type"],
        "decision_path": "artifacts/target-journal-decision.md",
        "decision_schema_version": decision["schema_version"],
        "decision_hash": decision_hash,
        "contract_path": "artifacts/target-journal-writing-contract.md",
        "contract_version": contract["contract_version"],
        "contract_hash": contract_hash,
        "selection_evidence_version": decision["evidence_version"],
        "writing_profile_evidence_id": contract["writing_profile_evidence_id"],
    })

    p3 = state["stages"]["chinese-finalization"]
    binding = p3["content_state"]["author_lock_binding"]
    binding["manuscript_sha256"] = output_hashes["chinese-finalization"]
    binding["contract_version"] = contract["contract_version"]
    binding["contract_sha256"] = contract_hash

    journal_handoff = _find_handoff(state, "journal-contract", "chinese-finalization")
    journal_handoff["source_artifacts"][0].update({
        "path": "artifacts/target-journal-decision.md",
        "version": decision["schema_version"],
        "sha256": decision_hash,
    })
    journal_handoff["source_artifacts"][1].update({
        "path": "artifacts/target-journal-writing-contract.md",
        "version": contract["contract_version"],
        "sha256": contract_hash,
    })

    translation = _find_handoff(state, "chinese-finalization", "english-translation")
    translation["source_artifacts"] = [dict(p3["output"])]
    payload = translation["payload"]
    payload.update({
        "chinese_manuscript_sha256": output_hashes["chinese-finalization"],
        "target_journal": decision["target_journal"],
        "target_journal_article_type": decision["article_type"],
        "target_journal_decision_file": "artifacts/target-journal-decision.md",
        "target_journal_decision_schema_version": decision["schema_version"],
        "target_journal_decision_sha256": decision_hash,
        "target_journal_contract_file": "artifacts/target-journal-writing-contract.md",
        "target_journal_contract_version": contract["contract_version"],
        "target_journal_contract_sha256": contract_hash,
        "target_journal_selection_evidence_version": decision["evidence_version"],
        "target_journal_writing_profile_evidence_id": contract["writing_profile_evidence_id"],
        "terminology_ledger": {"path": "artifacts/terms.tsv", "sha256": terms_hash},
    })
    payload["author_lock_record"]["manuscript_sha256"] = output_hashes["chinese-finalization"]

    p4 = state["stages"]["english-translation"]["output"]
    preflight = _find_handoff(state, "english-translation", "pre-submission-check")
    preflight["source_artifacts"] = [dict(p4)]
    preflight["payload"].update({
        "chinese_manuscript_sha256": output_hashes["chinese-finalization"],
        "english_translation_sha256": output_hashes["english-translation"],
        "target_journal_contract_sha256": contract_hash,
    })

    state_path = root / "pipeline-state.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state, state_path, journal_paths


def main() -> int:
    journal = _load(
        "journal_validator",
        REPO_ROOT / "journal-navigator" / "scripts" / "validate_journal_artifacts.py",
    )
    pipeline = _load(
        "pipeline_validator",
        REPO_ROOT / "paperline" / "scripts" / "validate_pipeline_state.py",
    )
    translator = _load(
        "translation_handoff_validator",
        REPO_ROOT / "zh-en-paper-translator" / "scripts" / "validate_pipeline_handoff.py",
    )

    failures: list[str] = []
    if journal.run_self_test():
        failures.append("journal-navigator artifact self-test failed")
    else:
        print("PASS: journal decision/profile/contract gates")
    if pipeline.run_self_test() != 0:
        failures.append("paperline state self-test failed")
    else:
        print("PASS: paperline state, rollback, and file-binding gates")
    if translator.run_self_test() != 0:
        failures.append("translator handoff self-test failed")
    else:
        print("PASS: translator handoff gates")

    with tempfile.TemporaryDirectory(prefix="paperline-contract-dry-run-") as temp:
        root = Path(temp)
        state, state_path, journal_paths = _bind_real_fixture(
            pipeline._valid_locked_example(), journal, pipeline, root
        )
        state_errors = pipeline.validate_state(state) + pipeline.validate_files(state, state_path)
        if state_errors:
            failures.append(f"real-file locked integration state invalid: {state_errors}")
        else:
            print("PASS: locked pipeline state bound to real artifact bytes")

        translation_handoff = _find_handoff(
            state, "chinese-finalization", "english-translation"
        )
        handoff_errors = translator.validate_handoff(translation_handoff)
        file_errors = translator.verify_files(translation_handoff, root)
        if handoff_errors or file_errors:
            failures.append(
                "paperline P3-to-P4 semantic handoff rejected: "
                f"{handoff_errors + file_errors}"
            )
        else:
            print("PASS: one real decision/contract/manuscript/ledger chain accepted end to end")

        preflight_handoff = _find_handoff(
            state, "english-translation", "pre-submission-check"
        )
        if preflight_handoff["source_artifacts"] != [
            state["stages"]["english-translation"]["output"]
        ]:
            failures.append("P4-to-P5 source is not the exact current P4 output")
        else:
            print("PASS: exact semantic P4-to-P5 handoff")

        no_s7 = json.loads(json.dumps(state))
        _find_handoff(no_s7, "chinese-finalization", "english-translation")[
            "payload"
        ]["chinese_manuscript_status"] = "S6"
        if not pipeline.validate_state(no_s7) or not translator.validate_handoff(
            _find_handoff(no_s7, "chinese-finalization", "english-translation")
        ):
            failures.append("missing-S7 negative case was accepted")
        else:
            print("PASS: missing S7 rejected by producer and consumer")

        changed_journal = json.loads(json.dumps(state))
        changed_journal["venue"]["contract_hash"] = "b" * 64
        if not pipeline.validate_state(changed_journal):
            failures.append("changed-journal negative case was accepted")
        else:
            print("PASS: journal-contract change invalidates old P3/P4 binding")

        stale_preflight = json.loads(json.dumps(state))
        _find_handoff(
            stale_preflight, "english-translation", "pre-submission-check"
        )["source_artifacts"][0]["sha256"] = "b" * 64
        if not pipeline.validate_state(stale_preflight):
            failures.append("stale-P4 P5 handoff negative case was accepted")
        else:
            print("PASS: stale P4 source rejected before P5")

        contract_path = journal_paths["contract"]
        valid_contract = contract_path.read_text(encoding="utf-8")
        contract_path.write_text(
            valid_contract.replace('status: "confirmed"', 'status: "draft"', 1),
            encoding="utf-8",
        )
        bad_semantic = json.loads(json.dumps(translation_handoff))
        bad_semantic["payload"]["target_journal_contract_sha256"] = _sha256(contract_path)
        if not translator.validate_handoff(bad_semantic) and not translator.verify_files(
            bad_semantic, root
        ):
            failures.append("draft journal contract with matching bytes/hash was accepted")
        else:
            print("PASS: matching hash cannot disguise a draft journal contract")
        contract_path.write_text(valid_contract, encoding="utf-8")

        terms_path = root / translation_handoff["payload"]["terminology_ledger"]["path"]
        terms_path.write_text("changed after author lock\n", encoding="utf-8")
        if not translator.verify_files(translation_handoff, root):
            failures.append("changed locked terminology ledger was accepted")
        else:
            print("PASS: changed locked terminology ledger rejected")

    if failures:
        print("FAIL: paperline contract dry run")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS: paperline cross-skill contract dry run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
