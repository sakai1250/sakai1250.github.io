#!/usr/bin/env python3
"""Prepare current markup for legacy header maintenance transforms.

Stable deep-link IDs are restored later by maintain_tab_deep_links.py. The
language/theme maintenance scripts also restore active-language action names
after maintain_header_controls.py runs. This compatibility step keeps the
legacy header transform independent from those newer generated states.
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

HEADER_CONTROL_COMPATIBILITY = {
    'aria-label="英語に切り替え"': 'aria-label="Switch to English / 英語に切り替え"',
    'aria-label="ライトテーマに切り替え"': 'aria-label="Switch to light theme / ライトテーマに切り替え"',
}


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    for section_id in STATIC_SECTION_IDS:
        marker = f'<section class="section-card" id="{section_id}">'
        if marker in html:
            html = html.replace(marker, '<section class="section-card">', 1)

    # maintain_header_controls.py predates the active-language action labels and
    # recognizes its historical bilingual states. Normalize only for that
    # maintenance stage; the dedicated language/theme transforms run later and
    # restore the visitor-facing localized names before generated files settle.
    for localized, legacy in HEADER_CONTROL_COMPATIBILITY.items():
        if localized in html:
            html = html.replace(localized, legacy, 1)

    INDEX.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
