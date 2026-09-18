from __future__ import annotations

import ast
import re
from pathlib import Path

README = Path("README.md")
WORKFLOW = Path(".github/workflows/static.yml")
WORKFLOWS_DIR = Path(".github/workflows")
RUNNER = Path("scripts/run_local_validation.py")
SCRIPTS_DIR = Path("scripts")
ENTRY_COMMAND = "scripts/run_local_validation.py"
CHECK_RE = re.compile(r"scripts/check_[A-Za-z0-9_]+\.py")


def read_local_validation_block(text: str) -> str:
    section = re.search(r"^## Local validation\s*$([\s\S]*?)(?=^##\s|\Z)", text, re.MULTILINE)
    if not section:
        raise SystemExit("README.md: missing '## Local validation' section")
    code_block = re.search(r"```bash\s*\n([\s\S]*?)\n```", section.group(1))
    if not code_block:
        raise SystemExit("README.md: missing primary bash block in local validation section")
    return code_block.group(1)


def runner_checks() -> set[str]:
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"), filename=str(RUNNER))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "CHECKS" for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            return set(value)
    raise SystemExit(f"{RUNNER}: missing literal CHECKS list")


def registered_workflow_checks() -> set[str]:
    registered: set[str] = set()
    for pattern in ("*.yml", "*.yaml"):
        for workflow in WORKFLOWS_DIR.glob(pattern):
            registered.update(CHECK_RE.findall(workflow.read_text(encoding="utf-8")))
    return registered


readme_text = README.read_text(encoding="utf-8")
workflow_text = WORKFLOW.read_text(encoding="utf-8")
readme_block = read_local_validation_block(readme_text)

if ENTRY_COMMAND not in readme_block:
    raise SystemExit(f"README local validation must call {ENTRY_COMMAND}")
if ENTRY_COMMAND not in workflow_text:
    raise SystemExit(f"static.yml must call {ENTRY_COMMAND}")

checks = runner_checks()
all_checks = {
    path.as_posix()
    for path in SCRIPTS_DIR.glob("check_*.py")
    if path.name != "check_external_links.py"
}
missing = sorted(all_checks - checks)
stale = sorted(checks - all_checks)
if missing or stale:
    if missing:
        print("Deterministic checks missing from local validation runner:")
        for path in missing:
            print(f"  - {path}")
    if stale:
        print("Local validation runner references missing or network-only checks:")
        for path in stale:
            print(f"  - {path}")
    raise SystemExit(1)

workflow_direct_checks = set(CHECK_RE.findall(workflow_text))
if workflow_direct_checks:
    raise SystemExit(
        "static.yml should use the shared validation runner instead of direct check scripts: "
        + ", ".join(sorted(workflow_direct_checks))
    )

registered_checks = registered_workflow_checks()
unregistered_external = "scripts/check_external_links.py" not in registered_checks
if unregistered_external:
    raise SystemExit("Network-dependent external-link check is not registered in any workflow")

print(
    "Validation entry point aligned: "
    f"README and static.yml use {ENTRY_COMMAND}; {len(checks)} deterministic checks are registered"
)
