#!/usr/bin/env python3
"""Keep the theme toggle's accessible action aligned with the current theme."""

from pathlib import Path


path = Path("main.js")
text = path.read_text(encoding="utf-8")

legacy = "        if (btn) btn.setAttribute('aria-pressed', String(t === 'dark'));"
current = """        if (btn) {
            btn.removeAttribute('aria-pressed');
            btn.setAttribute(
                'aria-label',
                t === 'dark'
                    ? 'Switch to light theme / ライトテーマに切り替え'
                    : 'Switch to dark theme / ダークテーマに切り替え'
            );
        }"""

if legacy in text:
    text = text.replace(legacy, current, 1)
elif current not in text:
    raise SystemExit("Could not find expected theme toggle state handling")

if "if (btn) btn.setAttribute('aria-pressed'" in text:
    raise SystemExit("Theme toggle still exposes ambiguous aria-pressed state")

for expected in (
    "Switch to light theme / ライトテーマに切り替え",
    "Switch to dark theme / ダークテーマに切り替え",
):
    if expected not in text:
        raise SystemExit(f"Missing theme toggle accessible action: {expected}")

path.write_text(text, encoding="utf-8")
