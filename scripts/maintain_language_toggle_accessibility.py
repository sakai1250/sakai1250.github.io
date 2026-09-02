#!/usr/bin/env python3
"""Keep the language toggle's accessible action aligned with the current language."""

from pathlib import Path


index_path = Path("index.html")
index_text = index_path.read_text(encoding="utf-8")

legacy_buttons = (
    '<button class="header-btn" id="lang-toggle" type="button">',
    '<button class="header-btn" id="lang-toggle" type="button" aria-label="Switch language / 言語切り替え">',
)
current_button = (
    '<button class="header-btn" id="lang-toggle" type="button" '
    'aria-label="Switch to English / 英語に切り替え">'
)

for legacy in legacy_buttons:
    if legacy in index_text:
        index_text = index_text.replace(legacy, current_button, 1)
        break
else:
    if current_button not in index_text:
        raise SystemExit("Could not find expected language toggle button")

if index_text.count(current_button) != 1:
    raise SystemExit("Language toggle must have exactly one initial accessible action")

index_path.write_text(index_text, encoding="utf-8")

main_path = Path("main.js")
main_text = main_path.read_text(encoding="utf-8")

legacy_anchor = """        safeStorageSet('lang', l);
        const s = document.getElementById('search');"""
current_block = """        safeStorageSet('lang', l);

        if (btn) {
            btn.setAttribute(
                'aria-label',
                l === 'ja'
                    ? 'Switch to English / 英語に切り替え'
                    : 'Switch to Japanese / 日本語に切り替え'
            );
        }
        const s = document.getElementById('search');"""

if current_block not in main_text:
    if legacy_anchor not in main_text:
        raise SystemExit("Could not find language toggle state handling")
    main_text = main_text.replace(legacy_anchor, current_block, 1)

if main_text.count(current_block) != 1:
    raise SystemExit("Language toggle must have exactly one accessible action block")

for expected in (
    "Switch to English / 英語に切り替え",
    "Switch to Japanese / 日本語に切り替え",
):
    if expected not in main_text:
        raise SystemExit(f"Missing language toggle accessible action: {expected}")

main_path.write_text(main_text, encoding="utf-8")
