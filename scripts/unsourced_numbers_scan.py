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
            issues.append({
                "file": fp.relative_to(REPO_ROOT).as_posix(),
                "line": i + 1,
                "match": m.group(0),
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
