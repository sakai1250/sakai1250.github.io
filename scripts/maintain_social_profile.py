#!/usr/bin/env python3
"""Synchronize social and structured profile metadata with CV-derived values."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from cv_profile import read_cv_section_bullets
from profile_descriptions import build_social_description


def replace_meta(text: str, pattern: re.Pattern[str], replacement: str, label: str) -> str:
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Could not find exactly one {label} metadata tag")
    return text


def sync_knows_about(text: str, research_areas: list[str]) -> str:
    serialized = json.dumps(research_areas, ensure_ascii=False)
    existing = re.compile(r'    "knowsAbout": \[[^\n]*\],\n')
    if existing.search(text):
        return existing.sub(f'    "knowsAbout": {serialized},\n', text, count=1)

    image_line = re.compile(r'(    "image": "[^"]+",\n)')
    text, count = image_line.subn(
        rf'\1    "knowsAbout": {serialized},\n', text, count=1
    )
    if count != 1:
        raise SystemExit("Could not find exactly one Person JSON-LD image field")
    return text


def main() -> None:
    path = Path("index.html")
    text = path.read_text(encoding="utf-8")
    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    social_description = html.escape(build_social_description(cv_text), quote=True)
    research_areas = read_cv_section_bullets(cv_text, "RESEARCH AREAS")

    text = replace_meta(
        text,
        re.compile(r'<meta name="twitter:description" content="[^"]*">'),
        f'<meta name="twitter:description" content="{social_description}">',
        "Twitter description",
    )
    text = sync_knows_about(text, research_areas)

    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
