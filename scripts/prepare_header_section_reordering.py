#!/usr/bin/env python3
"""Prepare current markup for legacy header maintenance transforms.

Stable deep-link IDs are restored later by maintain_tab_deep_links.py. This
compatibility step only removes generated section IDs so the legacy header
transform can continue to locate sections by their historical structure.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

STATIC_SECTION_IDS = (
    "research-research-achievements",
    "research-education",
    "research-awards",
    "research-internship",
    "engineer-my-apps-and-services",
)


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    for section_id in STATIC_SECTION_IDS:
        marker = f'<section class="section-card" id="{section_id}">'
        if marker in html:
            html = html.replace(marker, '<section class="section-card">', 1)

    INDEX.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
