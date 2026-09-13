from __future__ import annotations

import re
from pathlib import Path

WORKFLOW_DIR = Path(".github/workflows")
PYTHON_VERSION = Path(".python-version")
SETUP_PYTHON_RE = re.compile(r"\bactions/setup-python@")
VERSION_FILE_RE = re.compile(
    r"^\s*python-version-file:\s*['\"]?\.python-version['\"]?\s*(?:#.*)?$",
    re.MULTILINE,
)
HARDCODED_VERSION_RE = re.compile(r"^\s*python-version:\s*", re.MULTILINE)
PYTHON_EXECUTABLE_VERSION_RE = re.compile(r"^\d+\.\d+$")

version_lines = [line.strip() for line in PYTHON_VERSION.read_text(encoding="utf-8").splitlines() if line.strip()]
if len(version_lines) != 1:
    raise SystemExit(".python-version must contain exactly one non-empty version line")

version = version_lines[0]
if not PYTHON_EXECUTABLE_VERSION_RE.fullmatch(version):
    raise SystemExit(
        ".python-version must use major.minor format (for example, 3.13) so the "
        "README local-validation command python$(cat .python-version) remains executable"
    )

failures: list[str] = []
checked_steps = 0

for workflow in sorted((*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml"))):
    text = workflow.read_text(encoding="utf-8")
    setup_count = len(SETUP_PYTHON_RE.findall(text))
    if not setup_count:
        continue

    checked_steps += setup_count
    source_count = len(VERSION_FILE_RE.findall(text))
    if source_count != setup_count:
        failures.append(
            f"{workflow}: {setup_count} setup-python step(s) but {source_count} .python-version source(s)"
        )
    if HARDCODED_VERSION_RE.search(text):
        failures.append(f"{workflow}: hard-coded python-version found; use python-version-file instead")

if not checked_steps:
    raise SystemExit("No actions/setup-python steps found in GitHub Actions workflows")

if failures:
    print("Python runtime source drift detected:")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)

print(
    f"Python runtime source aligned: {checked_steps} setup-python step(s) use "
    f".python-version ({version})"
)
