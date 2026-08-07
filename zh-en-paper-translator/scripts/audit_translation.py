#!/usr/bin/env python3
"""Audit deterministic invariants in a Chinese-to-English paper translation."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+−]?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?%?")
CITATION_RE = re.compile(r"\[(?:\d+(?:\s*[-,–]\s*\d+)*)\]")
DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]*[A-Za-z0-9]", re.IGNORECASE)
URL_RE = re.compile(r"https?://[^\s<>\]\[()]+", re.IGNORECASE)
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def normalized_numbers(text: str) -> Counter[str]:
    return Counter(match.group(0).replace("−", "-") for match in NUMBER_RE.finditer(text))


def exact_tokens(text: str, pattern: re.Pattern[str]) -> Counter[str]:
    return Counter(match.group(0) for match in pattern.finditer(text))


def compare_counter(label: str, source: Counter[str], target: Counter[str], code: str) -> list[Finding]:
    findings: list[Finding] = []
    missing = source - target
    added = target - source
    if missing:
        findings.append(Finding("error", code, f"Missing {label}: {dict(missing)}"))
    if added:
        findings.append(Finding("error", code, f"Added {label}: {dict(added)}"))
    return findings


def load_termbase(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = set(reader.fieldnames or [])
        if not {"zh", "en"}.issubset(fields):
            raise ValueError("Termbase must contain tab-separated 'zh' and 'en' columns")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def audit_terms(source: str, translation: str, rows: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    translation_folded = translation.casefold()
    for index, row in enumerate(rows, start=2):
        zh = row.get("zh", "")
        en = row.get("en", "")
        status = row.get("status", "locked").casefold() or "locked"
        if not zh or zh not in source or status in {"pending", "rejected"}:
            continue
        if en and en.casefold() not in translation_folded:
            findings.append(Finding("error", "TERM_MISSING", f"Row {index}: source contains '{zh}' but translation lacks approved term '{en}'"))
        forbidden = [item.strip() for item in row.get("forbidden", "").split("|") if item.strip()]
        for item in forbidden:
            if item.casefold() in translation_folded:
                findings.append(Finding("error", "TERM_FORBIDDEN", f"Row {index}: forbidden term '{item}' appears for '{zh}'"))
    return findings


def audit(source: str, translation: str, termbase: list[dict[str, str]]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(compare_counter("numeric tokens", normalized_numbers(source), normalized_numbers(translation), "NUMBER_MISMATCH"))
    findings.extend(compare_counter("citation markers", exact_tokens(source, CITATION_RE), exact_tokens(translation, CITATION_RE), "CITATION_MISMATCH"))
    findings.extend(compare_counter("DOIs", exact_tokens(source, DOI_RE), exact_tokens(translation, DOI_RE), "DOI_MISMATCH"))
    findings.extend(compare_counter("URLs", exact_tokens(source, URL_RE), exact_tokens(translation, URL_RE), "URL_MISMATCH"))
    findings.extend(audit_terms(source, translation, termbase))
    cjk_count = len(CJK_RE.findall(translation))
    if cjk_count:
        findings.append(Finding("warning", "CJK_REMAINS", f"Translation contains {cjk_count} CJK character(s); review whether they are intentional"))
    if not translation.strip():
        findings.append(Finding("error", "EMPTY_TRANSLATION", "Translation is empty"))
    return findings


def run_self_test() -> int:
    source = "在3个样本中，储气库模型提高了12.5% [1]，详见10.1000/test.1。"
    good = "Across 3 samples, the gas-storage model improved by 12.5% [1]; see 10.1000/test.1."
    bad = "Across 4 samples, the cavern model improved by 15% [2]."
    rows = [{"zh": "储气库模型", "en": "gas-storage model", "status": "locked", "forbidden": "cavern model"}]
    good_findings = audit(source, good, rows)
    if good_findings:
        print(f"SELF-TEST FAIL: valid translation produced findings: {good_findings}", file=sys.stderr)
        return 1
    bad_findings = audit(source, bad, rows)
    expected = {"NUMBER_MISMATCH", "CITATION_MISMATCH", "DOI_MISMATCH", "TERM_MISSING", "TERM_FORBIDDEN"}
    observed = {finding.code for finding in bad_findings}
    if not expected.issubset(observed):
        print(f"SELF-TEST FAIL: expected {sorted(expected)}, observed {sorted(observed)}", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        termbase_path = Path(tmp) / "terms.tsv"
        termbase_path.write_text("zh\ten\tstatus\n储气库模型\tgas-storage model\tlocked\n", encoding="utf-8")
        if load_termbase(termbase_path)[0]["en"] != "gas-storage model":
            print("SELF-TEST FAIL: termbase parsing", file=sys.stderr)
            return 1
    print("SELF-TEST PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="UTF-8 Chinese source text")
    parser.add_argument("--translation", type=Path, help="UTF-8 English translation")
    parser.add_argument("--termbase", type=Path, help="Optional UTF-8 TSV terminology ledger")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON findings")
    parser.add_argument("--strict", action="store_true", help="Return nonzero for warnings as well as errors")
    parser.add_argument("--self-test", action="store_true", help="Run built-in tests and exit")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test()
    if args.source is None or args.translation is None:
        raise SystemExit("--source and --translation are required unless --self-test is used")
    try:
        findings = audit(read_text(args.source), read_text(args.translation), load_termbase(args.termbase))
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"[{item.severity.upper()}] {item.code}: {item.message}")
    else:
        print("PASS: no deterministic mismatches found")
    has_error = any(item.severity == "error" for item in findings)
    has_warning = any(item.severity == "warning" for item in findings)
    return 1 if has_error or (args.strict and has_warning) else 0


if __name__ == "__main__":
    raise SystemExit(main())
