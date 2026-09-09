#!/usr/bin/env python3
"""Normalize localized utility controls for legacy header maintenance."""

from pathlib import Path


path = Path("index.html")
text = path.read_text(encoding="utf-8")

localized_to_legacy = {
    'aria-label="トップへ戻る" data-ja-aria-label="トップへ戻る" data-en-aria-label="Back to top"':
        'aria-label="Back to top / トップへ戻る"',
    'aria-label="目次" data-ja-aria-label="目次" data-en-aria-label="Table of contents"':
        'aria-label="Table of contents / 目次"',
    'aria-label="閉じる" data-ja-aria-label="閉じる" data-en-aria-label="Close"':
        'aria-label="Close / 閉じる"',
}

for localized, legacy in localized_to_legacy.items():
    if localized in text:
        text = text.replace(localized, legacy, 1)
    elif legacy not in text:
        raise SystemExit(f"Could not find utility control maintenance marker: {legacy}")

path.write_text(text, encoding="utf-8")
