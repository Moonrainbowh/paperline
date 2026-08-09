#!/usr/bin/env python3
"""Validate the bundled literature catalogue and bilingual termbase."""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "references" / "literature" / "salt-cavern-geotech-ai-sources.tsv"
TERM_PATH = ROOT / "references" / "termbases" / "salt-cavern-geotech-ai.tsv"
SOURCE_FIELDS = {
    "source_id", "theme", "title", "year", "authors", "venue", "doi", "url",
    "verification_status", "evidence_level", "role",
}
TERM_FIELDS = {
    "zh", "en", "status", "authority", "source", "forbidden", "notes",
    "source_id", "category",
}
ALLOWED_STATUS = {"locked", "verified", "pending", "rejected"}
ALLOWED_AUTHORITY = {"user", "official", "standard", "literature", "inferred"}
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


def validate() -> list[str]:
    errors: list[str] = []
    sources = read_tsv(SOURCE_PATH, SOURCE_FIELDS)
    terms = read_tsv(TERM_PATH, TERM_FIELDS)

    source_ids = {row["source_id"] for row in sources}
    duplicate_ids = duplicates([row["source_id"] for row in sources])
    if duplicate_ids:
        errors.append(f"duplicate source_id values: {duplicate_ids}")

    duplicate_dois = duplicates([row["doi"] for row in sources])
    if duplicate_dois:
        errors.append(f"duplicate DOI values: {duplicate_dois}")

    for line, row in enumerate(sources, start=2):
        if not row["source_id"] or not row["title"] or not row["url"]:
            errors.append(f"source row {line}: source_id, title, and url are required")
        if row["doi"] and not DOI_RE.match(row["doi"]):
            errors.append(f"source row {line}: malformed DOI {row['doi']!r}")
        if row["doi"] and row["url"].casefold() != f"https://doi.org/{row['doi']}".casefold() and row["source_id"].startswith(("SC", "AI")):
            errors.append(f"source row {line}: article URL does not resolve through its DOI")

    duplicate_terms = duplicates([row["zh"] for row in terms])
    if duplicate_terms:
        errors.append(f"duplicate Chinese terms without context scoping: {duplicate_terms}")

    for line, row in enumerate(terms, start=2):
        if not row["zh"] or not row["en"]:
            errors.append(f"term row {line}: zh and en are required")
        if row["status"] not in ALLOWED_STATUS:
            errors.append(f"term row {line}: invalid status {row['status']!r}")
        if row["authority"] not in ALLOWED_AUTHORITY:
            errors.append(f"term row {line}: invalid authority {row['authority']!r}")
        if row["status"] == "pending" and row["authority"] != "inferred":
            errors.append(f"term row {line}: pending terms must use inferred authority")
        if row["status"] in {"locked", "verified"} and not row["source"]:
            errors.append(f"term row {line}: {row['status']} term lacks a source")
        for source_id in (part.strip() for part in row["source_id"].split("|") if part.strip()):
            if source_id not in source_ids:
                errors.append(f"term row {line}: unknown source_id {source_id!r}")

    if len(sources) < 30:
        errors.append(f"source catalogue unexpectedly small: {len(sources)} rows")
    if len(terms) < 100:
        errors.append(f"termbase unexpectedly small: {len(terms)} rows")
    return errors


def main() -> int:
    try:
        errors = validate()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    source_count = len(read_tsv(SOURCE_PATH, SOURCE_FIELDS))
    term_count = len(read_tsv(TERM_PATH, TERM_FIELDS))
    print(f"PASS: {source_count} sources and {term_count} terms validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
