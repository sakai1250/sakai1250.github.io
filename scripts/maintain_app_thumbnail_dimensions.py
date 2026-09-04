#!/usr/bin/env python3
"""Keep app thumbnails dimensioned so lazy external images do not shift layout."""

from __future__ import annotations

import re
from pathlib import Path


path = Path("index.html")
text = path.read_text(encoding="utf-8")
pattern = re.compile(r'<img\b[^>]*\bclass="app-thumb"[^>]*>')


def add_intrinsic_size(match: re.Match[str]) -> str:
    tag = match.group(0)
    has_width = re.search(r'\bwidth="\d+"', tag) is not None
    has_height = re.search(r'\bheight="\d+"', tag) is not None
    if has_width and has_height:
        return tag
    if has_width != has_height:
        raise SystemExit(f"App thumbnail has only one intrinsic dimension: {tag}")
    if ' loading="lazy"' not in tag:
        raise SystemExit(f"App thumbnail is missing lazy loading marker: {tag}")
    return tag.replace(
        ' loading="lazy"',
        ' width="82" height="82" loading="lazy"',
        1,
    )


matches = pattern.findall(text)
if not matches:
    raise SystemExit("Could not find app thumbnails")

text = pattern.sub(add_intrinsic_size, text)

for tag in pattern.findall(text):
    if 'width="82"' not in tag or 'height="82"' not in tag:
        raise SystemExit(f"App thumbnail intrinsic size drifted: {tag}")

path.write_text(text, encoding="utf-8")
