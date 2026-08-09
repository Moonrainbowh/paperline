#!/usr/bin/env python3
"""Inventory and compare Markdown, DOCX, PDF, and LaTeX manuscript structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
FORMAT_BY_SUFFIX = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".docx": "docx",
    ".pdf": "pdf",
    ".tex": "latex",
    ".latex": "latex",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str


@dataclass
class Inventory:
    path: str
    format: str
    counts: dict[str, int]
    notes: list[str]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def count_cjk(text: str) -> int:
    return len(CJK_RE.findall(text))


def strip_markdown_code(text: str) -> str:
    return re.sub(r"(?ms)^(```|~~~).*?^\1\s*$", "", text)


def inventory_markdown(path: Path) -> Inventory:
    raw = read_text(path)
    text = strip_markdown_code(raw)
    table_separators = re.findall(r"(?m)^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$", text)
    display_math = len(re.findall(r"(?s)(?<!\\)\$\$.*?(?<!\\)\$\$", text))
    display_math += len(re.findall(r"(?s)\\\[.*?\\\]", text))
    inline_math = len(re.findall(r"(?s)(?<![\\$])\$(?!\$).*?(?<![\\$])\$(?!\$)", text))
    paragraphs = [block for block in re.split(r"\r?\n\s*\r?\n", text) if block.strip()]
    counts = {
        "headings": len(re.findall(r"(?m)^#{1,6}\s+\S", text)),
        "paragraphs": len(paragraphs),
        "tables": len(table_separators),
        "formulas": display_math + inline_math,
        "images": len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text)),
        "links": len(re.findall(r"(?<!!)\[[^\]]+\]\([^)]+\)", text)),
        "footnotes": len(re.findall(r"(?m)^\[\^[^\]]+\]:", text)),
        "cjk_chars": count_cjk(text),
    }
    return Inventory(str(path), "markdown", counts, [])


def strip_latex_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def inventory_latex(path: Path) -> Inventory:
    raw = read_text(path)
    text = strip_latex_comments(raw)
    equation_envs = len(re.findall(r"\\begin\{(?:equation|align|alignat|gather|multline|eqnarray|displaymath)\*?\}", text))
    display_math = len(re.findall(r"(?s)\\\[.*?\\\]", text)) + len(re.findall(r"(?s)(?<!\\)\$\$.*?(?<!\\)\$\$", text))
    paragraphs = [block for block in re.split(r"\r?\n\s*\r?\n", text) if block.strip()]
    counts = {
        "headings": len(re.findall(r"\\(?:part|chapter|section|subsection|subsubsection|paragraph|subparagraph)\*?\s*\{", text)),
        "paragraphs": len(paragraphs),
        "tables": len(re.findall(r"\\begin\{(?:tabular\*?|longtable|tabularx)\}", text)),
        "formulas": equation_envs + display_math,
        "images": len(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\s*\{", text)),
        "labels": len(re.findall(r"\\label\s*\{", text)),
        "references": len(re.findall(r"\\(?:ref|pageref|eqref|autoref|cref|Cref)\s*\{", text)),
        "citations": len(re.findall(r"\\cite\w*\s*(?:\[[^\]]*\]\s*)*\{", text)),
        "cjk_chars": count_cjk(text),
    }
    return Inventory(str(path), "latex", counts, [])


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W = f"{{{W_NS}}}"
M = f"{{{M_NS}}}"


def docx_xml_parts(names: list[str]) -> list[str]:
    selected: list[str] = []
    for name in names:
        if name == "word/document.xml":
            selected.append(name)
        elif re.fullmatch(r"word/(?:header|footer)\d+\.xml", name):
            selected.append(name)
        elif name in {"word/footnotes.xml", "word/endnotes.xml", "word/comments.xml"}:
            selected.append(name)
    return selected


def inventory_docx(path: Path) -> Inventory:
    counts = {
        "paragraphs": 0,
        "tables": 0,
        "formulas": 0,
        "images": 0,
        "sections": 0,
        "headers": 0,
        "footers": 0,
        "footnotes": 0,
        "endnotes": 0,
        "text_boxes": 0,
        "hyperlinks": 0,
        "fields": 0,
        "comments": 0,
        "tracked_insertions": 0,
        "tracked_deletions": 0,
        "cjk_chars": 0,
    }
    notes: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            counts["images"] = sum(name.startswith("word/media/") and not name.endswith("/") for name in names)
            counts["headers"] = sum(bool(re.fullmatch(r"word/header\d+\.xml", name)) for name in names)
            counts["footers"] = sum(bool(re.fullmatch(r"word/footer\d+\.xml", name)) for name in names)
            counts["footnotes"] = int("word/footnotes.xml" in names)
            counts["endnotes"] = int("word/endnotes.xml" in names)
            for part in docx_xml_parts(names):
                root = ET.fromstring(archive.read(part))
                counts["paragraphs"] += sum(1 for _ in root.iter(W + "p"))
                counts["tables"] += sum(1 for _ in root.iter(W + "tbl"))
                counts["formulas"] += sum(1 for _ in root.iter(M + "oMath"))
                counts["sections"] += sum(1 for _ in root.iter(W + "sectPr"))
                counts["text_boxes"] += sum(1 for _ in root.iter(W + "txbxContent"))
                counts["hyperlinks"] += sum(1 for _ in root.iter(W + "hyperlink"))
                counts["fields"] += sum(1 for _ in root.iter(W + "fldSimple"))
                counts["fields"] += sum(1 for _ in root.iter(W + "instrText"))
                counts["comments"] += sum(1 for _ in root.iter(W + "comment"))
                counts["tracked_insertions"] += sum(1 for _ in root.iter(W + "ins"))
                counts["tracked_deletions"] += sum(1 for _ in root.iter(W + "del"))
                visible = "".join(node.text or "" for node in root.iter(W + "t"))
                counts["cjk_chars"] += count_cjk(visible)
    except (OSError, zipfile.BadZipFile, ET.ParseError) as exc:
        raise ValueError(f"Cannot inventory DOCX: {exc}") from exc
    if counts["tracked_insertions"] or counts["tracked_deletions"]:
        notes.append("Tracked changes are present; determine the authoritative visible text before translation.")
    if counts["comments"]:
        notes.append("Comments are present; do not treat comment text as manuscript prose without a decision.")
    return Inventory(str(path), "docx", counts, notes)


def inventory_pdf(path: Path) -> Inventory:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF inventory requires pypdf; use the bundled workspace Python runtime") from exc
    try:
        reader = PdfReader(str(path))
        page_texts: list[str] = []
        images = 0
        for page in reader.pages:
            page_texts.append(page.extract_text() or "")
            try:
                images += len(page.images)
            except Exception:
                pass
    except Exception as exc:
        raise ValueError(f"Cannot inventory PDF: {exc}") from exc
    joined = "\n".join(page_texts)
    low_text_pages = sum(len(text.strip()) < 40 for text in page_texts)
    notes = ["PDF formula and table counts are not reliably recoverable from the text layer; render and inspect every page."]
    if page_texts and low_text_pages:
        notes.append(f"{low_text_pages} of {len(page_texts)} page(s) have little extractable text; OCR or hybrid handling may be required.")
    counts = {
        "pages": len(reader.pages),
        "text_chars": len(joined),
        "low_text_pages": low_text_pages,
        "images": images,
        "cjk_chars": count_cjk(joined),
    }
    return Inventory(str(path), "pdf", counts, notes)


def detect_format(path: Path) -> str:
    try:
        return FORMAT_BY_SUFFIX[path.suffix.lower()]
    except KeyError as exc:
        raise ValueError(f"Unsupported format '{path.suffix}'; expected .md, .docx, .pdf, or .tex") from exc


def inventory(path: Path) -> Inventory:
    kind = detect_format(path)
    if kind == "markdown":
        return inventory_markdown(path)
    if kind == "latex":
        return inventory_latex(path)
    if kind == "docx":
        return inventory_docx(path)
    return inventory_pdf(path)


COMPARE_KEYS = {
    "markdown": ("headings", "paragraphs", "tables", "formulas", "images", "links", "footnotes"),
    "latex": ("headings", "paragraphs", "tables", "formulas", "images", "labels", "references", "citations"),
    "docx": ("paragraphs", "tables", "formulas", "images", "sections", "headers", "footers", "footnotes", "endnotes", "text_boxes", "hyperlinks", "fields"),
}


def compare(source: Inventory, translation: Inventory) -> list[Finding]:
    if source.format != translation.format:
        return [Finding("error", "FORMAT_MISMATCH", f"Cannot compare {source.format} directly with {translation.format}; inventory cross-format PDF/DOCX artifacts separately")]
    findings: list[Finding] = []
    if source.format == "pdf":
        if source.counts["pages"] != translation.counts["pages"]:
            findings.append(Finding("warning", "PDF_PAGE_REFLOW", f"Page count changed from {source.counts['pages']} to {translation.counts['pages']}; verify that reflow is intentional"))
        findings.append(Finding("warning", "PDF_VISUAL_REVIEW_REQUIRED", "PDF structure cannot prove layout or equation/table fidelity; render and inspect every page"))
    else:
        for key in COMPARE_KEYS[source.format]:
            before = source.counts.get(key, 0)
            after = translation.counts.get(key, 0)
            if before != after:
                findings.append(Finding("error", "STRUCTURE_MISMATCH", f"{key} changed from {before} to {after}"))
    if translation.counts.get("cjk_chars", 0):
        findings.append(Finding("warning", "CJK_REMAINS", f"Output text layer contains {translation.counts['cjk_chars']} CJK character(s); confirm they are intentionally preserved"))
    return findings


def write_minimal_docx(path: Path, chinese: bool, include_formula: bool = True) -> None:
    text = "结果" if chinese else "Results"
    formula = f'<m:oMath><m:r><m:t>x</m:t></m:r></m:oMath>' if include_formula else ""
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:m="{M_NS}"><w:body>'
        f'<w:p><w:r><w:t>{text}</w:t></w:r></w:p>'
        '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>1</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
        f'{formula}<w:sectPr/></w:body></w:document>'
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", xml)
        archive.writestr("word/media/image1.png", b"fixture")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        md_zh = root / "paper-zh.md"
        md_en = root / "paper-en.md"
        md_bad = root / "paper-bad.md"
        md_zh.write_text("# 结果\n\n| 指标 | 值 |\n| --- | --- |\n| R | 1 |\n\n$$x=1$$\n\n![图](a.png)\n", encoding="utf-8")
        md_en.write_text("# Results\n\n| Metric | Value |\n| --- | --- |\n| R | 1 |\n\n$$x=1$$\n\n![Figure](a.png)\n", encoding="utf-8")
        md_bad.write_text("# Results\n\nThe result was 1.\n", encoding="utf-8")
        if compare(inventory(md_zh), inventory(md_en)):
            print("SELF-TEST FAIL: valid Markdown comparison produced findings", file=sys.stderr)
            return 1
        if not any(item.code == "STRUCTURE_MISMATCH" for item in compare(inventory(md_zh), inventory(md_bad))):
            print("SELF-TEST FAIL: invalid Markdown structure was not detected", file=sys.stderr)
            return 1

        tex_zh = root / "paper-zh.tex"
        tex_en = root / "paper-en.tex"
        tex = "\\section{{{}}}\n\\begin{{tabular}}{{cc}}A&B\\\\\\end{{tabular}}\n\\begin{{equation}}x=1\\label{{eq:x}}\\end{{equation}}\n\\ref{{eq:x}}\\cite{{key}}"
        tex_zh.write_text(tex.format("结果"), encoding="utf-8")
        tex_en.write_text(tex.format("Results"), encoding="utf-8")
        if compare(inventory(tex_zh), inventory(tex_en)):
            print("SELF-TEST FAIL: valid LaTeX comparison produced findings", file=sys.stderr)
            return 1

        docx_zh = root / "paper-zh.docx"
        docx_en = root / "paper-en.docx"
        docx_bad = root / "paper-bad.docx"
        write_minimal_docx(docx_zh, chinese=True)
        write_minimal_docx(docx_en, chinese=False)
        write_minimal_docx(docx_bad, chinese=False, include_formula=False)
        if compare(inventory(docx_zh), inventory(docx_en)):
            print("SELF-TEST FAIL: valid DOCX comparison produced findings", file=sys.stderr)
            return 1
        if not any(item.code == "STRUCTURE_MISMATCH" for item in compare(inventory(docx_zh), inventory(docx_bad))):
            print("SELF-TEST FAIL: missing DOCX formula was not detected", file=sys.stderr)
            return 1
        try:
            from pypdf import PdfWriter
        except ImportError:
            pass
        else:
            pdf_path = root / "scan.pdf"
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            with pdf_path.open("wb") as stream:
                writer.write(stream)
            pdf_inventory = inventory(pdf_path)
            if pdf_inventory.counts["pages"] != 1 or pdf_inventory.counts["low_text_pages"] != 1:
                print("SELF-TEST FAIL: PDF low-text/OCR detection", file=sys.stderr)
                return 1
    print("SELF-TEST PASS")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Inventory one .md, .docx, .pdf, or .tex file")
    parser.add_argument("--source", type=Path, help="Source file for same-format comparison")
    parser.add_argument("--translation", type=Path, help="Translated file for same-format comparison")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON")
    parser.add_argument("--strict", action="store_true", help="Return nonzero for warnings as well as errors")
    parser.add_argument("--self-test", action="store_true", help="Run built-in Markdown, LaTeX, and DOCX tests")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.self_test:
        return run_self_test()
    try:
        if args.input and not args.source and not args.translation:
            result = inventory(args.input)
            print(json.dumps(asdict(result), ensure_ascii=False, indent=2) if args.as_json else result)
            return 0
        if args.source and args.translation and not args.input:
            source = inventory(args.source)
            translation = inventory(args.translation)
            findings = compare(source, translation)
            if args.as_json:
                print(json.dumps({"source": asdict(source), "translation": asdict(translation), "findings": [asdict(item) for item in findings]}, ensure_ascii=False, indent=2))
            elif findings:
                for item in findings:
                    print(f"[{item.severity.upper()}] {item.code}: {item.message}")
            else:
                print("PASS: protected document structure is unchanged")
            has_error = any(item.severity == "error" for item in findings)
            has_warning = any(item.severity == "warning" for item in findings)
            return 1 if has_error or (args.strict and has_warning) else 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"audit error: {exc}", file=sys.stderr)
        return 2
    raise SystemExit("Use --input FILE, --source FILE --translation FILE, or --self-test")


if __name__ == "__main__":
    raise SystemExit(main())
