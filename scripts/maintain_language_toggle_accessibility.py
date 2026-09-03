#!/usr/bin/env python3
"""Keep language choice and toggle accessibility aligned with visitor intent."""

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

language_bootstrap = """  <!-- Language Initialization: Resolve Saved or Browser Preference Before Paint -->
  <script>
    (function () {
      let savedLanguage = null;
      try { savedLanguage = localStorage.getItem('lang'); } catch {}
      const browserLanguage = (navigator.languages?.[0] || navigator.language || 'ja').toLowerCase();
      const language = savedLanguage || (browserLanguage.startsWith('en') ? 'en' : 'ja');
      document.documentElement.setAttribute('data-lang', language);
      document.documentElement.lang = language;
      window.addEventListener('DOMContentLoaded', () => {
        const languageButton = document.getElementById('lang-toggle');
        if (languageButton) {
          languageButton.setAttribute(
            'aria-label',
            language === 'ja'
              ? 'Switch to English / 英語に切り替え'
              : 'Switch to Japanese / 日本語に切り替え'
          );
        }
      });
    })();
  </script>
"""
theme_anchor = "  <!-- Theme Initialization: Prevent Flash of Incorrect Theme -->\n"
if language_bootstrap not in index_text:
    if theme_anchor not in index_text:
        raise SystemExit("Could not find theme bootstrap anchor for language initialization")
    index_text = index_text.replace(theme_anchor, language_bootstrap + theme_anchor, 1)

if index_text.count(language_bootstrap) != 1:
    raise SystemExit("Language bootstrap must appear exactly once")

index_path.write_text(index_text, encoding="utf-8")

main_path = Path("main.js")
main_text = main_path.read_text(encoding="utf-8")

legacy_anchor = """        safeStorageSet('lang', l);
        const s = document.getElementById('search');"""
current_block = """        if (persist) safeStorageSet('lang', l);

        if (btn) {
            btn.setAttribute(
                'aria-label',
                l === 'ja'
                    ? 'Switch to English / 英語に切り替え'
                    : 'Switch to Japanese / 日本語に切り替え'
            );
        }
        const s = document.getElementById('search');"""
previous_accessible_block = """        safeStorageSet('lang', l);

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
    if previous_accessible_block in main_text:
        main_text = main_text.replace(previous_accessible_block, current_block, 1)
    elif legacy_anchor in main_text:
        main_text = main_text.replace(legacy_anchor, current_block, 1)
    else:
        raise SystemExit("Could not find language toggle state handling")

legacy_set_signature = "    const set = (l) => {"
current_set_signature = "    const set = (l, persist = false) => {"
if legacy_set_signature in main_text:
    main_text = main_text.replace(legacy_set_signature, current_set_signature, 1)
elif current_set_signature not in main_text:
    raise SystemExit("Could not find language setter")

legacy_click = "    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-lang') === 'ja' ? 'en' : 'ja'));"
current_click = "    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-lang') === 'ja' ? 'en' : 'ja', true));"
if legacy_click in main_text:
    main_text = main_text.replace(legacy_click, current_click, 1)
elif current_click not in main_text:
    raise SystemExit("Could not find explicit language toggle persistence")

legacy_initial = "    set(safeStorageGet('lang') || 'ja');"
current_initial = """    const browserLanguage = (navigator.languages?.[0] || navigator.language || 'ja').toLowerCase();
    set(safeStorageGet('lang') || (browserLanguage.startsWith('en') ? 'en' : 'ja'));"""
if legacy_initial in main_text:
    main_text = main_text.replace(legacy_initial, current_initial, 1)
elif current_initial not in main_text:
    raise SystemExit("Could not find browser-aware initial language selection")

if main_text.count(current_block) != 1:
    raise SystemExit("Language toggle must have exactly one accessible action block")

for expected in (
    "Switch to English / 英語に切り替え",
    "Switch to Japanese / 日本語に切り替え",
    "if (persist) safeStorageSet('lang', l);",
    "browserLanguage.startsWith('en') ? 'en' : 'ja'",
    "document.documentElement.lang = l;",
):
    if expected not in main_text:
        raise SystemExit(f"Missing language preference behavior: {expected}")

for expected in (
    "document.documentElement.setAttribute('data-lang', language);",
    "document.documentElement.lang = language;",
    "browserLanguage.startsWith('en') ? 'en' : 'ja'",
    "const languageButton = document.getElementById('lang-toggle');",
    "language === 'ja'",
    "Switch to Japanese / 日本語に切り替え",
):
    if expected not in index_text:
        raise SystemExit(f"Missing initial language bootstrap behavior: {expected}")

if "        safeStorageSet('lang', l);" in main_text:
    raise SystemExit("Initial language application must not persist without an explicit visitor choice")

main_path.write_text(main_text, encoding="utf-8")
