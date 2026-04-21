#!/usr/bin/env python3
r"""Scan docs/**/*.md for likely-empirical numbers without nearby source.

Focus: percentage claims (%), since they're the most commonly fabricated
(LLM hallucinate "35% improvement" style numbers most often).

Heuristic — A percentage is "unsourced" if:
    - The line contains ``\d+%``
    - No source marker exists within ±2 lines
    - The percentage isn't obviously a code / calculation / example

Source markers:
    - URL (http / https)
    - Markdown link [...](http...) in same paragraph
    - Year citation like (2024) / (NeurIPS 2022)
    - Specific tokens: 来源 / 报告 / 博客 / 官方 / paper / benchmark / 论文
    - Explicit `[来源未验证]` opt-out tag

Usage:
    python scripts/unsourced_numbers_scan.py
    python scripts/unsourced_numbers_scan.py --strict
    python scripts/unsourced_numbers_scan.py --json

Known limitations:
    - Regex-based · no AST parsing · false positives expected
    - Doesn't understand when a number is just an illustration
    - Authors should iterate · the scanner surfaces candidates · not verdicts
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

PERCENT_PATTERN = re.compile(r"(?<![\w\.])\d+(?:\.\d+)?%")

SOURCE_MARKERS = [
    re.compile(r"https?://"),
    re.compile(r"\[(?P<text>[^\]]+)\]\((?P<url>https?://[^)]+)\)"),
    re.compile(r"\((?:19|20)\d{2}\)"),      # (2024)
    re.compile(r"NeurIPS|ICLR|ICML|SIGIR|VLDB|SIGMOD|arXiv"),
    re.compile(r"来源|报告|博客|官方|论文|benchmark", re.IGNORECASE),
    re.compile(r"\[来源未验证\]"),
    re.compile(r"\[来源\]"),
]

# Lines that are obviously not empirical claims (code, tables of contents, etc.)
SKIP_LINE_PATTERNS = [
    re.compile(r"^\s*#{1,6}\s"),           # headings
    re.compile(r"^\s*[-*]\s*$"),            # bare list markers
    re.compile(r"^```"),                     # code fence
    re.compile(r"^\s*\|.*\|.*\|\s*$"),      # table row (multi-column)
]

# Definitional patterns · the % is a concept definition or design target · not empirical claim
# Conservative: only skip when match is high-confidence non-empirical
AVAILABILITY_PATTERN = re.compile(r"\b99\.\d+%")          # 99.9% 99.95% 99.99% SLO targets
PERCENTILE_CONTEXT = re.compile(r"\bp(?:50|90|95|99)\b", re.IGNORECASE)  # p95 line · "%"通常是定义
# 100% 作修辞最大（"不可能 100%" · "追求 100% 不现实"）· · 是中文标点 · 用 [\s·]*
RHETORICAL_100 = re.compile(
    r"100%[\s·]*(?:不|做不到|不可能|不现实|无法|追求|别.*承诺|安全|准确|可靠|覆盖|命中)"
)
# e.g.  " < 5% 触发" / "> 95% 目标" —— design criteria, not empirical
DESIGN_CRITERIA_WORDS = re.compile(
    r"目标|SLO|预算|阈值|触发|budget|target|threshold|"
    r"你得|必须|应该|需要|不能|不超过|超过|以上|以下|限制|确保|保证|"
    r"must|should|limit",
    re.IGNORECASE,
)
# 范围近似（10%-30% / 10%–30% / 10-30% / 10%—30%）· 作者意图是"典型值范围"· 非精确 benchmark
RANGE_APPROX_PATTERN = re.compile(r"\d+\s*%?\s*[-–—~]\s*\d+\s*%")
# 自引用（讨论 scanner/agent/hallucinate 本身的数字）
SELF_REFERENTIAL = re.compile(
    r"scanner|hallucinate|对抗评审|agent 评审|P0 事实错|本轮|本次",
    re.IGNORECASE,
)


# Cheatsheet / comparison page design-target conventions
RECALL_TARGET = re.compile(r"[Rr]ecall(?:@\d+)?\s*\d+%")  # "Recall 95%" / "recall@10 95%" = design target


def _strip_markdown(line: str) -> str:
    """Remove markdown bold/italic markers · let RHETORICAL_100 etc match through **bold**."""
    return re.sub(r"[*`_]+", "", line)


def is_definitional_match(line: str, match: str) -> bool:
    """Return True if the % match is a concept definition or design target · not empirical claim."""
    stripped = _strip_markdown(line)
    # 99.x% — SLO availability convention
    if AVAILABILITY_PATTERN.search(match):
        return True
    # p50/p95/p99 on same line — likely defining the percentile
    if PERCENTILE_CONTEXT.search(line):
        return True
    # 100% only as rhetorical max ("不可能 100%", "追求 100% 不现实")
    if match == "100%" and RHETORICAL_100.search(stripped):
        return True
    # Design criteria keywords on same line — likely SLO target not empirical claim
    if DESIGN_CRITERIA_WORDS.search(line):
        return True
    # Range approximation pattern on line — typically "典型范围"
    if RANGE_APPROX_PATTERN.search(line):
        return True
    # Self-referential (wiki's own observation numbers that come with commit trace as source)
    if SELF_REFERENTIAL.search(line):
        return True
    # Recall target in cheatsheet/comparison context
    if RECALL_TARGET.search(line):
        return True
    return False

SKIP_DIRS = {"_templates"}


def iter_markdown_files():
    for p in sorted(DOCS_DIR.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def has_source_in_context(lines: list[str], i: int, radius: int = 2) -> bool:
    start = max(0, i - radius)
    end = min(len(lines), i + radius + 1)
    context = "\n".join(lines[start:end])
    return any(p.search(context) for p in SOURCE_MARKERS)


def is_skipped_line(line: str) -> bool:
    return any(p.match(line) for p in SKIP_LINE_PATTERNS)


def scan_file(fp: Path) -> list[dict]:
    issues = []
    in_code_block = False
    text = fp.read_text(encoding="utf-8")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if is_skipped_line(line):
            continue
        matches = list(PERCENT_PATTERN.finditer(line))
        if not matches:
            continue
        if has_source_in_context(lines, i, radius=2):
            continue
        for m in matches:
            match_text = m.group(0)
            if is_definitional_match(line, match_text):
                continue
            issues.append({
                "file": fp.relative_to(REPO_ROOT).as_posix(),
                "line": i + 1,
                "match": match_text,
                "snippet": line.strip()[:120],
            })
    return issues


def scan_all() -> list[dict]:
    all_issues = []
    for fp in iter_markdown_files():
        try:
            all_issues.extend(scan_file(fp))
        except Exception:
            continue
    return all_issues


def human_report(issues: list[dict]) -> str:
    if not issues:
        return "## Unsourced numbers scan\n\n✓ No unsourced percentage claims found."
    lines = [f"## Unsourced numbers scan · {len(issues)} candidates\n"]
    lines.append("Heuristic-based · false positives expected. Review each then:")
    lines.append("  · add source citation, or")
    lines.append("  · tag `[来源未验证]` to opt out of the signal.\n")
    lines.append(f"| {'file':<55} | {'line':<5} | {'%':<8} | snippet |")
    lines.append(f"| {'-'*55} | {'-'*5} | {'-'*8} | {'-'*60} |")
    for i in issues:
        lines.append(
            f"| {i['file']:<55} | {i['line']:<5} | {i['match']:<8} | {i['snippet']:<60} |"
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="exit 1 if issues found")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    issues = scan_all()

    if args.json:
        print(json.dumps(issues, indent=2, ensure_ascii=False))
    else:
        print(human_report(issues))

    if args.strict and issues:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
