#!/usr/bin/env python3
"""Keep the app detail modal exposed as an accessible dialog."""

from pathlib import Path


path = Path("index.html")
text = path.read_text(encoding="utf-8")

legacy = '<div class="modal-container" tabindex="-1">'
accessible = (
    '<div class="modal-container" tabindex="-1" role="dialog" '
    'aria-modal="true" aria-labelledby="modal-title">'
)

if legacy in text:
    text = text.replace(legacy, accessible, 1)
elif accessible not in text:
    raise SystemExit("Could not find the app modal container")

required = (
    'role="dialog"',
    'aria-modal="true"',
    'aria-labelledby="modal-title"',
    'id="modal-title"',
)
for marker in required:
    if marker not in text:
        raise SystemExit(f"App modal is missing accessible dialog marker: {marker}")

if text.count(accessible) != 1:
    raise SystemExit("Expected exactly one accessible app modal container")

path.write_text(text, encoding="utf-8")
