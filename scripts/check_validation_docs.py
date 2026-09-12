from __future__ import annotations

import re
from pathlib import Path

README = Path("README.md")
WORKFLOW = Path(".github/workflows/static.yml")
CHECK_RE = re.compile(r"\b(?:python(?:3(?:\.\d+)?)?)\s+(scripts/check_[A-Za-z0-9_]+\.py)\b")
REQUIRED_SHARED_STAGES = {
    "Python syntax and maintenance registry validation": "scripts/run_deterministic_maintenance.py --compile-only",
    "JavaScript syntax validation": "node --check main.js",
    "deterministic maintenance": "scripts/run_deterministic_maintenance.py",
    "maintenance idempotence diff": (
        "git diff --exit-code -- index.html 404.html main.js style.css sitemap.xml "
        "README.md llms.txt SECURITY.md .well-known/security.txt"
    ),
    "static fallback maintenance": "scripts/maintain_static_fallbacks.py",
    "static fallback idempotence diff": "git diff --exit-code -- index.html sitemap.xml",
}


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


def require_shared_stage(label: str, command: str, readme_block: str, workflow_text: str) -> None:
    readme_has = command in readme_block
    workflow_has = command in workflow_text
    if readme_has and workflow_has:
        return

    missing = []
    if not readme_has:
        missing.append("README local validation")
    if not workflow_has:
        missing.append("static.yml")
    print(f"Missing shared validation stage '{label}' from: {', '.join(missing)}")
    raise SystemExit(1)


readme_text = README.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")
readme_block = read_local_validation_block(readme_text)

readme_checks = check_scripts(readme_block)
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

for stage_label, stage_command in REQUIRED_SHARED_STAGES.items():
    require_shared_stage(stage_label, stage_command, readme_block, workflow_text)

print(
    "Validation documentation aligned: "
    f"{len(workflow_checks)} deterministic checks and "
    f"{len(REQUIRED_SHARED_STAGES)} shared validation stages"
)
