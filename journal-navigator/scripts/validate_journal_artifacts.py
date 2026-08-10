#!/usr/bin/env python3
"""校验期刊决策与双轨写作契约；仅使用 Python 标准库。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
import unicodedata
from datetime import date
from pathlib import Path


DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
CANDIDATE_ID_RE = re.compile(r"CAND-\d{3}\Z")
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>|\b(?:TODO|TBD)\b|draft\s*\|", re.IGNORECASE)
CANONICAL_FIELD_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*?)[ \t]*\Z")
FENCED_BLOCK_RE = re.compile(r"(?m)^[ \t]*(?:```|~~~)")
RAW_HTML_BLOCK_RE = re.compile(r"(?m)^[ \t]*<")
ATX_HEADING_RE = re.compile(r" {0,3}(#{1,6})(?:[ \t]+(.*?))?[ \t]*\Z")
LINK_REFERENCE_DEFINITION_RE = re.compile(r"(?m)^ {0,3}\[[^\]\r\n]+\]:")
SETEXT_OR_THEMATIC_RE = re.compile(r"(?m)^ {0,3}(?:=+|-+)[ \t]*$")
CANONICAL_BARE_LITERALS = {
    "requires_recheck_before_submission": frozenset({"true"}),
    "status": frozenset({"confirmed"}),
    "contract_status": frozenset({"confirmed"}),
    "author_confirmation": frozenset({"confirmed"}),
}

DECISION_FIELDS = (
    "artifact_type", "schema_version", "status", "manuscript_id",
    "manuscript_revision", "target_journal", "article_type",
    "section_or_collection", "evidence_version", "last_verified_at",
    "author_confirmed_at", "selected_candidate_id",
    "selection_evidence_file", "selection_evidence_sha256", "blocking_issues",
)

EVIDENCE_FIELDS = (
    "artifact_type", "schema_version", "evidence_version", "manuscript_id",
    "manuscript_revision", "generated_at", "last_verified_at",
    "shortlist_candidate_ids", "unknown_hard_gate_candidates",
    "failed_hard_gate_candidates",
)

CONTRACT_FIELDS = (
    "artifact_type", "contract_version", "contract_id", "status",
    "manuscript_id", "manuscript_revision", "target_journal", "article_type",
    "section_or_collection", "research_field", "generated_at",
    "last_verified_at", "author_confirmed_at", "selection_evidence_version",
    "writing_profile_evidence_id", "decision_file", "decision_sha256",
    "journal_profile_file", "journal_profile_sha256",
    "field_blueprint_file", "field_blueprint_sha256",
    "requires_recheck_before_submission", "blocking_issues",
)

DECISION_HEADINGS = (
    "## 1. 选定期刊与论文类型",
    "## 2. 硬门结论",
    "## 3. 软偏好与取舍",
    "## 4. 作者确认",
    "## 5. 写作画像交接块",
)

EVIDENCE_HEADINGS = (
    "## 1. 研究快照与作者约束",
    "## 2. 证据来源与核验日期",
    "## 3. 硬门结果",
    "## 4. 软偏好、权重与评分理由",
    "## 5. 淘汰与待核验候选",
    "## 6. 短名单及取舍",
    "## 7. 推荐次序与适用条件",
)

CONTRACT_HEADINGS = (
    "## 1. 目标定义与选择依据",
    "## 2. 双轨来源与可信度摘要",
    "## 3. 编辑侧重点与贡献排序",
    "## 4. 全文架构与篇幅预算",
    "## 5. 章节写作合同",
    "## 6. 图表与补充材料合同",
    "## 7. 语言、术语与语气",
    "## 8. 证据门槛",
    "## 9. 禁止事项",
    "## 10. 融合决策与冲突裁决",
    "## 11. 作者确认",
    "## 12. Paper Navigator 交接块",
)

JOURNAL_PROFILE_HEADINGS = (
    "## 1. 目标期刊与论文类型",
    "## 2. 官方规则与编辑范围",
    "## 3. A/C 样本选择和评分摘要",
    "## 4. 期刊结构、表达与边界",
    "## 5. 章节用途矩阵",
    "## 6. 期刊轨道规则清单",
)

FIELD_PROFILE_HEADINGS = (
    "## 1. 当前论文研究画像",
    "## 2. A/B 样本选择和评分摘要",
    "## 3. 领域论证链与方法子群",
    "## 4. 章节用途矩阵",
    "## 5. 领域轨道规则清单",
)


def read_text(path: Path, label: str) -> tuple[str, list[str]]:
    if not path.is_file():
        return "", [f"{label}不存在: {path}"]
    try:
        return path.read_text(encoding="utf-8-sig"), []
    except UnicodeError as exc:
        return "", [f"{label}不是有效 UTF-8: {exc}"]


def parse_canonical_scalar(
    raw: str,
    label: str,
    field_name: str,
    allow_json_container: bool = False,
) -> tuple[str, list[str]]:
    value = raw.strip()
    if not value:
        return "", []
    starts_quoted = value[0] in {"\"", "'"}
    ends_quoted = value[-1] in {"\"", "'"}
    if starts_quoted or ends_quoted:
        if not (starts_quoted and ends_quoted and value[0] == value[-1] and len(value) >= 2):
            return "", [f"{label} 引号必须同种、成对闭合"]
        quote = value[0]
        inner = value[1:-1]
        if "\\" in inner:
            return "", [f"{label} 的规范引号标量不得包含反斜线转义"]
        if quote in inner:
            return "", [f"{label} 不支持带内部同类引号的标量；请改用另一种成对引号"]
        return inner, []
    if value.startswith(("[", "{")):
        if not allow_json_container:
            return "", [f"{label} 不允许数组或对象值"]
        try:
            json.loads(
                value,
                object_pairs_hook=_reject_duplicate_json_pairs,
                parse_float=_parse_finite_json_float,
                parse_constant=lambda constant: (_ for _ in ()).throw(
                    ValueError(f"non-standard JSON constant: {constant}")
                ),
            )
        except (json.JSONDecodeError, ValueError):
            return "", [f"{label} 的行内数组或对象必须是严格 JSON"]
        return value, []
    if value in CANONICAL_BARE_LITERALS.get(field_name, frozenset()):
        return value, []
    return "", [
        f"{label} 的裸标量不在该字段允许的机器字面量中；"
        "自由文本、路径、日期、版本、数字及 YAML 隐式类型值必须使用同种成对引号"
    ]


def _reject_duplicate_json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_finite_json_float(raw: str) -> float:
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number: {raw}")
    return value


def split_formal_document(text: str, label: str) -> tuple[str, str, list[str]]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return "", "", [f"{label}缺少独占首行的 YAML 头部起始分隔符 ---"]
    closing_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            closing_index = index
            break
    if closing_index is None:
        return "", "", [f"{label} YAML 头部缺少独占行的闭合分隔符 ---"]
    return "".join(lines[1:closing_index]), "".join(lines[closing_index + 1:]), []


def parse_frontmatter(text: str, label: str) -> tuple[dict[str, str], list[str]]:
    frontmatter, _, split_errors = split_formal_document(text, label)
    if split_errors:
        return {}, split_errors
    data: dict[str, str] = {}
    errors: list[str] = []
    for line_number, line in enumerate(frontmatter.splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = CANONICAL_FIELD_RE.fullmatch(line)
        if match is None:
            errors.append(
                f"{label} YAML 头部第 {line_number} 行不符合规范字段格式 key: value"
            )
            continue
        key, raw_value = match.groups()
        value, scalar_errors = parse_canonical_scalar(
            raw_value,
            f"{label} YAML 头部字段 {key}",
            key,
            key in {
                "shortlist_candidate_ids",
                "unknown_hard_gate_candidates",
                "failed_hard_gate_candidates",
                "blocking_issues",
            },
        )
        errors.extend(scalar_errors)
        if scalar_errors:
            continue
        if key in data:
            errors.append(f"{label} YAML 头部字段重复: {key}")
            continue
        data[key] = value
    return data, errors


def require_fields(data: dict[str, str], fields: tuple[str, ...], label: str) -> list[str]:
    return [f"{label} YAML 缺少字段或值为空: {key}" for key in fields if not data.get(key, "").strip()]


def require_values(data: dict[str, str], expected: dict[str, str], label: str) -> list[str]:
    errors: list[str] = []
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"{label} {key} 必须是 {value}")
    return errors


def require_dates(data: dict[str, str], keys: tuple[str, ...], label: str) -> list[str]:
    errors: list[str] = []
    for key in keys:
        value = data.get(key, "")
        if not value:
            continue
        if not DATE_RE.fullmatch(value):
            errors.append(f"{label} {key} 必须使用 YYYY-MM-DD")
            continue
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            errors.append(f"{label} {key} 必须是真实存在的日历日期")
            continue
        if parsed > date.today():
            errors.append(f"{label} {key} 不得晚于校验当天")
    return errors


def date_value(data: dict[str, str], key: str) -> date | None:
    value = data.get(key, "")
    if not DATE_RE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def require_date_order(
    data: dict[str, str], ordered_keys: tuple[str, ...], label: str
) -> list[str]:
    errors: list[str] = []
    for earlier_key, later_key in zip(ordered_keys, ordered_keys[1:]):
        earlier = date_value(data, earlier_key)
        later = date_value(data, later_key)
        if earlier is not None and later is not None and earlier > later:
            errors.append(
                f"{label} 日期顺序必须满足 {earlier_key} <= {later_key}"
            )
    return errors


def require_sections(text: str, headings: tuple[str, ...], label: str) -> list[str]:
    _, body, split_errors = split_formal_document(text, label)
    if split_errors:
        return []
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    errors: list[str] = []
    expected_by_content = {heading[3:]: heading for heading in headings}
    for line in body.splitlines():
        heading_match = ATX_HEADING_RE.fullmatch(line)
        if heading_match is None or heading_match.group(1) != "##":
            continue
        content = heading_match.group(2) or ""
        content = re.sub(r"[ \t]+#+[ \t]*\Z", "", content).strip()
        expected_heading = expected_by_content.get(content)
        if expected_heading is None:
            errors.append(f"{label}含未声明的二级标题: {line}")
        elif line != expected_heading:
            errors.append(f"{label}二级标题必须使用规范写法: {expected_heading}")

    matches: list[re.Match[str]] = []
    for heading in headings:
        heading_matches = list(re.finditer(rf"(?m)^{re.escape(heading)}$", body))
        if not heading_matches:
            errors.append(f"{label}缺少必需标题: {heading}")
        elif len(heading_matches) > 1:
            errors.append(f"{label}必需标题必须且只能出现一次: {heading}")
        else:
            matches.append(heading_matches[0])
    if errors:
        return errors
    positions = [match.start() for match in matches]
    if positions != sorted(positions):
        errors.append(f"{label}必需标题顺序错误")
        return errors
    for index, (heading, match) in enumerate(zip(headings, matches)):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        if not has_visible_text(body[match.end():end]):
            errors.append(f"{label}章节不能为空: {heading}")
    return errors


def has_visible_text(value: str) -> bool:
    for character in value:
        if character.isspace():
            continue
        if unicodedata.category(character) in {"Cf", "Cc"}:
            continue
        return True
    return False


def require_visible_formal_markdown(text: str, label: str) -> list[str]:
    _, body, split_errors = split_formal_document(text, label)
    if split_errors:
        return []
    errors: list[str] = []
    if "\t" in body:
        errors.append(f"{label}正式正文不得包含制表符")
    if FENCED_BLOCK_RE.search(body):
        errors.append(f"{label}正式正文不得包含 fenced code block")
    if "<!--" in body or "-->" in body:
        errors.append(f"{label}正式正文不得包含 HTML 注释")
    if RAW_HTML_BLOCK_RE.search(body):
        errors.append(f"{label}正式正文不得包含原始 HTML 块")
    if LINK_REFERENCE_DEFINITION_RE.search(body):
        errors.append(f"{label}正式正文不得包含不可见的链接引用定义；请使用行内链接")
    if SETEXT_OR_THEMATIC_RE.search(body):
        errors.append(f"{label}正式正文不得使用 Setext 标题或横线分隔符")
    return errors


def visible_token_text(text: str, label: str) -> str:
    _, body, split_errors = split_formal_document(text, label)
    if split_errors:
        return ""
    body = re.sub(r"!\[[^\]\r\n]*\]\([^\r\n)]*\)", "", body)
    body = re.sub(r"\[([^\]\r\n]+)\]\([^\r\n)]*\)", r"\1", body)
    body = re.sub(r"(?i)\bhttps?://[^\s)]+", "", body)
    return body


def parse_indented_block(
    text: str,
    block_name: str,
    section_heading: str,
    next_heading: str | None,
    label: str,
) -> tuple[dict[str, str], list[str]]:
    marker_pattern = re.compile(
        rf"(?m)^(?P<line>[ \t]*(?:{re.escape(block_name)}|['\"]{re.escape(block_name)}['\"])[ \t]*:.*)\r?$"
    )
    markers = list(marker_pattern.finditer(text))
    if len(markers) != 1:
        return {}, [f"{label} 必须且只能出现一次"]
    marker = markers[0]
    if marker.group("line") != f"{block_name}:":
        return {}, [f"{label} 标记必须规范写为 {block_name}:"]
    section = re.search(rf"(?m)^{re.escape(section_heading)}\s*$", text)
    next_section = (
        re.search(rf"(?m)^{re.escape(next_heading)}\s*$", text)
        if next_heading is not None
        else None
    )
    if section is None:
        return {}, [f"{label} 所属章节不存在: {section_heading}"]
    section_end = next_section.start() if next_section is not None else len(text)
    if not (section.end() <= marker.start() < section_end):
        return {}, [f"{label} 必须位于章节 {section_heading}"]
    data: dict[str, str] = {}
    errors: list[str] = []
    tail = text[marker.end():]
    if tail.startswith("\r\n"):
        tail = tail[2:]
    elif tail.startswith("\n"):
        tail = tail[1:]
    for line in tail.splitlines():
        if not line.strip():
            errors.append(f"{label} 字段必须连续且紧随块标记")
            continue
        if not line.startswith((" ", "\t")):
            break
        if not line.startswith("  ") or len(line) < 3 or line[2] in {" ", "\t"}:
            errors.append(f"{label} 字段必须恰好缩进两个空格，且不得使用制表符")
            continue
        content = line[2:]
        match = CANONICAL_FIELD_RE.fullmatch(content)
        if match is None:
            errors.append(f"{label} 含不符合规范字段格式 key: value 的缩进行")
            continue
        key, raw_value = match.groups()
        value, scalar_errors = parse_canonical_scalar(
            raw_value,
            f"{label} 字段 {key}",
            key,
            allow_json_container=key in {
                "blocking_issues",
                "priority_focus",
                "required_sections",
                "unresolved_nonblocking",
            },
        )
        errors.extend(scalar_errors)
        if scalar_errors:
            continue
        if key in data:
            errors.append(f"{label} 字段重复: {key}")
            continue
        data[key] = value
    return data, errors


def parse_candidate_id_list(raw_value: str, field: str, label: str) -> tuple[list[str], list[str]]:
    """Parse a JSON-compatible inline YAML list of CAND-### identifiers."""
    if not raw_value:
        return [], []
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError:
        return [], [f"{label} {field} 必须是 JSON 兼容的 YAML 行内列表"]
    if not isinstance(value, list):
        return [], [f"{label} {field} 必须是列表"]

    errors: list[str] = []
    candidate_ids: list[str] = []
    for item in value:
        if not isinstance(item, str) or not CANDIDATE_ID_RE.fullmatch(item):
            errors.append(f"{label} {field} 只能包含 CAND-### 字符串")
            continue
        candidate_ids.append(item)
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append(f"{label} {field} 不得包含重复候选 ID")
    return candidate_ids, errors


