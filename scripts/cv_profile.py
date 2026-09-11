#!/usr/bin/env python3
"""Parse machine-readable profile fields from assets/cv.txt."""


def read_cv_header_profile(cv_text: str) -> tuple[list[str], str]:
    preamble = cv_text.split("\n\n", 1)[0]
    lines = [line.strip() for line in preamble.splitlines() if line.strip()]
    role_indexes = [index for index, line in enumerate(lines[:-1]) if " | " in line]
    if len(role_indexes) != 1:
        raise SystemExit("assets/cv.txt must contain exactly one role header followed by affiliation")

    role_index = role_indexes[0]
    roles = [role.strip() for role in lines[role_index].split("|") if role.strip()]
    affiliation = lines[role_index + 1].split(",", 1)[0].strip()
    if len(roles) < 2 or not affiliation or ":" in affiliation:
        raise SystemExit("assets/cv.txt has an incomplete role or affiliation header")
    return roles, affiliation
