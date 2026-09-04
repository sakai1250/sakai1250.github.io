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
    if re.search(r'\shidden(?:\s*=\s*(?:"hidden"|""|hidden))?$', start_tag):
        return source
    if re.search(r'\shidden(?:\s*=\s*(?:"hidden"|""|hidden))?(?:\s|$)', start_tag):
        return source
    replacement = f"{start_tag} hidden{match.group(2)}"
    return source[:match.start()] + replacement + source[match.end():]


html = ensure_hidden_attribute(html, "toc-fab")
html = ensure_hidden_attribute(html, "toc-menu")
HTML_PATH.write_text(html, encoding="utf-8")

js = JS_PATH.read_text(encoding="utf-8")
old_ready = """        updateTOC();
        updateSectionTabs();
    }
}
"""
new_ready = """        updateTOC();
        updateSectionTabs();
        fab.hidden = false;
        menu.hidden = false;
    }
}
"""

if new_ready not in js:
    if old_ready not in js:
        raise SystemExit("Could not find expected TOC initialization completion block")
    js = js.replace(old_ready, new_ready, 1)

if "fab.hidden = false;" not in js or "menu.hidden = false;" not in js:
    raise SystemExit("TOC controls are not revealed after runtime initialization")

JS_PATH.write_text(js, encoding="utf-8")
