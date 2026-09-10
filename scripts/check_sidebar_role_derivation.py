#!/usr/bin/env python3
"""Verify that sidebar roles follow the CV header instead of fixed role text."""

from pathlib import Path

from maintain_profile_metadata import build_sidebar_roles, read_cv_header_profile


def main() -> None:
    synthetic_cv = """TAIGO SAKAI
Portfolio: https://example.com
Email: test@example.com
Publication name: T. Sakai
ORCID: https://orcid.org/0000-0000-0000-0000
Ph.D. Student | Visiting Researcher | Computer Vision Researcher
Meijo University, Japan
"""
    japanese, english = build_sidebar_roles(synthetic_cv)
    if english != "Ph.D. Student · Visiting Researcher":
        raise SystemExit(f"English sidebar role did not follow changed CV roles: {english!r}")
    if japanese != "博士後期課程 · Visiting Researcher":
        raise SystemExit(f"Japanese sidebar role did not localize changed CV roles: {japanese!r}")

    roles, affiliation = read_cv_header_profile(synthetic_cv)
    if roles != ["Ph.D. Student", "Visiting Researcher", "Computer Vision Researcher"]:
        raise SystemExit(f"CV role header was not found after extra preamble fields: {roles!r}")
    if affiliation != "Meijo University":
        raise SystemExit(f"CV affiliation was not found after the role header: {affiliation!r}")

    ambiguous_cv = synthetic_cv + "\nResearcher | Engineer\nAnother University, Japan\n"
    try:
        read_cv_header_profile(ambiguous_cv)
    except SystemExit:
        pass
    else:
        raise SystemExit("Ambiguous CV role headers should be rejected")

    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    index_text = Path("index.html").read_text(encoding="utf-8")
    japanese, english = build_sidebar_roles(cv_text)
    if japanese not in index_text:
        raise SystemExit(f"Current Japanese sidebar role is not CV-derived: {japanese!r}")
    if english not in index_text:
        raise SystemExit(f"Current English sidebar role is not CV-derived: {english!r}")

    print("OK: sidebar roles derive from the CV role header without fixed line positions")


if __name__ == "__main__":
    main()
