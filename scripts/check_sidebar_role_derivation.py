#!/usr/bin/env python3
"""Verify that CV-derived roles and titles do not depend on fixed line positions."""

from pathlib import Path

from maintain_profile_metadata import build_page_title, build_sidebar_roles, read_cv_header_profile


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

    expected_title = "Taigo Sakai | Ph.D. Student, Visiting Researcher & Computer Vision Researcher"
    if build_page_title(synthetic_cv) != expected_title:
        raise SystemExit("Page title did not follow the content-based CV role parser")

    ambiguous_cv = synthetic_cv.replace(
        "Ph.D. Student | Visiting Researcher | Computer Vision Researcher\n",
        "Ph.D. Student | Visiting Researcher | Computer Vision Researcher\nResearcher | Engineer\n",
    )
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

    # Public title metadata belongs to maintain_profile_metadata.py. Header
    # maintenance must not grow a second CV-title parser or rewrite the same
    # title tags again.
    header_source = Path("scripts/maintain_header_controls.py").read_text(encoding="utf-8")
    duplicate_title_markers = (
        "build_page_title",
        "<title>",
        "og:title",
        "twitter:title",
    )
    duplicate_markers = [marker for marker in duplicate_title_markers if marker in header_source]
    if duplicate_markers:
        raise SystemExit(
            "Header maintenance duplicates profile title ownership: "
            + ", ".join(duplicate_markers)
        )

    print("OK: CV-derived roles and titles do not depend on fixed line positions")


if __name__ == "__main__":
    main()
