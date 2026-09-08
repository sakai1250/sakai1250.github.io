#!/usr/bin/env python3
"""Synchronize social-profile description metadata with the CV role header."""

from __future__ import annotations

import html
import re
from pathlib import Path


RESEARCH_FOCUS = "Computer Vision, Continual Learning, and Multi-View Tracking"


def read_cv_social_profile(cv_text: str) -> tuple[list[str], str]:
    lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
    if len(lines) < 5 or " | " not in lines[3]:
        raise SystemExit("assets/cv.txt is missing the expected role and affiliation header")

    roles = [role.strip() for role in lines[3].split("|") if role.strip()]
    affiliation = lines[4].split(",", 1)[0].strip()
    if not roles or not affiliation:
        raise SystemExit("assets/cv.txt has an incomplete role or affiliation header")
    return roles, affiliation


def build_social_description(cv_text: str) -> str:
    roles, affiliation = read_cv_social_profile(cv_text)
    visible_roles = roles[:2]
    role_phrase = " and ".join(visible_roles)
    return f"{role_phrase} at {affiliation} researching {RESEARCH_FOCUS}."


def main() -> None:
    path = Path("index.html")
    text = path.read_text(encoding="utf-8")
    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    description = html.escape(build_social_description(cv_text), quote=True)

    pattern = re.compile(r'<meta name="twitter:description" content="[^"]*">')
    replacement = f'<meta name="twitter:description" content="{description}">'
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise SystemExit("Could not find exactly one Twitter description metadata tag")

    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
