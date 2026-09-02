#!/usr/bin/env python3
"""Keep badge subsection headings semantically ordered without changing their appearance."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"
STYLE_PATH = ROOT / "style.css"

BADGE_IDS = ("badges-languages", "badges-frameworks", "badges-orgs")


def update_badge_heading(html: str, badge_id: str) -> tuple[str, bool]:
    pattern = re.compile(
        rf'(<div\s+class="badge-row"\s+id="{re.escape(badge_id)}"[^>]*>\s*)'
        r'<h[34]>(.*?)</h[34]>',
        re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find badge heading for #{badge_id}")

    replacement = f"{match.group(1)}<h3>{match.group(2)}</h3>"
    updated = html[: match.start()] + replacement + html[match.end() :]
    return updated, updated != html


def main() -> None:
    html = INDEX_PATH.read_text(encoding="utf-8")
    changed = False

    for badge_id in BADGE_IDS:
        html, did_change = update_badge_heading(html, badge_id)
        changed = changed or did_change

    style = STYLE_PATH.read_text(encoding="utf-8")
    if ".badge-row h4 {" in style:
        style = style.replace(".badge-row h4 {", ".badge-row h3 {", 1)
        changed = True
    elif ".badge-row h3 {" not in style:
        raise SystemExit("Could not find badge heading style selector")

    if changed:
        INDEX_PATH.write_text(html, encoding="utf-8")
        STYLE_PATH.write_text(style, encoding="utf-8")


if __name__ == "__main__":
    main()
