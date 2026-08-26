#!/usr/bin/env python3
"""Validate the three scoped geotechnical terminology packs."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "references" / "literature" / "geotechnical-domain-termbases-sources.tsv"
TERM_PATHS = (
    ROOT / "references" / "termbases" / "geotechnical-machine-learning.tsv",
    ROOT / "references" / "termbases" / "geotechnical-analogue-materials.tsv",
    ROOT / "references" / "termbases" / "salt-cavern-construction.tsv",
)
SOURCE_FIELDS = {
    "source_id", "domain", "title", "year", "authors", "venue", "doi", "url",
    "verification_status", "evidence_level", "role",
}
TERM_FIELDS = {
    "zh", "en", "sense_id", "domain", "category", "context", "context_cues",
    "status", "authority", "source", "source_id", "cnki_frequency", "cnki_evidence",
    "selection", "decision_scope", "confirmed_by", "confirmed_at", "forbidden", "notes",
}
ALLOWED_STATUS = {"locked", "verified", "recommended", "context-dependent", "pending", "rejected"}
ALLOWED_AUTHORITY = {"user", "official", "standard", "literature", "corpus", "inferred"}
ALLOWED_CNKI = {"not-collected", "not-applicable"}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)


def read_tsv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = set(reader.fieldnames or [])
        missing = required - fields
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def duplicates(values: list[str]) -> list[str]:
    counts = Counter(value.casefold() for value in values if value)
    return sorted(value for value, count in counts.items() if count > 1)


def valid_cnki_frequency(value: str) -> bool:
    return value in ALLOWED_CNKI or value.isdigit()


def validate() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    sources = read_tsv(SOURCE_PATH, SOURCE_FIELDS)
    source_ids = {row["source_id"] for row in sources}

    duplicate_ids = duplicates([row["source_id"] for row in sources])
    if duplicate_ids:
        errors.append(f"duplicate source_id values: {duplicate_ids}")
    duplicate_dois = duplicates([row["doi"] for row in sources])
    if duplicate_dois:
        errors.append(f"duplicate DOI values: {duplicate_dois}")
    for line, row in enumerate(sources, start=2):
        if not row["source_id"] or not row["domain"] or not row["title"] or not row["url"]:
            errors.append(f"source row {line}: source_id, domain, title, and url are required")
        if row["doi"] and not DOI_RE.match(row["doi"]):
            errors.append(f"source row {line}: malformed DOI {row['doi']!r}")

    for path in TERM_PATHS:
        rows = read_tsv(path, TERM_FIELDS)
        counts[path.name] = len(rows)
        if len(rows) < 50:
            errors.append(f"{path.name}: unexpectedly small termbase ({len(rows)} rows)")
        sense_keys = [f"{row['zh']}\0{row['sense_id']}" for row in rows]
        duplicate_senses = duplicates(sense_keys)
        if duplicate_senses:
            errors.append(f"{path.name}: duplicate zh/sense_id pairs: {duplicate_senses}")
        zh_counts = Counter(row["zh"] for row in rows if row["zh"])

        for line, row in enumerate(rows, start=2):
            if not all(row[field] for field in ("zh", "en", "sense_id", "domain", "category", "context", "status", "authority")):
                errors.append(f"{path.name} row {line}: core term and sense fields are required")
            if row["status"] not in ALLOWED_STATUS:
                errors.append(f"{path.name} row {line}: invalid status {row['status']!r}")
            if row["authority"] not in ALLOWED_AUTHORITY:
                errors.append(f"{path.name} row {line}: invalid authority {row['authority']!r}")
            if row["status"] == "verified" and row["authority"] in {"corpus", "inferred"}:
                errors.append(f"{path.name} row {line}: verified term cannot rely only on {row['authority']}")
            if row["status"] == "locked" and row["authority"] not in {"user", "official"}:
                errors.append(f"{path.name} row {line}: locked term must be user or official authority")
            if not valid_cnki_frequency(row["cnki_frequency"]):
                errors.append(f"{path.name} row {line}: invalid cnki_frequency {row['cnki_frequency']!r}")
            if row["cnki_frequency"] == "not-collected" and not row["cnki_evidence"]:
                errors.append(f"{path.name} row {line}: not-collected CNKI frequency needs a reason")
            if zh_counts[row["zh"]] > 1 and (not row["sense_id"] or not row["context"]):
                errors.append(f"{path.name} row {line}: repeated zh requires sense_id and context")
            for source_id in (item.strip() for item in row["source_id"].split("|") if item.strip()):
                if source_id not in source_ids:
                    errors.append(f"{path.name} row {line}: unknown source_id {source_id!r}")
            if row["status"] in {"locked", "verified", "recommended", "context-dependent"} and not row["source_id"]:
                errors.append(f"{path.name} row {line}: sourced status lacks source_id")
    counts[SOURCE_PATH.name] = len(sources)
    return errors, counts


def main() -> int:
    try:
        errors, counts = validate()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    summary = ", ".join(f"{name}={count}" for name, count in sorted(counts.items()))
    print(f"PASS: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
