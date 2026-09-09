#!/usr/bin/env python3
"""Keep the app detail modal exposed as one accessible dialog."""

from pathlib import Path
import re


html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

inner_plain = '<div class="modal-container" tabindex="-1">'
inner_labelled = (
    '<div class="modal-container" tabindex="-1" role="dialog" '
    'aria-modal="true" aria-labelledby="modal-title">'
)
inner_accessible = (
    '<div class="modal-container" tabindex="-1" role="dialog" '
    'aria-modal="true" aria-labelledby="modal-title" aria-describedby="modal-desc">'
)

if inner_accessible in html:
    html = html.replace(inner_accessible, inner_plain, 1)
elif inner_labelled in html:
    html = html.replace(inner_labelled, inner_plain, 1)
elif inner_plain not in html:
    raise SystemExit("Could not find the app modal container")

outer_pattern = re.compile(r'<div id="app-modal" class="modal-overlay"[^>]*>')
outer_match = outer_pattern.search(html)
if not outer_match:
    raise SystemExit("Could not find the app modal overlay")

outer_accessible = (
    '<div id="app-modal" class="modal-overlay" aria-hidden="true" role="dialog" '
    'aria-modal="true" aria-labelledby="modal-title" aria-describedby="modal-desc">'
)
html = html[:outer_match.start()] + outer_accessible + html[outer_match.end():]

if html.count('role="dialog"') != 1:
    raise SystemExit("Expected exactly one dialog role in the app modal markup")
for marker in (
    'aria-modal="true"',
    'aria-labelledby="modal-title"',
    'aria-describedby="modal-desc"',
    'id="modal-title"',
    'id="modal-desc"',
):
    if marker not in html:
        raise SystemExit(f"App modal is missing accessible dialog marker: {marker}")

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
    dialog = f"    dialog?.setAttribute('{attribute}', '{value}');"
    overlay = f"    modal.setAttribute('{attribute}', '{value}');"
    if dialog in js:
        js = js.replace(dialog, overlay, 1)
    elif overlay not in js:
        raise SystemExit(f"Could not find runtime app dialog attribute: {attribute}")

for attribute, value in runtime_attributes:
    marker = f"modal.setAttribute('{attribute}', '{value}');"
    if marker not in js:
        raise SystemExit(f"App modal overlay is missing runtime attribute: {attribute}")
if "dialog?.setAttribute('role', 'dialog');" in js:
    raise SystemExit("App modal container must not expose duplicate dialog semantics")

js_path.write_text(js, encoding="utf-8")
