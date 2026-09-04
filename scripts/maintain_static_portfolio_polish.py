#!/usr/bin/env python3
"""Keep portfolio header priority and layout in static HTML/CSS, not runtime JS."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLE = ROOT / "style.css"
EFFECTS = ROOT / "effects.js"

DESKTOP_STATS_RULE = """

@media (min-width: 769px) {
  .header-stats {
    transform: translate(-50%, -8px);
  }
}
"""


def update_index() -> None:
    text = INDEX.read_text(encoding="utf-8")
    old = text

    text = text.replace(
        'href="assets/cv.pdf" target="_blank" class="header-btn" rel="noopener noreferrer"',
        'href="assets/cv.pdf" target="_blank" class="header-btn primary" rel="noopener noreferrer"',
        1,
    )
    text = text.replace(
        'href="https://github.com/sakai1250" target="_blank" class="header-btn primary" rel="noopener noreferrer"',
        'href="https://github.com/sakai1250" target="_blank" class="header-btn" rel="noopener noreferrer"',
        1,
    )

    if 'href="assets/cv.pdf" target="_blank" class="header-btn primary"' not in text:
        raise SystemExit("CV header action was not made primary")
    if 'href="https://github.com/sakai1250" target="_blank" class="header-btn primary"' in text:
        raise SystemExit("GitHub header action is still primary")

    if text != old:
        INDEX.write_text(text, encoding="utf-8")


def update_style() -> None:
    text = STYLE.read_text(encoding="utf-8")
    if DESKTOP_STATS_RULE.strip() not in text:
        text = text.rstrip() + DESKTOP_STATS_RULE + "\n"
        STYLE.write_text(text, encoding="utf-8")


def update_effects() -> None:
    text = EFFECTS.read_text(encoding="utf-8")
    old = text

    text = re.sub(
        r"\nfunction initPortfolioPolish\(\) \{.*?\n\}\n\n"
        r"if \(document\.readyState === 'loading'\) \{.*?\n\} else \{\n"
        r"    initPortfolioPolish\(\);\n\}\n",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )

    if "initPortfolioPolish" in text or "portfolio-polish-style" in text:
        raise SystemExit("Runtime portfolio polish still remains in effects.js")

    if text != old:
        EFFECTS.write_text(text, encoding="utf-8")


def main() -> None:
    update_index()
    update_style()
    update_effects()


if __name__ == "__main__":
    main()
