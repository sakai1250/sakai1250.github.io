from __future__ import annotations

import re


EXPECTED_REPOS = {
    "おつりDoctor (iOS)": "otsuri_docter",
    "MAIORAL (iOS)": "PresentMemo",
}
APP_CARD_MARKER = '<div class="app-card"'
REPO_LINK = re.compile(
    r'href="https://github\.com/sakai1250/([A-Za-z0-9_.-]+)"[^>]*>\s*GitHub\s*</a>'
)
REPO_LINK_WITH_ATTRS = re.compile(
    r'href="https://github\.com/sakai1250/[A-Za-z0-9_.-]+"(?P<attrs>[^>]*)>\s*GitHub\s*</a>'
)


def app_card_bounds(text: str, title: str) -> tuple[int, int]:
    title_marker = f">{title}</a>"
    title_pos = text.find(title_marker)
    if title_pos == -1:
        raise SystemExit(f"Could not find app title: {title}")

    start = text.rfind(APP_CARD_MARKER, 0, title_pos)
    if start == -1:
        raise SystemExit(f"Could not find app card for: {title}")

    next_card = text.find(APP_CARD_MARKER, title_pos + len(title_marker))
    end = next_card if next_card != -1 else len(text)
    return start, end


def app_card(text: str, title: str) -> str:
    start, end = app_card_bounds(text, title)
    return text[start:end]


def align_app_repo(text: str, title: str, expected_repo: str) -> str:
    start, end = app_card_bounds(text, title)
    block = text[start:end]

    def replacement(match: re.Match[str]) -> str:
        return (
            f'href="https://github.com/sakai1250/{expected_repo}"'
            f'{match.group("attrs")}>GitHub</a>'
        )

    updated, count = REPO_LINK_WITH_ATTRS.subn(replacement, block, count=1)
    if count != 1:
        raise SystemExit(f"Expected one GitHub link in app card: {title}")
    return text[:start] + updated + text[end:]
