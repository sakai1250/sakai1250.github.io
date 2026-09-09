#!/usr/bin/env python3
"""Validate language-aware accessible names for utility controls."""

from pathlib import Path


index_text = Path("index.html").read_text(encoding="utf-8")
main_text = Path("main.js").read_text(encoding="utf-8")

expected = (
    'id="back-to-top" type="button" aria-label="トップへ戻る" data-ja-aria-label="トップへ戻る" data-en-aria-label="Back to top"',
    'id="toc-fab" type="button" aria-label="目次" data-ja-aria-label="目次" data-en-aria-label="Table of contents"',
    'class="modal-close" aria-label="閉じる" data-ja-aria-label="閉じる" data-en-aria-label="Close"',
)
for marker in expected:
    if marker not in index_text:
        raise SystemExit(f"Missing localized utility control marker: {marker}")

for mixed in (
    "Back to top / トップへ戻る",
    "Table of contents / 目次",
    "Close / 閉じる",
):
    if mixed in index_text:
        raise SystemExit(f"Mixed-language utility control label remains: {mixed}")

runtime_markers = (
    "document.querySelectorAll('[data-ja-aria-label][data-en-aria-label]')",
    "window.addEventListener('portfolio:languagechange', sync)",
)
for marker in runtime_markers:
    if marker not in main_text:
        raise SystemExit(f"Missing language-change synchronization marker: {marker}")

print("OK: utility control accessible names follow the active site language")
