"""MkDocs hook: render Diátaxis badge + prerequisites block at page top.

Features (all opt-in via frontmatter):
- `kind` (or auto-derived from `type`) → colored badge
- `depth` (入门 / 进阶 / 资深) → second badge
- `prerequisites: [slug1, slug2]` → "建议先读" box with resolved links
- `hide_badges: true` → opt this page out entirely

Injected immediately after the first H1 of the markdown body.
"""

from __future__ import annotations

import re

TYPE_TO_KIND = {
    "concept": "explanation",
    "system": "explanation",
    "comparison": "reference",
    "scenario": "how-to",
    "learning-path": "tutorial",
    "tutorial": "tutorial",
    "adr": "reference",
    "paper-note": "reference",
    "reference": "reference",
    "how-to": "how-to",
    "explanation": "explanation",
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


def _find_file_by_slug(files, slug: str):
    """Resolve a slug to a files.File. Tries several match patterns."""
    slug = slug.strip().replace("\\", "/")
    for f in files:
        sp = f.src_path.replace("\\", "/")
        if sp == f"{slug}.md":
            return f
        if sp == f"{slug}/index.md":
            return f
        if sp.endswith(f"/{slug}.md"):
            return f
    # Fallback: basename match
    for f in files:
        sp = f.src_path.replace("\\", "/")
        if sp.rsplit("/", 1)[-1] == f"{slug}.md":
            return f
    return None


def _render_prerequisites(prerequisites, page, files):
    if not prerequisites:
        return ""
    items = []
    for p in prerequisites:
        file_obj = _find_file_by_slug(files, p)
        if file_obj is None:
            items.append(f"<li><code>{p}</code> <em>（未找到对应页）</em></li>")
            continue
        try:
            rel = file_obj.url_relative_to(page.file)
        except Exception:
            rel = "/" + file_obj.url
        title = p
        if getattr(file_obj, "page", None) is not None:
            pmeta = getattr(file_obj.page, "meta", None) or {}
            title = pmeta.get("title") or p
        items.append(f'<li><a href="{rel}">{title}</a></li>')
    body = "".join(items)
    return (
        '<div class="admonition note" style="margin:0.6em 0 1.4em 0;">'
        '<p class="admonition-title">建议先读</p>'
        f'<ul style="margin:0.2em 0 0.2em 1.5em;">{body}</ul>'
        "</div>\n"
    )


def on_page_markdown(markdown, page, config, files, **kwargs):
    meta = page.meta or {}

    if meta.get("hide_badges"):
        return markdown

    # --- Kind / Depth badges ---
    kind = meta.get("kind")
    type_ = meta.get("type")
    if not kind and type_:
        kind = TYPE_TO_KIND.get(str(type_))

    depth = meta.get("depth")

    badge_parts = []
    if kind and kind in KIND_LABEL:
        badge_parts.append(_badge(KIND_LABEL[kind], KIND_COLOR[kind]))
    if depth:
        lbl, color = DEPTH_LABEL.get(str(depth), (str(depth), "#546e7a"))
        badge_parts.append(_badge(lbl, color))

    badge_block = ""
    if badge_parts:
        badge_block = (
            '<div class="page-badges" style="margin:0.2em 0 1em 0;">'
            + "".join(badge_parts)
            + "</div>\n"
        )

    # --- Prerequisites block ---
    prereq_raw = meta.get("prerequisites") or []
    if isinstance(prereq_raw, str):
        prereq_raw = [prereq_raw]
    prereq_block = _render_prerequisites(prereq_raw, page, files)

    if not badge_block and not prereq_block:
        return markdown

    # --- Inject after first H1 ---
    pattern = re.compile(r"^(#\s+.*?)(\r?\n)", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return markdown

    insert_at = match.end()
    injection = "\n" + badge_block + prereq_block
    return markdown[:insert_at] + injection + markdown[insert_at:]
