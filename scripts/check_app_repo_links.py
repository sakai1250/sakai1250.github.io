from __future__ import annotations

import re
from pathlib import Path


INDEX = Path("index.html")
EXPECTED_REPOS = {
    "おつりDoctor (iOS)": "otsuri_docter",
    "MAIORAL (iOS)": "PresentMemo",
}
REPO_LINK = re.compile(
    r'href="https://github\.com/sakai1250/([A-Za-z0-9_.-]+)"[^>]*>\s*GitHub\s*</a>'
)
APP_CARD_MARKER = '<div class="app-card"'


def app_card(text: str, title: str) -> str:
    title_marker = f">{title}</a>"
    title_pos = text.find(title_marker)
    if title_pos == -1:
        raise SystemExit(f"Could not find app title: {title}")

    start = text.rfind(APP_CARD_MARKER, 0, title_pos)
    if start == -1:
        raise SystemExit(f"Could not find app card for: {title}")

    next_card = text.find(APP_CARD_MARKER, title_pos + len(title_marker))
    end = next_card if next_card != -1 else len(text)
    return text[start:end]


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    problems = []

    for title, expected_repo in EXPECTED_REPOS.items():
        links = REPO_LINK.findall(app_card(text, title))
        if links != [expected_repo]:
            problems.append(
                f"{title}: expected exactly one GitHub link to {expected_repo}, found {links or 'none'}"
            )

    if problems:
        raise SystemExit("\n".join(problems))

    print("OK: app repository links match their products")


if __name__ == "__main__":
    main()
