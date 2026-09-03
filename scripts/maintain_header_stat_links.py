#!/usr/bin/env python3
"""Keep header portfolio counts linked to their corresponding evidence sections."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLE = ROOT / "style.css"

LINKS = {
    "stat-papers": "#research-research-achievements",
    "stat-awards": "#research-awards",
    "stat-apps": "#engineer-my-apps-and-services",
}


def link_stat_block(text: str, stat_id: str, href: str) -> str:
    already_linked = re.compile(
        rf'<a class="stat-item" href="{re.escape(href)}">\s*'
        rf'<div class="stat-value" id="{re.escape(stat_id)}">.*?</div>\s*'
        r'<div class="stat-label">.*?</div>\s*</a>',
        re.S,
    )
    if already_linked.search(text):
        return text

    block = re.compile(
        r'<div class="stat-item">\s*'
        rf'(<div class="stat-value" id="{re.escape(stat_id)}">.*?</div>\s*'
        r'<div class="stat-label">.*?</div>)\s*</div>',
        re.S,
    )
    replacement = rf'<a class="stat-item" href="{href}">\n              \1\n            </a>'
    text, count = block.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Could not maintain the stat-item wrapper for {stat_id}")
    return text


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    for stat_id, href in LINKS.items():
        html = link_stat_block(html, stat_id, href)
    INDEX.write_text(html, encoding="utf-8")

    css = STYLE.read_text(encoding="utf-8")
    marker = "/* Header stat navigation */"
    rules = """

/* Header stat navigation */
.stat-item[href] {
  color: inherit;
  text-decoration: none;
}

.stat-item[href]:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 4px;
  border-radius: 4px;
}
"""
    if marker not in css:
        css = css.rstrip() + rules + "\n"
        STYLE.write_text(css, encoding="utf-8")

    current = INDEX.read_text(encoding="utf-8")
    for stat_id, href in LINKS.items():
        target_id = href.removeprefix("#")
        if f'id="{target_id}"' not in current:
            raise SystemExit(f"Header stat target is not static: {target_id}")
        if not re.search(
            rf'<a class="stat-item" href="{re.escape(href)}">.*?id="{re.escape(stat_id)}"',
            current,
            re.S,
        ):
            raise SystemExit(f"Header stat link was not maintained: {stat_id}")


if __name__ == "__main__":
    main()
