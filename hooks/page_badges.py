"""MkDocs hook: render Diátaxis kind + depth badges at page top.

Mapping rules:
- frontmatter `kind` wins if set
- else: frontmatter `type` auto-maps to Diátaxis kind
- frontmatter `depth` (入门 / 进阶 / 资深) renders alongside
- badges inject after first H1 in markdown body

Usage: enable via `hooks: [hooks/page_badges.py]` in mkdocs.yml.
"""

from __future__ import annotations

import re

TYPE_TO_KIND = {
    "concept": ("explanation", "explanation"),
    "system": ("explanation", "explanation"),
    "comparison": ("reference", "reference"),
    "scenario": ("how-to", "how-to"),
    "learning-path": ("tutorial", "tutorial"),
    "tutorial": ("tutorial", "tutorial"),
    "adr": ("reference", "reference"),
    "paper-note": ("reference", "reference"),
    "reference": ("reference", "reference"),
    "how-to": ("how-to", "how-to"),
    "explanation": ("explanation", "explanation"),
}

KIND_LABEL = {
    "tutorial":    "Tutorial · 手把手",
    "how-to":      "How-to · 任务导向",
    "reference":   "Reference · 速查",
    "explanation": "Explanation · 原理",
}

KIND_COLOR = {
    "tutorial":    "#2e7d32",
    "how-to":      "#1565c0",
    "reference":   "#6a1b9a",
    "explanation": "#c62828",
}

DEPTH_LABEL = {
    "入门": ("入门", "#558b2f"),
    "进阶": ("进阶", "#ef6c00"),
    "资深": ("资深", "#ad1457"),
}


def _badge(label: str, color: str) -> str:
    return (
        f'<span style="display:inline-block;padding:0.15em 0.55em;'
        f"margin-right:0.4em;border-radius:4px;font-size:0.75em;"
        f"font-weight:600;background:{color};color:#fff;"
        f'vertical-align:middle;">{label}</span>'
    )


def on_page_markdown(markdown, page, config, files, **kwargs):
    """Inject badges right after the first H1."""
    meta = page.meta or {}

    # Skip pages opting out (home, 404, tags index, role landings etc.)
    if meta.get("hide_badges"):
        return markdown
    # Skip pages with no H1 candidate
    if "\n#" not in markdown and not markdown.lstrip().startswith("# "):
        return markdown

    kind = meta.get("kind")
    type_ = meta.get("type")
    if not kind and type_:
        kind, _ = TYPE_TO_KIND.get(str(type_), (None, None))

    depth = meta.get("depth")

    if not kind and not depth:
        return markdown

    parts = []
    if kind and kind in KIND_LABEL:
        parts.append(_badge(KIND_LABEL[kind], KIND_COLOR[kind]))
    if depth:
        depth_label, depth_color = DEPTH_LABEL.get(str(depth), (str(depth), "#546e7a"))
        parts.append(_badge(depth_label, depth_color))

    if not parts:
        return markdown

    badge_block = (
        '<div class="page-badges" style="margin:0.2em 0 1.4em 0;">'
        + "".join(parts)
        + "</div>\n"
    )

    # Find first H1 and inject immediately after
    pattern = re.compile(r"^(#\s+.*?)(\r?\n)", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return markdown

    insert_at = match.end()
    return markdown[:insert_at] + "\n" + badge_block + markdown[insert_at:]
