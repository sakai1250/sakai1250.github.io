#!/usr/bin/env python3
"""Keep the theme toggle's accessible action aligned with theme and language."""

from pathlib import Path


path = Path("main.js")
text = path.read_text(encoding="utf-8")

helper = """    const syncAccessibleName = (theme) => {
        if (!btn) return;
        btn.removeAttribute('aria-pressed');
        const lang = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ja';
        const label = theme === 'dark'
            ? (lang === 'en' ? 'Switch to light theme' : 'ライトテーマに切り替え')
            : (lang === 'en' ? 'Switch to dark theme' : 'ダークテーマに切り替え');
        btn.setAttribute('aria-label', label);
    };
"""
helper_anchor = "    const icon = document.getElementById('theme-icon');\n"
if helper not in text:
    if helper_anchor not in text:
        raise SystemExit("Could not find theme toggle helper anchor")
    text = text.replace(helper_anchor, helper_anchor + helper, 1)

legacy_blocks = (
    """        if (btn) {
            btn.removeAttribute('aria-pressed');
            btn.setAttribute(
                'aria-label',
                t === 'dark'
                    ? 'Switch to light theme / ライトテーマに切り替え'
                    : 'Switch to dark theme / ダークテーマに切り替え'
            );
        }""",
    "        if (btn) btn.setAttribute('aria-pressed', String(t === 'dark'));",
)
current_action = "        syncAccessibleName(t);"
if current_action not in text:
    for legacy in legacy_blocks:
        if legacy in text:
            text = text.replace(legacy, current_action, 1)
            break
    else:
        raise SystemExit("Could not find expected theme toggle state handling")

listener = (
    "    window.addEventListener('portfolio:languagechange', () => "
    "syncAccessibleName(document.documentElement.getAttribute('data-theme') || 'dark'));\n"
)
listener_anchor = "    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true, true));\n"
if listener not in text:
    if listener_anchor not in text:
        raise SystemExit("Could not find theme toggle listener anchor")
    text = text.replace(listener_anchor, listener_anchor + listener, 1)

for legacy in legacy_blocks:
    if legacy in text:
        raise SystemExit("Theme toggle still exposes legacy mixed-language state handling")
if text.count(helper) != 1 or text.count(current_action) != 1 or text.count(listener) != 1:
    raise SystemExit("Theme toggle language-aware accessible-name handling must appear exactly once")

for expected in (
    "Switch to light theme",
    "Switch to dark theme",
    "ライトテーマに切り替え",
    "ダークテーマに切り替え",
    "portfolio:languagechange",
):
    if expected not in text:
        raise SystemExit(f"Missing theme toggle accessible action: {expected}")

path.write_text(text, encoding="utf-8")

index_path = Path("index.html")
index_text = index_path.read_text(encoding="utf-8")
initial_label = 'aria-label="ライトテーマに切り替え"'
legacy_labels = (
    'aria-label="Switch theme / テーマ切り替え"',
    'aria-label="Switch to light theme / ライトテーマに切り替え"',
)
if initial_label not in index_text:
    for legacy in legacy_labels:
        if legacy in index_text:
            index_text = index_text.replace(legacy, initial_label, 1)
            break
    else:
        raise SystemExit("Could not find expected initial theme toggle accessible name")

legacy_bootstrap = """      const theme = savedTheme || systemTheme;
      document.documentElement.setAttribute('data-theme', theme);"""
bilingual_bootstrap = """      const theme = savedTheme || systemTheme;
      document.documentElement.setAttribute('data-theme', theme);
      window.addEventListener('DOMContentLoaded', () => {
        const themeButton = document.getElementById('theme-toggle');
        const themeIcon = document.getElementById('theme-icon');
        if (themeButton) {
          themeButton.setAttribute(
            'aria-label',
            theme === 'dark'
              ? 'Switch to light theme / ライトテーマに切り替え'
              : 'Switch to dark theme / ダークテーマに切り替え'
          );
        }
        if (themeIcon) themeIcon.textContent = theme === 'dark' ? '☾' : '☀︎';
      });"""
current_bootstrap = """      const theme = savedTheme || systemTheme;
      document.documentElement.setAttribute('data-theme', theme);
      window.addEventListener('DOMContentLoaded', () => {
        const themeButton = document.getElementById('theme-toggle');
        const themeIcon = document.getElementById('theme-icon');
        const language = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ja';
        if (themeButton) {
          const label = theme === 'dark'
            ? (language === 'en' ? 'Switch to light theme' : 'ライトテーマに切り替え')
            : (language === 'en' ? 'Switch to dark theme' : 'ダークテーマに切り替え');
          themeButton.setAttribute('aria-label', label);
        }
        if (themeIcon) themeIcon.textContent = theme === 'dark' ? '☾' : '☀︎';
      });"""

if current_bootstrap in index_text:
    pass
elif bilingual_bootstrap in index_text:
    index_text = index_text.replace(bilingual_bootstrap, current_bootstrap, 1)
elif legacy_bootstrap in index_text:
    index_text = index_text.replace(legacy_bootstrap, current_bootstrap, 1)
else:
    raise SystemExit("Could not find expected theme bootstrap")

for legacy in legacy_labels:
    if legacy in index_text:
        raise SystemExit("Initial theme toggle still has a mixed-language accessible name")
if index_text.count(initial_label) != 1:
    raise SystemExit("Initial theme toggle must have exactly one Japanese fallback action label")
if index_text.count(current_bootstrap) != 1:
    raise SystemExit("Theme bootstrap must align the initial action exactly once")

index_path.write_text(index_text, encoding="utf-8")
