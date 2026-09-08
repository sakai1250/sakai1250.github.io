#!/usr/bin/env python3
"""Verify that social profile text follows CV role and affiliation changes."""

from html import escape
from pathlib import Path

from maintain_social_profile import build_social_description


def main() -> None:
    synthetic_cv = """TAIGO SAKAI
Japanese name: 坂井 泰吾
Publication name: T. Sakai
Ph.D. Student | Visiting Researcher | Computer Vision Researcher
Future University, Tokyo, Japan
"""
    synthetic_description = build_social_description(synthetic_cv)
    expected_synthetic = (
        "Ph.D. Student and Visiting Researcher at Future University researching "
        "Computer Vision, Continual Learning, and Multi-View Tracking."
    )
    if synthetic_description != expected_synthetic:
        raise SystemExit(
            "Social description did not follow changed CV role/affiliation: "
            f"expected={expected_synthetic!r}, actual={synthetic_description!r}"
        )
    if "Special Assistant" in synthetic_description or "Meijo University" in synthetic_description:
        raise SystemExit("Social description retained stale current-profile text")

    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    index_text = Path("index.html").read_text(encoding="utf-8")
    current_description = escape(build_social_description(cv_text), quote=True)
    expected_tag = f'<meta name="twitter:description" content="{current_description}">'
    if expected_tag not in index_text:
        raise SystemExit("Current Twitter description does not match assets/cv.txt")

    print("OK: social profile description derives from CV roles and affiliation")


if __name__ == "__main__":
    main()