def linked_path(owner: Path, raw_value: str, expected_name: str, label: str) -> tuple[Path | None, list[str]]:
    if not raw_value or raw_value == "none":
        return None, [f"{label}链接不能为空"]
    path = (owner.parent / raw_value).resolve()
    errors = [] if path.name == expected_name else [f"{label}文件名必须是 {expected_name}"]
    return path, errors


def validate_selection_evidence(path: Path, expected: dict[str, str] | None = None) -> list[str]:
    text, errors = read_text(path, "选刊证据")
    if errors:
        return errors
    data, parse_errors = parse_frontmatter(text, "选刊证据")
    errors.extend(parse_errors)
    errors.extend(require_fields(data, EVIDENCE_FIELDS, "选刊证据"))
    errors.extend(require_values(data, {
        "artifact_type": "journal_selection_evidence", "schema_version": "1.0"
    }, "选刊证据"))
    errors.extend(require_dates(data, ("generated_at", "last_verified_at"), "选刊证据"))
    errors.extend(require_date_order(
        data, ("generated_at", "last_verified_at"), "选刊证据"
    ))
    errors.extend(require_sections(text, EVIDENCE_HEADINGS, "选刊证据"))
    errors.extend(require_visible_formal_markdown(text, "选刊证据"))
    if PLACEHOLDER_RE.search(text):
        errors.append("选刊证据仍含占位内容")

    shortlist, shortlist_errors = parse_candidate_id_list(
        data.get("shortlist_candidate_ids", ""), "shortlist_candidate_ids", "选刊证据"
    )
    unknown, unknown_errors = parse_candidate_id_list(
        data.get("unknown_hard_gate_candidates", ""),
        "unknown_hard_gate_candidates", "选刊证据",
    )
    failed, failed_errors = parse_candidate_id_list(
        data.get("failed_hard_gate_candidates", ""),
        "failed_hard_gate_candidates", "选刊证据",
    )
    errors.extend(shortlist_errors + unknown_errors + failed_errors)

    shortlist_set = set(shortlist)
    unknown_set = set(unknown)
    failed_set = set(failed)
    if shortlist_set & unknown_set:
        errors.append("选刊证据 shortlist_candidate_ids 不得包含未知硬门候选")
    if shortlist_set & failed_set:
        errors.append("选刊证据 shortlist_candidate_ids 不得包含硬门失败候选")
    if unknown_set & failed_set:
        errors.append("选刊证据同一候选不得同时标记为 unknown 和 fail")

    visible_text = visible_token_text(text, "选刊证据")
    if not re.search(r"\bCAND-\d{3}\b", visible_text):
        errors.append("选刊证据至少需要一个 CAND-### 候选 ID")
    if not re.search(r"\b(?:OFF|IDX)-\d{3}\b", visible_text):
        errors.append("选刊证据至少需要一个官方或权威索引来源 ID（OFF/IDX）")
    if expected:
        for key in ("manuscript_id", "manuscript_revision", "evidence_version"):
            if data.get(key) != expected.get(key):
                errors.append(f"决策与选刊证据的 {key} 不一致")
        selected_candidate_id = expected.get("selected_candidate_id", "")
        if unknown:
            errors.append("confirmed 决策要求 unknown_hard_gate_candidates 严格为空列表")
        if not shortlist:
            errors.append("confirmed 决策要求 shortlist_candidate_ids 至少包含一个候选")
        if selected_candidate_id not in shortlist_set:
            errors.append("目标期刊决策 selected_candidate_id 必须属于结构化短名单")
        if selected_candidate_id in failed_set:
            errors.append("目标期刊决策不得选择 failed_hard_gate_candidates 中的候选")
        if selected_candidate_id in unknown_set:
            errors.append("目标期刊决策不得选择 unknown_hard_gate_candidates 中的候选")
        evidence_verified = date_value(data, "last_verified_at")
        decision_verified = date_value(expected, "last_verified_at")
        decision_confirmed = date_value(expected, "author_confirmed_at")
        if (
            evidence_verified is not None
            and decision_verified is not None
            and evidence_verified > decision_verified
        ):
            errors.append("选刊证据 last_verified_at 不得晚于目标期刊决策 last_verified_at")
        if (
            evidence_verified is not None
            and decision_confirmed is not None
            and evidence_verified > decision_confirmed
        ):
            errors.append("选刊证据核验日期不得晚于作者选刊确认日期")
    return errors


