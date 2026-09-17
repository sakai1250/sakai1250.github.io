#!/usr/bin/env python3
"""Parse machine-readable profile fields from assets/cv.txt."""

import re


def read_cv_field(cv_text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(.+?)\s*$", cv_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit(f"assets/cv.txt is missing a machine-readable {label} field")
    value = match.group(1).strip()
    if not value:
        raise SystemExit(f"assets/cv.txt has an empty machine-readable {label} field")
    return value


def read_cv_name(cv_text: str) -> str:
    first_line = cv_text.splitlines()[0].strip() if cv_text.splitlines() else ""
    if not first_line or ":" in first_line:
        raise SystemExit("assets/cv.txt is missing the profile name header")
    return first_line.title()


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


def read_cv_section_bullets(cv_text: str, heading: str) -> list[str]:
    """Return bullet values from one all-caps section in the machine-readable CV."""
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n(?P<body>.*?)(?=\n[A-Z][A-Z ]+\n|\Z)",
        cv_text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise SystemExit(f"assets/cv.txt is missing section: {heading}")
    return re.findall(r"^-\s+(.+)$", match.group("body"), flags=re.MULTILINE)
