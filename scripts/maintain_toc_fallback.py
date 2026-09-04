#!/usr/bin/env python3
"""Keep JavaScript-only TOC controls hidden until runtime setup is complete."""

from pathlib import Path
import re


HTML_PATH = Path("index.html")
JS_PATH = Path("main.js")

html = HTML_PATH.read_text(encoding="utf-8")


def ensure_hidden_attribute(source: str, element_id: str) -> str:
    pattern = re.compile(rf'(<(?:button|div)\b[^>]*\bid="{re.escape(element_id)}"[^>]*)(>)')
    match = pattern.search(source)
    if not match:
        raise SystemExit(f"Could not find expected #{element_id} control")
    start_tag = match.group(1)
    if re.search(r'\shidden(?:\s*=\s*(?:"hidden"|""|hidden))?(?:\s|$)', start_tag):
        return source
    replacement = f"{start_tag} hidden{match.group(2)}"
    return source[:match.start()] + replacement + source[match.end():]


html = ensure_hidden_attribute(html, "toc-fab")
html = ensure_hidden_attribute(html, "toc-menu")
HTML_PATH.write_text(html, encoding="utf-8")

js = JS_PATH.read_text(encoding="utf-8")

# Keep initTOC itself compatible with the existing interaction maintenance.
# The wrapper reveals the controls only if initTOC returns successfully.
inline_reveal = """        updateTOC();
        updateSectionTabs();
        fab.hidden = false;
        menu.hidden = false;
    }
}
"""
plain_completion = """        updateTOC();
        updateSectionTabs();
    }
}
"""
if inline_reveal in js:
    js = js.replace(inline_reveal, plain_completion, 1)
elif plain_completion not in js:
    raise SystemExit("Could not find expected TOC initialization completion block")

plain_startup = "    safeInit(initTOC, 'TOC');"
enhanced_startup = "    safeInit(initTOCAndReveal, 'TOC');"
if plain_startup in js:
    js = js.replace(plain_startup, enhanced_startup, 1)
elif enhanced_startup not in js:
    raise SystemExit("Could not find expected TOC startup call")

wrapper = """
function initTOCAndReveal() {
    initTOC();
    const fab = document.getElementById('toc-fab');
    const menu = document.getElementById('toc-menu');
    if (!fab || !menu || !fab.hasAttribute('aria-controls')) return;
    fab.hidden = false;
    menu.hidden = false;
}

"""
wrapper_anchor = "function getSectionId(content, section, index) {"
if wrapper not in js:
    if wrapper_anchor not in js:
        raise SystemExit("Could not find expected TOC wrapper insertion point")
    js = js.replace(wrapper_anchor, wrapper + wrapper_anchor, 1)

required_markers = (
    enhanced_startup,
    "function initTOCAndReveal() {",
    "if (!fab || !menu || !fab.hasAttribute('aria-controls')) return;",
    "fab.hidden = false;",
    "menu.hidden = false;",
)
for marker in required_markers:
    if marker not in js:
        raise SystemExit(f"Missing TOC fallback runtime marker: {marker}")

JS_PATH.write_text(js, encoding="utf-8")