def validate_decision(path: Path) -> list[str]:
    errors: list[str] = []
    if path.name != "target-journal-decision.md":
        errors.append("决策文件名必须是 target-journal-decision.md")
    text, read_errors = read_text(path, "目标期刊决策")
    errors.extend(read_errors)
    if read_errors:
        return errors
    data, parse_errors = parse_frontmatter(text, "目标期刊决策")
    errors.extend(parse_errors)
    errors.extend(require_fields(data, DECISION_FIELDS, "目标期刊决策"))
    errors.extend(require_values(data, {
        "artifact_type": "target_journal_decision",
        "schema_version": "1.0",
        "status": "confirmed",
        "blocking_issues": "[]",
    }, "目标期刊决策"))
    errors.extend(require_dates(
        data, ("last_verified_at", "author_confirmed_at"), "目标期刊决策"
    ))
    errors.extend(require_date_order(
        data, ("last_verified_at", "author_confirmed_at"), "目标期刊决策"
    ))
    errors.extend(require_sections(text, DECISION_HEADINGS, "目标期刊决策"))
    errors.extend(require_visible_formal_markdown(text, "目标期刊决策"))
    if PLACEHOLDER_RE.search(text):
        errors.append("目标期刊决策仍含占位内容")
    visible_text = visible_token_text(text, "目标期刊决策")
    if not re.search(r"\bCAND-\d{3}\b", visible_text):
        errors.append("目标期刊决策至少需要一个 CAND-###")
    if not re.search(r"\b(?:OFF|IDX)-\d{3}\b", visible_text):
        errors.append("目标期刊决策至少需要一个官方或权威索引来源 ID（OFF/IDX）")
    if not CANDIDATE_ID_RE.fullmatch(data.get("selected_candidate_id", "")):
        errors.append("目标期刊决策 selected_candidate_id 必须是 CAND-###")
    author_decision, author_block_errors = parse_indented_block(
        text,
        "author_decision",
        "## 4. 作者确认",
        "## 5. 写作画像交接块",
        "目标期刊决策 author_decision",
    )
    errors.extend(author_block_errors)
    if author_decision.get("status") != "confirmed":
        errors.append("目标期刊决策 author_decision.status 必须是 confirmed")
    if author_decision.get("confirmed_at") != data.get("author_confirmed_at"):
        errors.append("目标期刊决策 author_decision.confirmed_at 必须与头部一致")
    if set(author_decision) != {"status", "confirmed_at"}:
        errors.append("目标期刊决策 author_decision 只能包含 status 与 confirmed_at")
    evidence_path, link_errors = linked_path(
        path, data.get("selection_evidence_file", ""),
        "journal-selection-evidence.md", "选刊证据",
    )
    errors.extend(link_errors)
    if evidence_path:
        errors.extend(validate_selection_evidence(evidence_path, data))
        if not SHA256_RE.fullmatch(data.get("selection_evidence_sha256", "")):
            errors.append("目标期刊决策 selection_evidence_sha256 必须是 64 位小写 SHA-256")
        elif evidence_path.is_file():
            actual_evidence_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
            if data.get("selection_evidence_sha256") != actual_evidence_digest:
                errors.append("目标期刊决策 selection_evidence_sha256 与选刊证据文件字节不一致")
    return errors


def validate_profile(
    path: Path,
    label: str,
    kind: str,
    version_key: str,
    headings: tuple[str, ...],
    contract: dict[str, str],
) -> list[str]:
    text, errors = read_text(path, label)
    if errors:
        return errors
    data, parse_errors = parse_frontmatter(text, label)
    errors.extend(parse_errors)
    fields = (
        "artifact_type", version_key, "writing_profile_evidence_id", "manuscript_id",
        "manuscript_revision", "generated_at", "last_verified_at",
    )
    if kind == "journal_writing_profile":
        fields += ("target_journal", "article_type")
    else:
        fields += ("research_field",)
    errors.extend(require_fields(data, fields, label))
    errors.extend(require_values(data, {"artifact_type": kind, version_key: "2.0"}, label))
    errors.extend(require_dates(data, ("generated_at", "last_verified_at"), label))
    errors.extend(require_date_order(data, ("generated_at", "last_verified_at"), label))
    errors.extend(require_sections(text, headings, label))
    errors.extend(require_visible_formal_markdown(text, label))
    visible_text = visible_token_text(text, label)
    for key in ("writing_profile_evidence_id", "manuscript_id", "manuscript_revision"):
        if data.get(key) != contract.get(key):
            errors.append(f"契约与{label}的 {key} 不一致")
    profile_verified = date_value(data, "last_verified_at")
    contract_verified = date_value(contract, "last_verified_at")
    contract_confirmed = date_value(contract, "author_confirmed_at")
    if (
        profile_verified is not None
        and contract_verified is not None
        and profile_verified > contract_verified
    ):
        errors.append(f"{label} last_verified_at 不得晚于写作契约 last_verified_at")
    if (
        profile_verified is not None
        and contract_confirmed is not None
        and profile_verified > contract_confirmed
    ):
        errors.append(f"{label}核验日期不得晚于写作契约作者确认日期")
    if kind == "journal_writing_profile":
        for key in ("target_journal", "article_type"):
            if data.get(key) != contract.get(key):
                errors.append(f"契约与{label}的 {key} 不一致")
        if not re.search(r"\bJP-\d{3}\b", visible_text):
            errors.append(f"{label}至少需要一个 JP-###")
        if not re.search(r"\[O\d+\]", visible_text):
            errors.append(f"{label}至少需要一个官方来源 [O#]")
    else:
        if not re.search(r"\bFB-\d{3}\b", visible_text):
            errors.append(f"{label}至少需要一个 FB-###")
    if PLACEHOLDER_RE.search(text):
        errors.append(f"{label}仍含占位内容")
    return errors


