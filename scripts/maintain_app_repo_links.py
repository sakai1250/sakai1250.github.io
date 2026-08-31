from __future__ import annotations

from pathlib import Path

from app_repo_links import EXPECTED_REPOS, align_app_repo


INDEX = Path("index.html")


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    original = text

    for title, expected_repo in EXPECTED_REPOS.items():
        text = align_app_repo(text, title, expected_repo)

    if text != original:
        INDEX.write_text(text, encoding="utf-8")
        print("Updated app repository links")
    else:
        print("OK: app repository links already match their products")


if __name__ == "__main__":
    main()
