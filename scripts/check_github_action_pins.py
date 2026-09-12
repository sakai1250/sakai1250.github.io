from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")
USES_RE = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")

problems: list[str] = []
refs_by_action: dict[str, set[str]] = defaultdict(set)
locations_by_action: dict[str, list[str]] = defaultdict(list)

for pattern in ("*.yml", "*.yaml"):
    for workflow in sorted(WORKFLOWS_DIR.glob(pattern)):
        text = workflow.read_text(encoding="utf-8")
        for match in USES_RE.finditer(text):
            spec = match.group(1)
            line_number = text.count("\n", 0, match.start()) + 1

            if spec.startswith("./") or spec.startswith("docker://"):
                continue

            if "@" not in spec:
                problems.append(f"{workflow}:{line_number}: action reference has no @ref: {spec}")
                continue

            action, ref = spec.rsplit("@", 1)
            if not SHA_RE.fullmatch(ref):
                problems.append(
                    f"{workflow}:{line_number}: action is not pinned to a full commit SHA: {spec}"
                )
                continue

            refs_by_action[action].add(ref.lower())
            locations_by_action[action].append(f"{workflow}:{line_number}")

for action, refs in sorted(refs_by_action.items()):
    if len(refs) <= 1:
        continue
    problems.append(
        f"{action}: inconsistent commit SHAs across workflows: {', '.join(sorted(refs))} "
        f"({', '.join(locations_by_action[action])})"
    )

if problems:
    print("GitHub Actions dependency pinning problems:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print(
    "GitHub Actions dependencies pinned consistently: "
    f"{len(refs_by_action)} external actions across workflow files"
)