def validate_contract(path: Path) -> list[str]:
    errors: list[str] = []
    if path.name != "target-journal-writing-contract.md":
        errors.append("契约文件名必须是 target-journal-writing-contract.md")
    text, read_errors = read_text(path, "写作契约")
    errors.extend(read_errors)
    if read_errors:
        return errors
    data, parse_errors = parse_frontmatter(text, "写作契约")
    errors.extend(parse_errors)
    errors.extend(require_fields(data, CONTRACT_FIELDS, "写作契约"))
    errors.extend(require_values(data, {
        "artifact_type": "target_journal_writing_contract",
        "contract_version": "2.0",
        "status": "confirmed",
        "requires_recheck_before_submission": "true",
        "blocking_issues": "[]",
    }, "写作契约"))
    errors.extend(require_dates(
        data, ("generated_at", "last_verified_at", "author_confirmed_at"), "写作契约"
    ))
    errors.extend(require_date_order(
        data,
        ("generated_at", "last_verified_at", "author_confirmed_at"),
        "写作契约",
    ))
    errors.extend(require_sections(text, CONTRACT_HEADINGS, "写作契约"))
    errors.extend(require_visible_formal_markdown(text, "写作契约"))
    visible_text = visible_token_text(text, "写作契约")
    if PLACEHOLDER_RE.search(text):
        errors.append("写作契约仍含占位内容")
    if not SHA256_RE.fullmatch(data.get("decision_sha256", "")):
        errors.append("写作契约 decision_sha256 必须是 64 位小写 SHA-256")

    contract_author_decision, contract_author_errors = parse_indented_block(
        text,
        "contract_author_decision",
        "## 11. 作者确认",
        "## 12. Paper Navigator 交接块",
        "写作契约 contract_author_decision",
    )
    errors.extend(contract_author_errors)
    expected_author_decision = {
        "status": "confirmed",
        "confirmed_at": data.get("author_confirmed_at", ""),
        "blocking_issues": "[]",
    }
    for key, expected in expected_author_decision.items():
        if contract_author_decision.get(key) != expected:
            errors.append(
                f"写作契约作者确认块 {key} 必须与头部一致，当前为 {contract_author_decision.get(key)!r}"
            )
    if set(contract_author_decision) != set(expected_author_decision):
        errors.append("写作契约 contract_author_decision 只能包含三个规定字段")

    handoff, handoff_block_errors = parse_indented_block(
        text,
        "paper_navigator_handoff",
        "## 12. Paper Navigator 交接块",
        None,
        "写作契约 paper_navigator_handoff",
    )
    errors.extend(handoff_block_errors)
    expected_handoff = {
        "contract_status": "confirmed",
        "author_confirmation": "confirmed",
        "target_journal": data.get("target_journal", ""),
        "article_type": data.get("article_type", ""),
        "selection_evidence_version": data.get("selection_evidence_version", ""),
        "writing_profile_evidence_id": data.get("writing_profile_evidence_id", ""),
        "decision_sha256": data.get("decision_sha256", ""),
        "blocking_issues": "[]",
    }
    for key, expected in expected_handoff.items():
        if handoff.get(key) != expected:
            errors.append(f"写作契约交接块 {key} 必须与头部一致，当前为 {handoff.get(key)!r}")
    optional_handoff_fields = {
        "priority_focus",
        "required_sections",
        "journal_profile_source",
        "field_blueprint_source",
        "section_budget_source",
        "evidence_gate_source",
        "terminology_source",
        "fusion_decision_source",
        "unresolved_nonblocking",
    }
    unknown_handoff_fields = set(handoff) - set(expected_handoff) - optional_handoff_fields
    if unknown_handoff_fields:
        errors.append(
            "写作契约交接块含未知字段: " + ", ".join(sorted(unknown_handoff_fields))
        )
    for prefix in ("JP", "FB", "FR"):
        if not re.search(rf"\b{prefix}-\d{{3}}\b", visible_text):
            errors.append(f"写作契约至少需要一个 {prefix}-### 规则")
    if not re.search(r"\[O\d+\]", visible_text):
        errors.append("写作契约至少需要一个官方来源 [O#]")
    for category in ("A", "B", "C", "D"):
        if not re.search(rf"(?<![A-Za-z]){category}(?![A-Za-z])", visible_text):
            errors.append(f"写作契约缺少 {category} 类来源摘要")

    decision_path, decision_errors = linked_path(
        path, data.get("decision_file", ""), "target-journal-decision.md", "目标期刊决策"
    )
    journal_path, journal_errors = linked_path(
        path, data.get("journal_profile_file", ""), "journal-writing-profile.md", "期刊画像"
    )
    field_path, field_errors = linked_path(
        path, data.get("field_blueprint_file", ""), "field-writing-blueprint.md", "领域蓝图"
    )
    errors.extend(decision_errors + journal_errors + field_errors)
    if decision_path:
        errors.extend(validate_decision(decision_path))
        decision_text, read_errors = read_text(decision_path, "目标期刊决策")
        if not read_errors:
            decision, _ = parse_frontmatter(decision_text, "目标期刊决策")
            for key in (
                "manuscript_id", "manuscript_revision", "target_journal",
                "article_type", "section_or_collection",
            ):
                if decision.get(key) != data.get(key):
                    errors.append(f"决策与契约的 {key} 不一致")
            if decision.get("evidence_version") != data.get("selection_evidence_version"):
                errors.append("决策 evidence_version 与契约 selection_evidence_version 不一致")
            decision_verified = date_value(decision, "last_verified_at")
            decision_confirmed = date_value(decision, "author_confirmed_at")
            contract_verified = date_value(data, "last_verified_at")
            contract_confirmed = date_value(data, "author_confirmed_at")
            if (
                decision_verified is not None
                and contract_verified is not None
                and decision_verified > contract_verified
            ):
                errors.append("目标期刊决策 last_verified_at 不得晚于写作契约 last_verified_at")
            if (
                decision_confirmed is not None
                and contract_confirmed is not None
                and decision_confirmed > contract_confirmed
            ):
                errors.append("作者选刊确认日期不得晚于写作契约作者确认日期")
            actual_digest = hashlib.sha256(decision_path.read_bytes()).hexdigest()
            if data.get("decision_sha256") != actual_digest:
                errors.append("契约 decision_sha256 与决策文件字节不一致")
    if journal_path:
        errors.extend(validate_profile(
            journal_path, "期刊画像", "journal_writing_profile", "profile_version",
            JOURNAL_PROFILE_HEADINGS, data,
        ))
        if not SHA256_RE.fullmatch(data.get("journal_profile_sha256", "")):
            errors.append("写作契约 journal_profile_sha256 必须是 64 位小写 SHA-256")
        elif journal_path.is_file():
            actual_journal_digest = hashlib.sha256(journal_path.read_bytes()).hexdigest()
            if data.get("journal_profile_sha256") != actual_journal_digest:
                errors.append("写作契约 journal_profile_sha256 与期刊画像文件字节不一致")
    if field_path:
        errors.extend(validate_profile(
            field_path, "领域蓝图", "field_writing_blueprint", "blueprint_version",
            FIELD_PROFILE_HEADINGS, data,
        ))
        if not SHA256_RE.fullmatch(data.get("field_blueprint_sha256", "")):
            errors.append("写作契约 field_blueprint_sha256 必须是 64 位小写 SHA-256")
        elif field_path.is_file():
            actual_field_digest = hashlib.sha256(field_path.read_bytes()).hexdigest()
            if data.get("field_blueprint_sha256") != actual_field_digest:
                errors.append("写作契约 field_blueprint_sha256 与领域蓝图文件字节不一致")
    return errors


def validate(path: Path) -> list[str]:
    text, errors = read_text(path, "输入文件")
    if errors:
        return errors
    data, parse_errors = parse_frontmatter(text, "输入文件")
    if parse_errors:
        return parse_errors
    kind = data.get("artifact_type")
    if kind == "target_journal_decision":
        return validate_decision(path)
    if kind == "target_journal_writing_contract":
        return validate_contract(path)
    return ["只接受 target_journal_decision 或 target_journal_writing_contract 正式交接产物"]


