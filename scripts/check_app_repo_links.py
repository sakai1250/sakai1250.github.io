from __future__ import annotations

from pathlib import Path

from app_repo_links import EXPECTED_REPOS, REPO_LINK, app_card


INDEX = Path("index.html")


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
