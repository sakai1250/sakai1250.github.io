#!/usr/bin/env python3
"""Keep app cards linked to their intended GitHub repositories."""

from __future__ import annotations

import re
from pathlib import Path


INDEX = Path("index.html")
EXPECTED_REPOS = {
    "おつりDoctor (iOS)": "otsuri_docter",
    "MAIORAL (iOS)": "PresentMemo",
}
APP_CARD_MARKER = '<div class="app-card"'
REPO_LINK = re.compile(
    r'href="https://github\.com/sakai1250/(?:PresentMemo|otsuri_docter)"(?P<attrs>[^>]*)>\s*GitHub\s*</a>'
)


def align_app_repo(text: str, title: str, expected_repo: str) -> str:
    title_marker = f">{title}</a>"
    title_pos = text.find(title_marker)
    if title_pos == -1:
        raise SystemExit(f"Could not find app title: {title}")

    start = text.rfind(APP_CARD_MARKER, 0, title_pos)
    if start == -1:
        raise SystemExit(f"Could not find app card for: {title}")

    next_card = text.find(APP_CARD_MARKER, title_pos + len(title_marker))
    end = next_card if next_card != -1 else len(text)
    block = text[start:end]

    def replacement(match: re.Match[str]) -> str:
        return (
            f'href="https://github.com/sakai1250/{expected_repo}"'
            f'{match.group("attrs")}>GitHub</a>'
        )

    updated, count = REPO_LINK.subn(replacement, block, count=1)
    if count != 1:
        raise SystemExit(f"Expected one GitHub link in app card: {title}")

    return text[:start] + updated + text[end:]


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    for title, expected_repo in EXPECTED_REPOS.items():
        text = align_app_repo(text, title, expected_repo)
    INDEX.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