def write_valid_fixture(root: Path) -> dict[str, Path]:
    """Write a valid cross-skill fixture; production validation still uses validate()."""
    if True:
        root.mkdir(parents=True, exist_ok=True)
        root = Path(root)
        evidence = root / "journal-selection-evidence.md"
        decision = root / "target-journal-decision.md"
        journal = root / "journal-writing-profile.md"
        field = root / "field-writing-blueprint.md"
        contract = root / "target-journal-writing-contract.md"

        evidence.write_text("""---
artifact_type: "journal_selection_evidence"
schema_version: "1.0"
evidence_version: "ev-001"
manuscript_id: "ms-001"
manuscript_revision: "r1"
generated_at: "2026-08-10"
last_verified_at: "2026-08-10"
shortlist_candidate_ids: ["CAND-001"]
unknown_hard_gate_candidates: []
failed_hard_gate_candidates: ["CAND-002"]
---
# 选刊证据
## 1. 研究快照与作者约束
稿件为示例研究论文，作者确认官方范围为硬门。
## 2. 证据来源与核验日期
OFF-001，核验日期 2026-08-10。
## 3. 硬门结果
CAND-001 全部通过。未知硬门候选：无
## 4. 软偏好、权重与评分理由
等权，作者可替换。
## 5. 淘汰与待核验候选
CAND-002 因硬门失败淘汰。
## 6. 短名单及取舍
CAND-001。
## 7. 推荐次序与适用条件
CAND-001 首选。
""", encoding="utf-8")

        evidence_digest = hashlib.sha256(evidence.read_bytes()).hexdigest()

        decision.write_text("""---
artifact_type: "target_journal_decision"
schema_version: "1.0"
status: "confirmed"
manuscript_id: "ms-001"
manuscript_revision: "r1"
target_journal: "示例期刊"
article_type: "Research Article"
section_or_collection: "none"
evidence_version: "ev-001"
last_verified_at: "2026-08-10"
author_confirmed_at: "2026-08-10"
selected_candidate_id: "CAND-001"
selection_evidence_file: "./journal-selection-evidence.md"
selection_evidence_sha256: "__EVIDENCE_SHA256__"
blocking_issues: []
---
# 目标期刊决策
## 1. 选定期刊与论文类型
CAND-001，示例期刊，Research Article。
## 2. 硬门结论
均通过，依据 OFF-001。
## 3. 软偏好与取舍
主题匹配优先。
## 4. 作者确认
author_decision:
  status: confirmed
  confirmed_at: "2026-08-10"
## 5. 写作画像交接块
可以建立画像。
""".replace("__EVIDENCE_SHA256__", evidence_digest), encoding="utf-8")

        decision_digest = hashlib.sha256(decision.read_bytes()).hexdigest()

        journal.write_text("""---
artifact_type: "journal_writing_profile"
profile_version: "2.0"
writing_profile_evidence_id: "profile-001"
manuscript_id: "ms-001"
manuscript_revision: "r1"
target_journal: "示例期刊"
article_type: "Research Article"
generated_at: "2026-08-10"
last_verified_at: "2026-08-10"
---
# 期刊画像
## 1. 目标期刊与论文类型
示例期刊，Research Article。
## 2. 官方规则与编辑范围
[O1]
## 3. A/C 样本选择和评分摘要
A C J R E U
## 4. 期刊结构、表达与边界
只记录多篇样本的可重复观察。
## 5. 章节用途矩阵
摘要与引言均有用途记录。
## 6. 期刊轨道规则清单
JP-001
""", encoding="utf-8")

        journal_digest = hashlib.sha256(journal.read_bytes()).hexdigest()

        field.write_text("""---
artifact_type: "field_writing_blueprint"
blueprint_version: "2.0"
writing_profile_evidence_id: "profile-001"
manuscript_id: "ms-001"
manuscript_revision: "r1"
research_field: "示例领域"
generated_at: "2026-08-10"
last_verified_at: "2026-08-10"
---
# 领域蓝图
## 1. 当前论文研究画像
对象、问题、方法与输出已登记。
## 2. A/B 样本选择和评分摘要
A B J R E U
## 3. 领域论证链与方法子群
方法子群边界已记录。
## 4. 章节用途矩阵
方法、结果和讨论均有用途记录。
## 5. 领域轨道规则清单
FB-001
""", encoding="utf-8")

        field_digest = hashlib.sha256(field.read_bytes()).hexdigest()

        contract.write_text(f"""---
artifact_type: "target_journal_writing_contract"
contract_version: "2.0"
contract_id: "contract-001"
status: "confirmed"
manuscript_id: "ms-001"
manuscript_revision: "r1"
target_journal: "示例期刊"
article_type: "Research Article"
section_or_collection: "none"
research_field: "示例领域"
generated_at: "2026-08-10"
last_verified_at: "2026-08-10"
author_confirmed_at: "2026-08-10"
selection_evidence_version: "ev-001"
writing_profile_evidence_id: "profile-001"
decision_file: "./target-journal-decision.md"
decision_sha256: "{decision_digest}"
journal_profile_file: "./journal-writing-profile.md"
journal_profile_sha256: "{journal_digest}"
field_blueprint_file: "./field-writing-blueprint.md"
field_blueprint_sha256: "{field_digest}"
requires_recheck_before_submission: true
blocking_issues: []
---
# 写作契约
## 1. 目标定义与选择依据
目标为示例期刊 Research Article。
## 2. 双轨来源与可信度摘要
A B C D [O1]
## 3. 编辑侧重点与贡献排序
JP-001 FB-001 FR-001
## 4. 全文架构与篇幅预算
章节和篇幅预算已登记。
## 5. 章节写作合同
摘要、引言、方法、结果、讨论和结论的职责已登记。
## 6. 图表与补充材料合同
图表与补充材料边界已登记。
## 7. 语言、术语与语气
仅登记官方机械语言规则。
## 8. 证据门槛
核心主张必须有直接证据。
## 9. 禁止事项
不得弱化证据边界。
## 10. 融合决策与冲突裁决
高影响冲突由作者确认。
## 11. 作者确认
contract_author_decision:
  status: confirmed
  confirmed_at: "2026-08-10"
  blocking_issues: []
## 12. Paper Navigator 交接块
paper_navigator_handoff:
  contract_status: confirmed
  author_confirmation: confirmed
  target_journal: "示例期刊"
  article_type: "Research Article"
  selection_evidence_version: "ev-001"
  writing_profile_evidence_id: "profile-001"
  decision_sha256: "{decision_digest}"
  blocking_issues: []
""", encoding="utf-8")

        return {
            "evidence": evidence,
            "decision": decision,
            "journal_profile": journal,
            "field_blueprint": field,
            "contract": contract,
        }


