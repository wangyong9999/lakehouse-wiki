#!/usr/bin/env python3
"""Scan all docs/**/*.md frontmatter applies_to fields · flag stale versions.

For each page's applies_to field, locate "<product> <version>" patterns and
compare <version> against the latest declared in scripts/known_versions.yml.
If <version> is strictly less, emit a warning row.

Usage:
    python scripts/version_scan.py             # human-readable report, exit 0
    python scripts/version_scan.py --strict    # exit 1 if any stale found
    python scripts/version_scan.py --json      # JSON output for CI consumers

Design principles:
- Conservative: only flag when declared version is provably older. Unknown
  strings are reported as "unknown" not "stale" to avoid false positives.
- Manual lookup table (known_versions.yml). Updated quarterly. Avoids runtime
  HTTP calls (fast, reproducible, no auth needed).
- Heuristic version parsing: tuple of leading integers. "1.10" > "1.9".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("PyYAML required. Install via: pip install pyyaml\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
KNOWN = REPO_ROOT / "scripts" / "known_versions.yml"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def parse_version(v: str) -> tuple[int, ...]:
    """Extract leading numeric tuple · pad to 3 parts so 3.6 == 3.6.0."""
    parts = re.findall(r"\d+", v)
    if not parts:
        return (0, 0, 0)
    nums = [int(p) for p in parts[:3]]
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


def is_older(declared: str, latest: str) -> bool:
    """True if declared version < latest. Conservative on parse errors."""
    if not declared or not latest:
        return False
    try:
        return parse_version(declared) < parse_version(latest)
    except Exception:
        return False


SKIP_DIRS = {"_templates"}


def iter_markdown_files():
    for p in sorted(DOCS_DIR.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def extract_declared_versions(applies_str: str, product: str, aliases: list[str]) -> list[str]:
    """Find versions declared next to the product name in applies_to.

    Matches patterns like 'Trino 480+', 'Spark 3.5.8 LTS', 'DuckDB 1.0-1.3'.
    Returns all version strings found · caller picks max.
    """
    names = [product] + aliases
    declared = []
    for name in names:
        # \b avoids matching "iceberg" inside "pyiceberg" · anchors at word boundary
        pattern = re.compile(
            rf"\b{re.escape(name)}\s+(\d+(?:\.\d+)*)",
            re.IGNORECASE,
        )
        for m in pattern.finditer(applies_str):
            declared.append(m.group(1))
    return declared


def scan():
    data = yaml.safe_load(KNOWN.read_text(encoding="utf-8"))
    products = data.get("products", {})

    stale: list[dict] = []
    fresh: list[dict] = []
    unknown_products: set[str] = set()

    for fp in iter_markdown_files():
        try:
            text = fp.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(text)
        applies = fm.get("applies_to")
        if not applies:
            continue
        applies_str = str(applies)

        for product, info in products.items():
            aliases = info.get("aliases", []) or []
            declared_versions = extract_declared_versions(applies_str, product, aliases)
            if not declared_versions:
                continue

            latest = str(info.get("latest", ""))
            if not latest or not re.search(r"\d", latest):
                continue

            # Use max declared (wiki often writes "X 3.5+ / 4.1" — take latest part)
            max_decl = max(declared_versions, key=parse_version)
            rel = fp.relative_to(REPO_ROOT).as_posix()

            if is_older(max_decl, latest):
                stale.append({
                    "file": rel,
                    "product": product,
                    "declared": max_decl,
                    "latest": latest,
                    "applies_to": applies_str[:120],
                    "source": info.get("source", ""),
                })
            else:
                fresh.append({
                    "file": rel,
                    "product": product,
                    "declared": max_decl,
                    "latest": latest,
                })

    return stale, fresh, unknown_products


def human_report(stale: list, fresh: list) -> str:
    lines = [f"## Version scan  ·  {len(stale)} stale  ·  {len(fresh)} fresh"]
    if stale:
        lines.append("")
        lines.append("### ⚠ Potentially stale")
        lines.append(
            f"| {'file':<48} | {'product':<18} | {'declared':<12} | {'latest':<12} |"
        )
        lines.append(f"| {'-'*48} | {'-'*18} | {'-'*12} | {'-'*12} |")
        for s in stale:
            lines.append(
                f"| {s['file']:<48} | {s['product']:<18} | {s['declared']:<12} | {s['latest']:<12} |"
            )
        lines.append("")
        lines.append("Action: refresh `applies_to` in each file, or update `scripts/known_versions.yml` if the known-latest is outdated.")
    else:
        lines.append("")
        lines.append("✓ All declared versions are fresh or unverifiable.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="exit 1 if stale found")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    args = parser.parse_args()

    stale, fresh, _ = scan()

    if args.json:
        print(json.dumps({"stale": stale, "fresh": fresh}, indent=2, ensure_ascii=False))
    else:
        print(human_report(stale, fresh))

    if args.strict and stale:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
