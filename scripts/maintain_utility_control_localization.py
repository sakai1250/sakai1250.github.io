#!/usr/bin/env python3
"""Keep utility control accessible names aligned with the active site language."""

from pathlib import Path


path = Path("index.html")
text = path.read_text(encoding="utf-8")

controls = {
    'aria-label="Back to top / トップへ戻る"':
        'aria-label="トップへ戻る" data-ja-aria-label="トップへ戻る" data-en-aria-label="Back to top"',
    'aria-label="Table of contents / 目次"':
        'aria-label="目次" data-ja-aria-label="目次" data-en-aria-label="Table of contents"',
    'aria-label="Close / 閉じる"':
        'aria-label="閉じる" data-ja-aria-label="閉じる" data-en-aria-label="Close"',
}

for legacy, localized in controls.items():
    if legacy in text:
        text = text.replace(legacy, localized, 1)
    elif localized not in text:
        raise SystemExit(f"Could not find utility control localization marker: {legacy}")

for mixed_label in controls:
    if mixed_label in text:
        raise SystemExit(f"Mixed-language utility control label remains: {mixed_label}")

path.write_text(text, encoding="utf-8")