def run_self_test() -> list[str]:
    with tempfile.TemporaryDirectory(prefix="journal-navigator-selftest-") as temp:
        paths = write_valid_fixture(Path(temp))
        evidence = paths["evidence"]
        decision = paths["decision"]
        journal_profile = paths["journal_profile"]
        contract = paths["contract"]
        decision_digest = hashlib.sha256(decision.read_bytes()).hexdigest()

        errors: list[str] = []
        if validate(decision):
            errors.append("有效决策样例未通过")
        else:
            print("PASS: valid confirmed journal decision")
        if validate(contract):
            errors.append("有效契约样例未通过")
        else:
            print("PASS: valid confirmed writing contract")

        valid_decision_dates = decision.read_text(encoding="utf-8")
        impossible_month = valid_decision_dates.replace(
            'last_verified_at: "2026-08-10"',
            'last_verified_at: "2026-99-10"',
            1,
        )
        decision.write_text(impossible_month, encoding="utf-8")
        month_errors = validate(decision)
        impossible_day = valid_decision_dates.replace(
            'author_confirmed_at: "2026-08-10"',
            'author_confirmed_at: "2026-02-30"',
            1,
        ).replace(
            'confirmed_at: "2026-08-10"',
            'confirmed_at: "2026-02-30"',
            1,
        )
        decision.write_text(impossible_day, encoding="utf-8")
        day_errors = validate(decision)
        if not any("last_verified_at 必须是真实存在的日历日期" in item for item in month_errors):
            errors.append("不存在月份的日历日期负例未被拒绝")
        elif not any("author_confirmed_at 必须是真实存在的日历日期" in item for item in day_errors):
            errors.append("不存在日期的日历日期负例未被拒绝")
        else:
            print("PASS: reject impossible month and day calendar dates")
        decision.write_text(valid_decision_dates, encoding="utf-8")

        future_decision_dates = valid_decision_dates.replace(
            "2026-08-10", "2099-01-01"
        )
        decision.write_text(future_decision_dates, encoding="utf-8")
        if not any("不得晚于校验当天" in item for item in validate(decision)):
            errors.append("未来核验/作者确认日期负例未被拒绝")
        else:
            print("PASS: reject future verification and author-confirmation dates")

        reversed_decision_dates = valid_decision_dates.replace(
            'author_confirmed_at: "2026-08-10"',
            'author_confirmed_at: "2026-08-09"',
            1,
        ).replace(
            'confirmed_at: "2026-08-10"',
            'confirmed_at: "2026-08-09"',
            1,
        )
        decision.write_text(reversed_decision_dates, encoding="utf-8")
        if not any("日期顺序必须满足" in item for item in validate(decision)):
            errors.append("作者确认早于证据核验的日期顺序负例未被拒绝")
        else:
            print("PASS: reject author confirmation before verification date")
        decision.write_text(valid_decision_dates, encoding="utf-8")

        spaced_frontmatter_key = valid_decision_dates.replace(
            'status: "confirmed"',
            'status: "confirmed"\nstatus : "draft"',
            1,
        )
        decision.write_text(spaced_frontmatter_key, encoding="utf-8")
        if not any("不符合规范字段格式" in item for item in validate(decision)):
            errors.append("冒号前空格的 YAML 重复键负例未被拒绝")
        else:
            print("PASS: reject noncanonical frontmatter key with space before colon")

        quoted_frontmatter_key = valid_decision_dates.replace(
            'status: "confirmed"',
            'status: "confirmed"\n\'status\': "draft"',
            1,
        )
        decision.write_text(quoted_frontmatter_key, encoding="utf-8")
        if not any("不符合规范字段格式" in item for item in validate(decision)):
            errors.append("带引号的 YAML 重复键负例未被拒绝")
        else:
            print("PASS: reject quoted frontmatter key outside canonical subset")

        unbalanced_frontmatter_quote = valid_decision_dates.replace(
            'status: "confirmed"',
            "status: 'confirmed",
            1,
        )
        decision.write_text(unbalanced_frontmatter_quote, encoding="utf-8")
        if not any("引号必须同种、成对闭合" in item for item in validate(decision)):
            errors.append("YAML 头部未闭合单引号负例未被拒绝")
        else:
            print("PASS: reject unbalanced frontmatter scalar quote")

        yaml_indicator_cases = (
            ('target_journal: # hidden comment', "YAML comment"),
            ('target_journal: Example: Journal', "colon indicator"),
            ('target_journal: &x ExampleJournal', "anchor"),
            ('target_journal: !!str ExampleJournal', "tag"),
        )
        for replacement, description in yaml_indicator_cases:
            case = valid_decision_dates.replace(
                'target_journal: "示例期刊"', replacement, 1
            )
            decision.write_text(case, encoding="utf-8")
            if not any("必须使用同种成对引号" in item for item in validate(decision)):
                errors.append(f"未加引号的 {description} 标量负例未被拒绝")
            else:
                print(f"PASS: reject unquoted YAML {description} scalar")

        implicit_scalar_cases = (
            ('target_journal: "示例期刊"', 'target_journal: null', "null"),
            ('target_journal: "示例期刊"', 'target_journal: true', "boolean"),
            ('article_type: "Research Article"', 'article_type: 1', "integer"),
            ('schema_version: "1.0"', 'schema_version: 1.0', "float"),
            ('last_verified_at: "2026-08-10"', 'last_verified_at: 2026-08-10', "date"),
        )
        for original, replacement, description in implicit_scalar_cases:
            case = valid_decision_dates.replace(original, replacement, 1)
            decision.write_text(case, encoding="utf-8")
            if not any("裸标量不在该字段允许的机器字面量中" in item for item in validate(decision)):
                errors.append(f"未加引号的 YAML {description} 隐式类型负例未被拒绝")
            else:
                print(f"PASS: reject unquoted YAML implicit {description} scalar")

        implicit_numeric_lexemes = ("0123", ".5", "1.", "0b1010", "00", "01", "-.5")
        for lexeme in implicit_numeric_lexemes:
            case = valid_decision_dates.replace(
                'target_journal: "示例期刊"', f"target_journal: {lexeme}", 1
            )
            decision.write_text(case, encoding="utf-8")
            if not any(
                "裸标量不在该字段允许的机器字面量中" in item
                for item in validate(decision)
            ):
                errors.append(f"自由文本字段的未加引号数字词形 {lexeme} 未被拒绝")
            else:
                print(f"PASS: reject unquoted numeric-looking scalar {lexeme}")

        overflowing_json_number = valid_decision_dates.replace(
            "blocking_issues: []", "blocking_issues: [1e999]", 1
        )
        decision.write_text(overflowing_json_number, encoding="utf-8")
        if not any("行内数组或对象必须是严格 JSON" in item for item in validate(decision)):
            errors.append("JSON 容器中溢出为非有限值的数字负例未被拒绝")
        else:
            print("PASS: reject overflowing non-finite JSON number")

        escaped_scalar_cases = (
            (r'target_journal: "\u793a\u4f8b\u671f\u520a"', "unicode escape"),
            (r'target_journal: "Example\nJournal"', "newline escape"),
            (r'target_journal: "\x45xample Journal"', "hex escape"),
        )
        for replacement, description in escaped_scalar_cases:
            case = valid_decision_dates.replace(
                'target_journal: "示例期刊"', replacement, 1
            )
            decision.write_text(case, encoding="utf-8")
            if not any("不得包含反斜线转义" in item for item in validate(decision)):
                errors.append(f"双引号 {description} 解析差异负例未被拒绝")
            else:
                print(f"PASS: reject quoted scalar {description}")

        spaced_block_key = valid_decision_dates.replace(
            "  status: confirmed",
            "  status: confirmed\n  status : pending_confirmation",
            1,
        )
        decision.write_text(spaced_block_key, encoding="utf-8")
        if not any("含不符合规范字段格式" in item for item in validate(decision)):
            errors.append("确认块冒号前空格的重复键负例未被拒绝")
        else:
            print("PASS: reject noncanonical key in author confirmation block")

        unbalanced_block_quote = valid_decision_dates.replace(
            "  status: confirmed",
            '  status: "confirmed',
            1,
        )
        decision.write_text(unbalanced_block_quote, encoding="utf-8")
        if not any("引号必须同种、成对闭合" in item for item in validate(decision)):
            errors.append("确认块未闭合双引号负例未被拒绝")
        else:
            print("PASS: reject unbalanced structured-block scalar quote")

        block_layout_cases = (
            (
                valid_decision_dates.replace(
                    "  status: confirmed\n  confirmed_at:",
                    "    status: confirmed\n    confirmed_at:",
                    1,
                ),
                "four-space code indentation",
            ),
            (
                valid_decision_dates.replace(
                    "  status: confirmed\n  confirmed_at:",
                    "\tstatus: confirmed\n\tconfirmed_at:",
                    1,
                ),
                "tab code indentation",
            ),
            (
                valid_decision_dates.replace(
                    "author_decision:\n  status: confirmed\n  confirmed_at:",
                    "author_decision:\n\n    status: confirmed\n    confirmed_at:",
                    1,
                ),
                "blank line plus code indentation",
            ),
        )
        for case, description in block_layout_cases:
            decision.write_text(case, encoding="utf-8")
            block_errors = validate(decision)
            if not any(
                "恰好缩进两个空格" in item or "字段必须连续" in item
                for item in block_errors
            ):
                errors.append(f"确认块 {description} 负例未被拒绝")
            else:
                print(f"PASS: reject author block {description}")

        for alternate_marker in ("author_decision :", "'author_decision':"):
            case = valid_decision_dates.replace(
                "## 5. 写作画像交接块",
                alternate_marker
                + "\n  status: pending_confirmation\n  confirmed_at: \"2026-08-10\"\n"
                + "## 5. 写作画像交接块",
                1,
            )
            decision.write_text(case, encoding="utf-8")
            if not any("必须且只能出现一次" in item for item in validate(decision)):
                errors.append(f"等价确认块标记 {alternate_marker!r} 负例未被拒绝")
            else:
                print(f"PASS: reject alternate author block marker {alternate_marker!r}")

        shifted_by_noncanonical_h2 = valid_decision_dates.replace(
            "author_decision:",
            "## 5. 写作画像交接块 ##\nauthor_decision:",
            1,
        )
        decision.write_text(shifted_by_noncanonical_h2, encoding="utf-8")
        if not any("二级标题必须使用规范写法" in item for item in validate(decision)):
            errors.append("非规范等价 H2 改变确认块章节归属的负例未被拒绝")
        else:
            print("PASS: reject noncanonical equivalent H2 before author block")

        leading_space_h2 = valid_decision_dates + "\n ## 2. 硬门结论\n"
        decision.write_text(leading_space_h2, encoding="utf-8")
        if not any("二级标题必须使用规范写法" in item for item in validate(decision)):
            errors.append("带前导空格的 CommonMark 等价 H2 负例未被拒绝")
        else:
            print("PASS: reject leading-space equivalent H2")

        setext_shift = valid_decision_dates.replace(
            "author_decision:",
            "写作画像交接块\n---\nauthor_decision:",
            1,
        )
        decision.write_text(setext_shift, encoding="utf-8")
        if not any("Setext 标题" in item for item in validate(decision)):
            errors.append("Setext H2 改变确认块章节归属的负例未被拒绝")
        else:
            print("PASS: reject Setext heading before author block")

        decision_parts = valid_decision_dates.split("---", 2)
        fenced_decision = (
            "---" + decision_parts[1] + "---\n```text\n"
            + decision_parts[2].lstrip() + "\n```\n"
        )
        decision.write_text(fenced_decision, encoding="utf-8")
        if not any("fenced code block" in item for item in validate(decision)):
            errors.append("整个正式正文被 fenced code 包裹的负例未被拒绝")
        else:
            print("PASS: reject formal decision body hidden in fenced code")

        html_wrapped_decision = (
            "---" + decision_parts[1] + "---\n<pre>\n"
            + decision_parts[2].lstrip() + "\n</pre>\n"
        )
        decision.write_text(html_wrapped_decision, encoding="utf-8")
        if not any("原始 HTML 块" in item for item in validate(decision)):
            errors.append("整个正式正文被原始 HTML 块包裹的负例未被拒绝")
        else:
            print("PASS: reject formal decision body hidden in raw HTML")

        raw_html_wrappers = (
            ("<?paperline-hide", "?>", "processing instruction"),
            ("<!HIDE", ">", "markup declaration"),
            ("<![CDATA[", "]]>", "CDATA block"),
        )
        for opener, closer, description in raw_html_wrappers:
            wrapped = (
                "---" + decision_parts[1] + "---\n" + opener + "\n"
                + decision_parts[2].lstrip() + "\n" + closer + "\n"
            )
            decision.write_text(wrapped, encoding="utf-8")
            if not any("原始 HTML 块" in item for item in validate(decision)):
                errors.append(f"正文被 {description} 包裹的负例未被拒绝")
            else:
                print(f"PASS: reject formal decision body hidden in {description}")

        malformed_closing_delimiter = valid_decision_dates.replace(
            "\n---\n# 目标期刊决策",
            "\n--- trailing\n# 目标期刊决策",
            1,
        )
        decision.write_text(malformed_closing_delimiter, encoding="utf-8")
        if not any("闭合分隔符" in item for item in validate(decision)):
            errors.append("带尾随文本的 YAML 闭合分隔符负例未被拒绝")
        else:
            print("PASS: reject noncanonical YAML frontmatter delimiter")
        decision.write_text(valid_decision_dates, encoding="utf-8")

        valid_evidence = evidence.read_text(encoding="utf-8")
        invalid_evidence = valid_evidence.replace(
            "unknown_hard_gate_candidates: []",
            'unknown_hard_gate_candidates: ["CAND-003"]',
            1,
        )
        evidence.write_text(invalid_evidence, encoding="utf-8")
        if not validate(decision):
            errors.append("结构化未知硬门负例未被拒绝")
        else:
            print("PASS: reject structured unknown hard gate despite prose magic phrase")
        evidence.write_text(valid_evidence, encoding="utf-8")

        duplicate_unknown = valid_evidence.replace(
            "unknown_hard_gate_candidates: []",
            'unknown_hard_gate_candidates: ["CAND-003"]\nunknown_hard_gate_candidates: []',
            1,
        )
        evidence.write_text(duplicate_unknown, encoding="utf-8")
        if not validate(decision):
            errors.append("重复键覆盖未知硬门的负例未被拒绝")
        else:
            print("PASS: reject duplicate frontmatter key hiding an unknown hard gate")
        evidence.write_text(valid_evidence, encoding="utf-8")

        failed_selected = valid_evidence.replace(
            'failed_hard_gate_candidates: ["CAND-002"]',
            'failed_hard_gate_candidates: ["CAND-001"]',
            1,
        )
        evidence.write_text(failed_selected, encoding="utf-8")
        if not validate(decision):
            errors.append("所选候选硬门失败的结构化负例未被拒绝")
        else:
            print("PASS: reject selected candidate with failed hard gate")
        evidence.write_text(valid_evidence, encoding="utf-8")

        official_evidence = evidence.read_text(encoding="utf-8")
        official_decision = decision.read_text(encoding="utf-8")
        evidence.write_text(official_evidence.replace("OFF-001", "USR-001"), encoding="utf-8")
        decision.write_text(official_decision.replace("OFF-001", "USR-001"), encoding="utf-8")
        if not validate(decision):
            errors.append("只有作者陈述、没有官方/索引证据的负例未被拒绝")
        else:
            print("PASS: reject decision without official/index evidence")
        evidence.write_text(official_evidence, encoding="utf-8")
        decision.write_text(official_decision, encoding="utf-8")

        hidden_source_evidence = (
            official_evidence.replace("OFF-001", "USR-001")
            + "\n[OFF-001]: https://example.invalid/hidden\n"
        )
        original_evidence_digest = hashlib.sha256(
            official_evidence.encode("utf-8")
        ).hexdigest()
        hidden_evidence_digest = hashlib.sha256(
            hidden_source_evidence.encode("utf-8")
        ).hexdigest()
        hidden_source_decision = (
            official_decision.replace("OFF-001", "USR-001")
            .replace(original_evidence_digest, hidden_evidence_digest, 1)
            + "\n[OFF-001]: https://example.invalid/hidden\n"
        )
        evidence.write_text(hidden_source_evidence, encoding="utf-8")
        decision.write_text(hidden_source_decision, encoding="utf-8")
        hidden_source_errors = validate(decision)
        if not any("链接引用定义" in item for item in hidden_source_errors):
            errors.append("不可见链接定义伪造官方来源 ID 的负例未被拒绝")
        else:
            print("PASS: reject official source ID hidden in link-reference definition")
        evidence.write_text(official_evidence, encoding="utf-8")
        decision.write_text(official_decision, encoding="utf-8")

        changed_evidence_bytes = official_evidence.replace(
            "等权，作者可替换。",
            "等权，但本行在决策锁定后被修改。",
            1,
        )
        evidence.write_text(changed_evidence_bytes, encoding="utf-8")
        if not validate(decision):
            errors.append("选刊证据字节变化但版本不变的负例未被拒绝")
        else:
            print("PASS: reject changed selection-evidence bytes behind a stable version")
        evidence.write_text(official_evidence, encoding="utf-8")

        pending_author = official_decision.replace(
            "author_decision:\n  status: confirmed",
            "author_decision:\n  status: pending_confirmation",
            1,
        )
        decision.write_text(pending_author, encoding="utf-8")
        if not validate(decision):
            errors.append("结构化作者确认未完成的负例未被拒绝")
        else:
            print("PASS: reject unconfirmed author decision")
        decision.write_text(official_decision, encoding="utf-8")

        duplicate_author_status = official_decision.replace(
            "  status: confirmed",
            "  status: pending_confirmation\n  status: confirmed",
            1,
        )
        decision.write_text(duplicate_author_status, encoding="utf-8")
        if not validate(decision):
            errors.append("作者确认块重复键覆盖负例未被拒绝")
        else:
            print("PASS: reject duplicate key in author confirmation block")
        decision.write_text(official_decision, encoding="utf-8")

        author_block_match = re.search(
            r"(?ms)^author_decision:\n(?:^[ \t].*\n?)+",
            official_decision,
        )
        if author_block_match is None:
            errors.append("自测无法定位作者确认块")
        else:
            author_block = author_block_match.group(0)
            misplaced_author = (
                official_decision[:author_block_match.start()]
                + "作者确认块被错误放置。\n"
                + official_decision[author_block_match.end():]
            )
            misplaced_author = misplaced_author.replace(
                "## 1. 选定期刊与论文类型\n",
                "## 1. 选定期刊与论文类型\n" + author_block,
                1,
            )
            decision.write_text(misplaced_author, encoding="utf-8")
            if not validate(decision):
                errors.append("作者确认块放错章节的负例未被拒绝")
            else:
                print("PASS: reject author confirmation block outside its section")
            decision.write_text(official_decision, encoding="utf-8")

        valid_contract = contract.read_text(encoding="utf-8")
        pending_contract_author = valid_contract.replace(
            "contract_author_decision:\n  status: confirmed",
            "contract_author_decision:\n  status: pending_confirmation",
            1,
        )
        contract.write_text(pending_contract_author, encoding="utf-8")
        if not validate(contract):
            errors.append("写作契约第 11 节作者未确认负例未被拒绝")
        else:
            print("PASS: reject unconfirmed contract author decision in section 11")
        contract.write_text(valid_contract, encoding="utf-8")

        valid_journal_profile = journal_profile.read_text(encoding="utf-8")
        journal_profile.write_text(
            valid_journal_profile.replace(
                "只记录多篇样本的可重复观察。",
                "本画像正文在合同锁定后被修改。",
                1,
            ),
            encoding="utf-8",
        )
        if not validate(contract):
            errors.append("期刊画像字节变化但证据 ID 不变的负例未被拒绝")
        else:
            print("PASS: reject changed journal-profile bytes behind a stable evidence ID")
        journal_profile.write_text(valid_journal_profile, encoding="utf-8")

        contract_parts = valid_contract.split("---", 2)
        commented_contract = (
            "---" + contract_parts[1] + "---\n<!--\n"
            + contract_parts[2].lstrip() + "\n-->\n"
        )
        contract.write_text(commented_contract, encoding="utf-8")
        if not any("HTML 注释" in item for item in validate(contract)):
            errors.append("整个正式正文被 HTML 注释包裹的负例未被拒绝")
        else:
            print("PASS: reject formal contract body hidden in HTML comment")

        duplicate_empty_heading = valid_contract.replace(
            "## 4. 全文架构与篇幅预算\n章节和篇幅预算已登记。\n",
            "## 4. 全文架构与篇幅预算\n## 4. 全文架构与篇幅预算\n",
            1,
        )
        contract.write_text(duplicate_empty_heading, encoding="utf-8")
        if not any("必须且只能出现一次" in item for item in validate(contract)):
            errors.append("重复标题掩盖空章节正文的负例未被拒绝")
        else:
            print("PASS: reject duplicate required heading hiding an empty section")

        hidden_section_definition = valid_contract.replace(
            "章节和篇幅预算已登记。",
            "[section-four-hidden]: https://example.invalid/hidden",
            1,
        )
        contract.write_text(hidden_section_definition, encoding="utf-8")
        if not any("链接引用定义" in item for item in validate(contract)):
            errors.append("不可见链接定义充当章节唯一正文的负例未被拒绝")
        else:
            print("PASS: reject link-reference definition as sole section body")

        zero_width_section = valid_contract.replace(
            "章节和篇幅预算已登记。", "\u200b", 1
        )
        contract.write_text(zero_width_section, encoding="utf-8")
        if not any("章节不能为空" in item for item in validate(contract)):
            errors.append("零宽字符充当章节唯一正文的负例未被拒绝")
        else:
            print("PASS: reject zero-width-only section body")

        alternate_contract_author_marker = valid_contract.replace(
            "## 12. Paper Navigator 交接块",
            "contract_author_decision :\n"
            "  status: pending_confirmation\n"
            "  confirmed_at: \"2026-08-10\"\n"
            "  blocking_issues: []\n"
            "## 12. Paper Navigator 交接块",
            1,
        )
        contract.write_text(alternate_contract_author_marker, encoding="utf-8")
        if not any("必须且只能出现一次" in item for item in validate(contract)):
            errors.append("等价 contract_author_decision 标记负例未被拒绝")
        else:
            print("PASS: reject alternate contract-author block marker")

        alternate_handoff_marker = (
            valid_contract
            + "\n'paper_navigator_handoff':\n"
            + "  contract_status: pending_confirmation\n"
        )
        contract.write_text(alternate_handoff_marker, encoding="utf-8")
        if not any("必须且只能出现一次" in item for item in validate(contract)):
            errors.append("等价 paper_navigator_handoff 标记负例未被拒绝")
        else:
            print("PASS: reject alternate Paper Navigator handoff marker")

        duplicate_contract_status = valid_contract.replace(
            "  contract_status: confirmed",
            "  contract_status: pending_confirmation\n  contract_status: confirmed",
            1,
        )
        contract.write_text(duplicate_contract_status, encoding="utf-8")
        if not validate(contract):
            errors.append("Paper Navigator 交接块重复键覆盖负例未被拒绝")
        else:
            print("PASS: reject duplicate key in Paper Navigator handoff block")

        handoff_block_match = re.search(
            r"(?ms)^paper_navigator_handoff:\n(?:^[ \t].*\n?)+",
            valid_contract,
        )
        if handoff_block_match is None:
            errors.append("自测无法定位 Paper Navigator 交接块")
        else:
            handoff_block = handoff_block_match.group(0)
            misplaced_handoff = (
                valid_contract[:handoff_block_match.start()]
                + "交接块被错误放置。\n"
                + valid_contract[handoff_block_match.end():]
            )
            misplaced_handoff = misplaced_handoff.replace(
                "## 1. 目标定义与选择依据\n",
                "## 1. 目标定义与选择依据\n" + handoff_block,
                1,
            )
            contract.write_text(misplaced_handoff, encoding="utf-8")
            if not validate(contract):
                errors.append("Paper Navigator 交接块放错章节的负例未被拒绝")
            else:
                print("PASS: reject Paper Navigator handoff block outside its section")

        bad_contract = valid_contract.replace(
            'writing_profile_evidence_id: "profile-001"',
            'writing_profile_evidence_id: "profile-bad"', 1
        )
        contract.write_text(bad_contract, encoding="utf-8")
        if not validate(contract):
            errors.append("证据 ID 不一致负例未被拒绝")
        else:
            print("PASS: reject writing-profile evidence mismatch")

        mismatched_section = valid_contract.replace(
            'section_or_collection: "none"', 'section_or_collection: "special-section"', 1
        )
        contract.write_text(mismatched_section, encoding="utf-8")
        if not validate(contract):
            errors.append("决策与契约栏目不一致负例未被拒绝")
        else:
            print("PASS: reject decision/contract section mismatch")

        empty_section = valid_contract.replace(
            "## 4. 全文架构与篇幅预算\n章节和篇幅预算已登记。\n",
            "## 4. 全文架构与篇幅预算\n",
            1,
        )
        contract.write_text(empty_section, encoding="utf-8")
        if not validate(contract):
            errors.append("空写作契约章节负例未被拒绝")
        else:
            print("PASS: reject empty writing-contract section")

        stale_decision_hash = valid_contract.replace(decision_digest, "b" * 64)
        contract.write_text(stale_decision_hash, encoding="utf-8")
        if not validate(contract):
            errors.append("契约绑定过期决策哈希的负例未被拒绝")
        else:
            print("PASS: reject stale decision SHA-256 binding")

        wrong_selection_version = valid_contract.replace(
            'selection_evidence_version: "ev-001"',
            'selection_evidence_version: "ev-old"',
        )
        contract.write_text(wrong_selection_version, encoding="utf-8")
        if not validate(contract):
            errors.append("契约与选刊证据版本不一致负例未被拒绝")
        else:
            print("PASS: reject selection-evidence version mismatch")
        return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验期刊选择决策或双轨写作契约。")
    parser.add_argument("artifact", nargs="?", type=Path, help="正式决策或写作契约路径")
    parser.add_argument("--self-test", action="store_true", help="运行内置正例和负例自测")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test()
        if errors:
            print("FAIL: journal-navigator 校验器自测失败")
            for error in errors:
                print(f"- {error}")
            return 1
        print("PASS: journal-navigator 校验器自测通过")
        return 0

    if args.artifact is None:
        parser.error("请提供 artifact 路径，或使用 --self-test")
    errors = validate(args.artifact.resolve())
    if errors:
        print("FAIL: 期刊产物不可交接")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: 期刊产物通过交接校验")
    return 0


if __name__ == "__main__":
    sys.exit(main())
