#!/usr/bin/env python3
"""Verify that social and search profile text follows CV identity changes."""

from html import escape
from pathlib import Path

from maintain_social_profile import build_search_description, build_social_description


def main() -> None:
    synthetic_cv = """TAIGO SAKAI
Japanese name: 坂井 泰吾
Publication name: T. Sakai
Ph.D. Student | Visiting Researcher | Computer Vision Researcher
Future University, Tokyo, Japan
"""
    synthetic_social_description = build_social_description(synthetic_cv)
    expected_social = (
        "Ph.D. Student and Visiting Researcher at Future University researching "
        "Computer Vision, Continual Learning, and Multi-View Tracking."
    )
    if synthetic_social_description != expected_social:
        raise SystemExit(
            "Social description did not follow changed CV role/affiliation: "
            f"expected={expected_social!r}, actual={synthetic_social_description!r}"
        )

    synthetic_search_description = build_search_description(synthetic_cv)
    expected_search = (
        "Future University 博士後期課程・Visiting Researcher 坂井泰吾のポートフォリオ。"
        "Computer Vision、Continual Learning、Multi-View Trackingの研究とiOS/Web開発実績を紹介しています。"
    )
    if synthetic_search_description != expected_search:
        raise SystemExit(
            "Search description did not follow changed CV role/affiliation: "
            f"expected={expected_search!r}, actual={synthetic_search_description!r}"
        )

    for description in (synthetic_social_description, synthetic_search_description):
        if "Special Assistant" in description or "Meijo University" in description or "名城大学" in description:
            raise SystemExit("Profile description retained stale current-profile text")

    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    index_text = Path("index.html").read_text(encoding="utf-8")

    current_social_description = escape(build_social_description(cv_text), quote=True)
    expected_twitter_tag = (
        f'<meta name="twitter:description" content="{current_social_description}">'
    )
    if expected_twitter_tag not in index_text:
        raise SystemExit("Current Twitter description does not match assets/cv.txt")

    current_search_description = escape(build_search_description(cv_text), quote=True)
    expected_search_tag = (
        '<meta name="description"\n'
        f'    content="{current_search_description}">'
    )
    expected_og_tag = (
        '<meta property="og:description"\n'
        f'    content="{current_search_description}">'
    )
    if expected_search_tag not in index_text:
        raise SystemExit("Current search description does not match assets/cv.txt")
    if expected_og_tag not in index_text:
        raise SystemExit("Current Open Graph description does not match assets/cv.txt")

    # Social description ownership belongs to the dedicated social-profile
    # transform. Header maintenance should not duplicate that CV-derived logic.
    header_source = Path("scripts/maintain_header_controls.py").read_text(encoding="utf-8")
    if "build_social_description" in header_source:
        raise SystemExit("Header maintenance duplicates social-description ownership")

    social_source = Path("scripts/maintain_social_profile.py").read_text(encoding="utf-8")
    if "build_social_description(cv_text)" not in social_source:
        raise SystemExit("Social-profile maintenance does not derive description from the current CV")
    stale_social_literal = (
        "Ph.D. Student and Special Assistant at Meijo University researching "
        "Computer Vision, Continual Learning, and Multi-View Tracking."
    )
    if stale_social_literal in social_source or stale_social_literal in header_source:
        raise SystemExit("Maintenance still contains a hard-coded current-profile description")

    profile_source = Path("scripts/maintain_profile_metadata.py").read_text(encoding="utf-8")
    if "from maintain_social_profile import build_search_description" not in profile_source:
        raise SystemExit("Profile maintenance does not reuse the CV-derived search description helper")
    if "build_search_description(cv_text)" not in profile_source:
        raise SystemExit("Profile maintenance does not derive search description from the current CV")
    stale_search_literal = (
        "名城大学大学院 博士後期課程・Special Assistant 坂井泰吾のポートフォリオ。"
        "Computer Vision、Continual Learning、Multi-View Trackingの研究とiOS/Web開発実績を紹介しています。"
    )
    if stale_search_literal in profile_source:
        raise SystemExit("Profile maintenance still contains a hard-coded current-profile search description")

    print("OK: social, search, and Open Graph descriptions derive from CV roles and affiliation")


if __name__ == "__main__":
    main()
