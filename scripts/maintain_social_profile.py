#!/usr/bin/env python3
"""Synchronize Twitter profile metadata with the CV-derived description."""

from __future__ import annotations

import html
import re
from pathlib import Path

from profile_descriptions import build_social_description


def replace_meta(text: str, pattern: re.Pattern[str], replacement: str, label: str) -> str:
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit(f"Could not find exactly one {label} metadata tag")
    return text


def main() -> None:
    path = Path("index.html")
    text = path.read_text(encoding="utf-8")
    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    social_description = html.escape(build_social_description(cv_text), quote=True)

    text = replace_meta(
        text,
        re.compile(r'<meta name="twitter:description" content="[^"]*">'),
        f'<meta name="twitter:description" content="{social_description}">',
        "Twitter description",
    )

    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
