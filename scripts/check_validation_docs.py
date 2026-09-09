from __future__ import annotations

import re
from pathlib import Path

README = Path("README.md")
WORKFLOW = Path(".github/workflows/static.yml")
CHECK_RE = re.compile(r"\b(?:python(?:3(?:\.14)?)?)\s+(scripts/check_[A-Za-z0-9_]+\.py)\b")


def read_local_validation_block(text: str) -> str:
    section = re.search(r"^## Local validation\s*$([\s\S]*?)(?=^##\s|\Z)", text, re.MULTILINE)
    if not section:
        raise SystemExit("README.md: missing '## Local validation' section")

    code_block = re.search(r"```bash\s*\n([\s\S]*?)\n```", section.group(1))
    if not code_block:
        raise SystemExit("README.md: missing primary bash block in local validation section")
    return code_block.group(1)


def check_scripts(text: str) -> set[str]:
    return set(CHECK_RE.findall(text))


readme_text = README.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")

readme_checks = check_scripts(read_local_validation_block(readme_text))
workflow_checks = check_scripts(workflow_text)

only_readme = sorted(readme_checks - workflow_checks)
only_workflow = sorted(workflow_checks - readme_checks)

if only_readme or only_workflow:
    if only_readme:
        print("Validation checks documented locally but not run by static.yml:")
        for path in only_readme:
            print(f"  - {path}")
    if only_workflow:
        print("Validation checks run by static.yml but missing from README local validation:")
        for path in only_workflow:
            print(f"  - {path}")
    raise SystemExit(1)

if not workflow_checks:
    raise SystemExit("No scripts/check_*.py validations found in static.yml")

print(f"Validation documentation aligned: {len(workflow_checks)} deterministic checks")
