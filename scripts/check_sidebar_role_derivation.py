#!/usr/bin/env python3
"""Verify that sidebar roles follow the CV header instead of fixed role text."""

from pathlib import Path

from maintain_profile_metadata import build_sidebar_roles


def main() -> None:
    synthetic_cv = """TAIGO SAKAI
Portfolio: https://example.com
Email: test@example.com
Ph.D. Student | Visiting Researcher | Computer Vision Researcher
Meijo University, Japan
"""
    japanese, english = build_sidebar_roles(synthetic_cv)
    if english != "Ph.D. Student · Visiting Researcher":
        raise SystemExit(f"English sidebar role did not follow changed CV roles: {english!r}")
    if japanese != "博士後期課程 · Visiting Researcher":
        raise SystemExit(f"Japanese sidebar role did not localize changed CV roles: {japanese!r}")

    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    index_text = Path("index.html").read_text(encoding="utf-8")
    japanese, english = build_sidebar_roles(cv_text)
    if japanese not in index_text:
        raise SystemExit(f"Current Japanese sidebar role is not CV-derived: {japanese!r}")
    if english not in index_text:
        raise SystemExit(f"Current English sidebar role is not CV-derived: {english!r}")

    print("OK: sidebar roles derive from the CV role header and follow role changes")


if __name__ == "__main__":
    main()
