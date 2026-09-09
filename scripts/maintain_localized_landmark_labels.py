#!/usr/bin/env python3
"""Keep landmark and filter accessible names aligned with the active page language."""

from pathlib import Path


html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

label_replacements = {
    '<nav class="tab-nav header-tab-nav" aria-label="Research and engineering / 研究と開発">': (
        '<nav class="tab-nav header-tab-nav" aria-label="研究と開発" '
        'data-ja-aria-label="研究と開発" data-en-aria-label="Research and engineering">'
    ),
    '<div class="filter-row year-filter" role="group" aria-label="Filter research outputs by year / 研究業績を年度で絞り込む">': (
        '<div class="filter-row year-filter" role="group" aria-label="研究業績を年度で絞り込む" '
        'data-ja-aria-label="研究業績を年度で絞り込む" '
        'data-en-aria-label="Filter research outputs by year">'
    ),
    '<div class="filter-row" role="group" aria-label="Filter engineering work / 開発実績を絞り込む">': (
        '<div class="filter-row" role="group" aria-label="開発実績を絞り込む" '
        'data-ja-aria-label="開発実績を絞り込む" '
        'data-en-aria-label="Filter engineering work">'
    ),
    '<nav id="section-tab-nav" class="section-tab-nav" aria-label="Portfolio sections / ポートフォリオ内の項目"></nav>': (
        '<nav id="section-tab-nav" class="section-tab-nav" aria-label="ポートフォリオ内の項目" '
        'data-ja-aria-label="ポートフォリオ内の項目" '
        'data-en-aria-label="Portfolio sections"></nav>'
    ),
}

for mixed, localized in label_replacements.items():
    if localized in html:
        continue
    if mixed not in html:
        raise SystemExit(f"Could not find landmark label to localize: {mixed}")
    html = html.replace(mixed, localized, 1)

for mixed in label_replacements:
    if mixed in html:
        raise SystemExit(f"Mixed-language accessible name remains: {mixed}")

html_path.write_text(html, encoding="utf-8")

js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

safe_init_anchor = "    safeInit(initLanguage, 'Language');\n"
safe_init_line = "    safeInit(initLocalizedAccessibleNames, 'LocalizedAccessibleNames');\n"
if safe_init_line not in js:
    if safe_init_anchor not in js:
        raise SystemExit("Could not find language initialization anchor")
    js = js.replace(safe_init_anchor, safe_init_anchor + safe_init_line, 1)

function_anchor = "function initContextualShareLink() {\n"
localized_function = """function initLocalizedAccessibleNames() {
    const sync = () => {
        const lang = document.documentElement.dataset.lang === 'en' ? 'en' : 'ja';
        document.querySelectorAll('[data-ja-aria-label][data-en-aria-label]').forEach(element => {
            const label = lang === 'en' ? element.dataset.enAriaLabel : element.dataset.jaAriaLabel;
            if (label) element.setAttribute('aria-label', label);
        });
    };

    window.addEventListener('portfolio:languagechange', sync);
    sync();
}

"""
if localized_function not in js:
    if function_anchor not in js:
        raise SystemExit("Could not find JavaScript function insertion anchor")
    js = js.replace(function_anchor, localized_function + function_anchor, 1)

required_js = (
    "safeInit(initLocalizedAccessibleNames, 'LocalizedAccessibleNames')",
    "document.querySelectorAll('[data-ja-aria-label][data-en-aria-label]')",
    "window.addEventListener('portfolio:languagechange', sync)",
    "element.dataset.enAriaLabel",
    "element.dataset.jaAriaLabel",
)
missing = [marker for marker in required_js if marker not in js]
if missing:
    raise SystemExit(f"Localized accessible-name synchronization is incomplete: {missing}")

js_path.write_text(js, encoding="utf-8")
