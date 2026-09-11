#!/usr/bin/env python3
"""Synchronize social and search profile metadata with the CV role header."""

from __future__ import annotations

import html
import re
from pathlib import Path


RESEARCH_FOCUS = "Computer Vision, Continual Learning, and Multi-View Tracking"
SEARCH_RESEARCH_FOCUS = "Computer Vision、Continual Learning、Multi-View Tracking"
ROLE_LABELS_JA = {
    "Ph.D. Student": "博士後期課程",
}
AFFILIATION_LABELS_JA = {
    "Meijo University": "名城大学大学院",
}


def read_cv_social_profile(cv_text: str) -> tuple[list[str], str]:
    preamble = cv_text.split("\n\n", 1)[0]
    lines = [line.strip() for line in preamble.splitlines() if line.strip()]
    role_indexes = [index for index, line in enumerate(lines[:-1]) if " | " in line]
    if len(role_indexes) != 1:
        raise SystemExit("assets/cv.txt must contain exactly one role header followed by affiliation")

    role_index = role_indexes[0]
    roles = [role.strip() for role in lines[role_index].split("|") if role.strip()]
    affiliation = lines[role_index + 1].split(",", 1)[0].strip()
    if not roles or not affiliation or ":" in affiliation:
        raise SystemExit("assets/cv.txt has an incomplete role or affiliation header")
    return roles, affiliation


def build_social_description(cv_text: str) -> str:
    roles, affiliation = read_cv_social_profile(cv_text)
    visible_roles = roles[:2]
    role_phrase = " and ".join(visible_roles)
    return f"{role_phrase} at {affiliation} researching {RESEARCH_FOCUS}."


def build_search_description(cv_text: str) -> str:
    roles, affiliation = read_cv_social_profile(cv_text)
    visible_roles = roles[:2]
    localized_roles = [ROLE_LABELS_JA.get(role, role) for role in visible_roles]
    localized_affiliation = AFFILIATION_LABELS_JA.get(affiliation, affiliation)
    role_phrase = "・".join(localized_roles)
    return (
        f"{localized_affiliation} {role_phrase} 坂井泰吾のポートフォリオ。"
        f"{SEARCH_RESEARCH_FOCUS}の研究とiOS/Web開発実績を紹介しています。"
    )


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
    search_description = html.escape(build_search_description(cv_text), quote=True)

    text = replace_meta(
        text,
        re.compile(r'<meta name="twitter:description" content="[^"]*">'),
        f'<meta name="twitter:description" content="{social_description}">',
        "Twitter description",
    )
    text = replace_meta(
        text,
        re.compile(
            r'<meta name="description"\s+content="[^"]*">',
            flags=re.DOTALL,
        ),
        f'<meta name="description"\n    content="{search_description}">',
        "search description",
    )
    text = replace_meta(
        text,
        re.compile(
            r'<meta property="og:description"\s+content="[^"]*">',
            flags=re.DOTALL,
        ),
        f'<meta property="og:description"\n    content="{search_description}">',
        "Open Graph description",
    )

    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
