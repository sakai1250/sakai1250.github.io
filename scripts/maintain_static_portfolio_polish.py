#!/usr/bin/env python3
"""Keep portfolio header priority and layout in static HTML/CSS, not runtime JS."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLE = ROOT / "style.css"
MAIN = ROOT / "main.js"
README = ROOT / "README.md"
EFFECTS = ROOT / "effects.js"

DESKTOP_STATS_RULE = """

@media (min-width: 769px) {
  .header-stats {
    transform: translate(-50%, -8px);
  }
}
"""

CURSOR_STYLE = """
.cursor {
  width: 1px;
  height: 1.05em;
  margin-left: 6px;
  background: var(--accent);
  animation: blink 1.05s step-end infinite;
}

@keyframes blink { 50% { opacity: 0; } }
"""

OBSOLETE_HEADER_NAV = re.compile(
    r'\n\s*<!-- <div class="header-bottom">.*?</div> -->',
    flags=re.DOTALL,
)

OBSOLETE_BACKGROUND_NOTE = "  <!-- Neural Network Background Canvas will be injected here by JS -->\n\n"

SOCIAL_ICON_LABELS = ("x-icon", "linkedin-icon", "qiita-icon")


def hide_redundant_social_icon_labels(text: str) -> str:
    for icon_id in SOCIAL_ICON_LABELS:
        text = re.sub(
            rf'\s+role="img"\s+aria-labelledby="{re.escape(icon_id)}"',
            ' aria-hidden="true"',
            text,
            count=1,
        )
        text = re.sub(
            rf'\s+aria-labelledby="{re.escape(icon_id)}"\s+class="octicon"',
            ' class="octicon" aria-hidden="true"',
            text,
            count=1,
        )
        text = re.sub(
            rf'\s*<title id="{re.escape(icon_id)}">.*?</title>',
            '',
            text,
            count=1,
        )
    return text


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
    text = text.replace('<span class="cursor" aria-hidden="true"></span>', '', 1)
    text = re.sub(
        r'\n  <script src="effects\.js\?v=[^"]+"></script>',
        '',
        text,
        count=1,
    )
    text = OBSOLETE_HEADER_NAV.sub('', text, count=1)
    text = text.replace(OBSOLETE_BACKGROUND_NOTE, '', 1)
    text = hide_redundant_social_icon_labels(text)

    if 'href="assets/cv.pdf" target="_blank" class="header-btn primary"' not in text:
        raise SystemExit("CV header action was not made primary")
    if 'href="https://github.com/sakai1250" target="_blank" class="header-btn primary"' in text:
        raise SystemExit("GitHub header action is still primary")
    if 'effects.js' in text or 'class="cursor"' in text:
        raise SystemExit("obsolete effects.js runtime markup is still present")
    if 'header-bottom' in text or 'data-jump=' in text or 'header-hint' in text:
        raise SystemExit("obsolete commented header navigation is still present")
    if 'Neural Network Background Canvas' in text:
        raise SystemExit("obsolete background canvas note is still present")
    for icon_id in SOCIAL_ICON_LABELS:
        if f'aria-labelledby="{icon_id}"' in text or f'<title id="{icon_id}">' in text:
            raise SystemExit(f"redundant accessible label remains on {icon_id}")

    if text != old:
        INDEX.write_text(text, encoding="utf-8")


def update_style() -> None:
    text = STYLE.read_text(encoding="utf-8")
    old = text
    text = text.replace(CURSOR_STYLE, "")
    if DESKTOP_STATS_RULE.strip() not in text:
        text = text.rstrip() + DESKTOP_STATS_RULE + "\n"
    if '.cursor {' in text or '@keyframes blink' in text:
        raise SystemExit("obsolete typing cursor styles are still present")
    if text != old:
        STYLE.write_text(text, encoding="utf-8")


def update_main() -> None:
    text = MAIN.read_text(encoding="utf-8")
    old = text
    text = text.replace("\n    safeInit(window.initTypingEffect, 'TypingEffect');", "", 1)
    if 'initTypingEffect' in text:
        raise SystemExit("obsolete typing effect initialization is still present")
    if text != old:
        MAIN.write_text(text, encoding="utf-8")


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    old = text
    text = re.sub(
        r'^- `effects\.js` is a temporary compatibility shim.*\n',
        '',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if 'effects.js' in text:
        raise SystemExit("README still documents the obsolete effects.js shim")
    if text != old:
        README.write_text(text, encoding="utf-8")


def remove_effects_shim() -> None:
    if EFFECTS.exists():
        EFFECTS.unlink()


def main() -> None:
    update_index()
    update_style()
    update_main()
    update_readme()
    remove_effects_shim()


if __name__ == "__main__":
    main()
