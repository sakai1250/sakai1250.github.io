#!/usr/bin/env python3
"""Keep repository-facing profile identity aligned with the canonical CV header."""

from pathlib import Path
import re

from cv_profile import read_cv_field, read_cv_header_profile, read_cv_name


CV_PATH = Path("assets/cv.txt")
README_PATH = Path("README.md")
LLMS_PATH = Path("llms.txt")


def maintain_readme_name(text: str, name: str) -> str:
    text, heading_count = re.subn(
        r"(?m)^# .+ — Portfolio$", f"# {name} — Portfolio", text, count=1
    )
    if heading_count != 1:
        raise SystemExit("Could not find README profile heading")

    text, intro_count = re.subn(
        r"(?m)^Personal portfolio for [^,]+, (.+)$",
        lambda match: f"Personal portfolio for {name}, {match.group(1)}",
        text,
        count=1,
    )
    if intro_count != 1:
        raise SystemExit("Could not find README profile introduction")
    return text


def maintain_llms_identity(
    text: str,
    name: str,
    japanese_name: str,
    publication_name: str,
    roles: list[str],
    affiliation: str,
) -> str:
    text, heading_count = re.subn(r"(?m)^# .+$", f"# {name}", text, count=1)
    if heading_count != 1:
        raise SystemExit("Could not find llms.txt profile heading")

    role_text = " | ".join(roles)
    summary = f"> {role_text} @ {affiliation}"
    text, summary_count = re.subn(r"(?m)^> .+$", summary, text, count=1)
    if summary_count != 1:
        raise SystemExit("Could not find llms.txt profile summary")

    identity_fields = {
        "English name": name,
        "Japanese name": japanese_name,
        "Publication name": publication_name,
    }
    for label, value in identity_fields.items():
        text, field_count = re.subn(
            rf"(?m)^- {re.escape(label)}: .+$", f"- {label}: {value}", text, count=1
        )
        if field_count != 1:
            raise SystemExit(f"Could not find llms.txt {label} field")

    text, role_count = re.subn(
        r"(?m)^- Current role: .+$",
        f"- Current role: {role_text} @ {affiliation}",
        text,
        count=1,
    )
    if role_count != 1:
        raise SystemExit("Could not find llms.txt current role field")
    return text


def validate_identity_independence() -> None:
    synthetic_name = "Example Researcher"
    synthetic_japanese_name = "例 研究者"
    synthetic_publication_name = "E. Researcher"
    synthetic_roles = ["Research Fellow", "Computer Vision Researcher"]
    synthetic_affiliation = "Example University"
    old_name = "Old Name"
    readme = f"# {old_name} — Portfolio\n\nPersonal portfolio for {old_name}, a researcher.\n"
    llms = (
        f"# {old_name}\n\n> Old Role @ Old University\n\n## Identity\n\n"
        f"- English name: {old_name}\n- Japanese name: 旧 氏名\n"
        f"- Publication name: O. Name\n- Current role: Old Role @ Old University\n"
    )

    maintained_readme = maintain_readme_name(readme, synthetic_name)
    if maintained_readme.count(synthetic_name) != 2 or old_name in maintained_readme:
        raise SystemExit("README name maintenance depends on the current profile literal")

    maintained_llms = maintain_llms_identity(
        llms,
        synthetic_name,
        synthetic_japanese_name,
        synthetic_publication_name,
        synthetic_roles,
        synthetic_affiliation,
    )
    expected_role = "Research Fellow | Computer Vision Researcher @ Example University"
    expected_identity_fields = (
        f"- English name: {synthetic_name}",
        f"- Japanese name: {synthetic_japanese_name}",
        f"- Publication name: {synthetic_publication_name}",
    )
    if any(field not in maintained_llms for field in expected_identity_fields):
        raise SystemExit("llms.txt name variants are not fully derived from profile inputs")
    if old_name in maintained_llms or "旧 氏名" in maintained_llms or "O. Name" in maintained_llms:
        raise SystemExit("llms.txt name maintenance depends on current profile literals")
    if maintained_llms.count(expected_role) != 2 or "Old Role" in maintained_llms:
        raise SystemExit("llms.txt role maintenance depends on the current profile literal")


def main() -> None:
    validate_identity_independence()
    cv_text = CV_PATH.read_text(encoding="utf-8")
    name = read_cv_name(cv_text)
    japanese_name = read_cv_field(cv_text, "Japanese name")
    publication_name = read_cv_field(cv_text, "Publication name")
    roles, affiliation = read_cv_header_profile(cv_text)
    README_PATH.write_text(
        maintain_readme_name(README_PATH.read_text(encoding="utf-8"), name),
        encoding="utf-8",
    )
    LLMS_PATH.write_text(
        maintain_llms_identity(
            LLMS_PATH.read_text(encoding="utf-8"),
            name,
            japanese_name,
            publication_name,
            roles,
            affiliation,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
