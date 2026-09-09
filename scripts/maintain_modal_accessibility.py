#!/usr/bin/env python3
"""Keep the app detail modal exposed as one accessible dialog."""

from pathlib import Path


html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

legacy = '<div class="modal-container" tabindex="-1">'
labelled = (
    '<div class="modal-container" tabindex="-1" role="dialog" '
    'aria-modal="true" aria-labelledby="modal-title">'
)
accessible = (
    '<div class="modal-container" tabindex="-1" role="dialog" '
    'aria-modal="true" aria-labelledby="modal-title" aria-describedby="modal-desc">'
)

if legacy in html:
    html = html.replace(legacy, accessible, 1)
elif labelled in html:
    html = html.replace(labelled, accessible, 1)
elif accessible not in html:
    raise SystemExit("Could not find the app modal container")

required_html = (
    'role="dialog"',
    'aria-modal="true"',
    'aria-labelledby="modal-title"',
    'aria-describedby="modal-desc"',
    'id="modal-title"',
    'id="modal-desc"',
)
for marker in required_html:
    if marker not in html:
        raise SystemExit(f"App modal is missing accessible dialog marker: {marker}")

if html.count(accessible) != 1:
    raise SystemExit("Expected exactly one accessible app modal container")

html_path.write_text(html, encoding="utf-8")

js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

runtime_attributes = (
    ("role", "dialog"),
    ("aria-modal", "true"),
    ("aria-labelledby", "modal-title"),
    ("aria-describedby", "modal-desc"),
)
for attribute, value in runtime_attributes:
    overlay = f"    modal.setAttribute('{attribute}', '{value}');"
    dialog = f"    dialog?.setAttribute('{attribute}', '{value}');"
    if overlay in js:
        js = js.replace(overlay, dialog, 1)
    elif dialog not in js:
        raise SystemExit(f"Could not find runtime app dialog attribute: {attribute}")

if "modal.setAttribute('role', 'dialog');" in js:
    raise SystemExit("App modal overlay must not expose duplicate dialog semantics")
for attribute, value in runtime_attributes:
    marker = f"dialog?.setAttribute('{attribute}', '{value}');"
    if marker not in js:
        raise SystemExit(f"App modal container is missing runtime attribute: {attribute}")

js_path.write_text(js, encoding="utf-8")
