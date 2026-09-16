#!/usr/bin/env python3
"""Keep repository-facing profile names aligned with the canonical CV name."""

from pathlib import Path
import re

from cv_profile import read_cv_name


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


def maintain_llms_name(text: str, name: str) -> str:
    text, heading_count = re.subn(r"(?m)^# .+$", f"# {name}", text, count=1)
    if heading_count != 1:
        raise SystemExit("Could not find llms.txt profile heading")

    text, field_count = re.subn(
        r"(?m)^- English name: .+$", f"- English name: {name}", text, count=1
    )
    if field_count != 1:
        raise SystemExit("Could not find llms.txt English name field")
    return text


def validate_name_independence() -> None:
    synthetic = "Example Researcher"
    readme = "# Old Name — Portfolio\n\nPersonal portfolio for Old Name, a researcher.\n"
    llms = "# Old Name\n\n## Identity\n\n- English name: Old Name\n"
    if synthetic not in maintain_readme_name(readme, synthetic):
        raise SystemExit("README name maintenance depends on the current profile literal")
    if maintain_llms_name(llms, synthetic).count(synthetic) != 2:
        raise SystemExit("llms.txt name maintenance depends on the current profile literal")


def main() -> None:
    validate_name_independence()
    name = read_cv_name(CV_PATH.read_text(encoding="utf-8"))
    README_PATH.write_text(
        maintain_readme_name(README_PATH.read_text(encoding="utf-8"), name),
        encoding="utf-8",
    )
    LLMS_PATH.write_text(
        maintain_llms_name(LLMS_PATH.read_text(encoding="utf-8"), name),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
