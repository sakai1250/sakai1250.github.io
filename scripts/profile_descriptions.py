#!/usr/bin/env python3
"""Build CV-derived profile descriptions shared by metadata transforms."""

from cv_profile import read_cv_field, read_cv_header_profile, read_cv_section_bullets


ROLE_LABELS_JA = {
    "Ph.D. Student": "博士後期課程",
}
AFFILIATION_LABELS_JA = {
    "Meijo University": "名城大学大学院",
}


def join_english(items: list[str]) -> str:
    if not items:
        raise SystemExit("assets/cv.txt RESEARCH AREAS must contain at least one bullet")
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def research_areas(cv_text: str) -> list[str]:
    areas = read_cv_section_bullets(cv_text, "RESEARCH AREAS")
    if not areas:
        raise SystemExit("assets/cv.txt RESEARCH AREAS must contain at least one bullet")
    return areas


def build_social_description(cv_text: str) -> str:
    roles, affiliation = read_cv_header_profile(cv_text)
    visible_roles = roles[:2]
    role_phrase = " and ".join(visible_roles)
    focus = join_english(research_areas(cv_text))
    return f"{role_phrase} at {affiliation} researching {focus}."


def build_search_description(cv_text: str) -> str:
    roles, affiliation = read_cv_header_profile(cv_text)
    japanese_name = read_cv_field(cv_text, "Japanese name").replace(" ", "")
    visible_roles = roles[:2]
    localized_roles = [ROLE_LABELS_JA.get(role, role) for role in visible_roles]
    localized_affiliation = AFFILIATION_LABELS_JA.get(affiliation, affiliation)
    role_phrase = "・".join(localized_roles)
    focus = "、".join(research_areas(cv_text))
    return (
        f"{localized_affiliation} {role_phrase} {japanese_name}のポートフォリオ。"
        f"{focus}の研究とiOS/Web開発実績を紹介しています。"
    )
