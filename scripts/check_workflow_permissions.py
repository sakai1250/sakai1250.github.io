from __future__ import annotations

import re
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")
WRITE_ALLOWED = {Path(".github/workflows/optimize-portfolio.yml")}
TOP_LEVEL_PERMISSIONS_RE = re.compile(
    r"(?m)^permissions:\s*\n((?:^[ \t]+[^\n]+\n?)*)"
)
CONTENTS_PERMISSION_RE = re.compile(r"(?m)^  contents:\s*(read|write)\s*$")


def workflow_paths() -> list[Path]:
    paths: list[Path] = []
    for pattern in ("*.yml", "*.yaml"):
        paths.extend(WORKFLOWS_DIR.glob(pattern))
    return sorted(paths)


errors: list[str] = []
paths = workflow_paths()

if not paths:
    raise SystemExit("No GitHub Actions workflows found")

for path in paths:
    text = path.read_text(encoding="utf-8")
    match = TOP_LEVEL_PERMISSIONS_RE.search(text)
    if not match:
        errors.append(f"{path}: missing explicit top-level permissions block")
        continue

    contents_match = CONTENTS_PERMISSION_RE.search(match.group(1))
    if not contents_match:
        errors.append(f"{path}: top-level permissions must declare contents: read or write")
        continue

    permission = contents_match.group(1)
    if permission == "write" and path not in WRITE_ALLOWED:
        errors.append(f"{path}: unexpected contents: write permission")
    if permission == "read" and path in WRITE_ALLOWED:
        errors.append(f"{path}: optimizer workflow requires contents: write to commit maintained assets")

    extra_scopes = [
        line.strip()
        for line in match.group(1).splitlines()
        if line.strip() and not line.startswith("  contents:")
    ]
    if extra_scopes:
        errors.append(
            f"{path}: unexpected top-level permission scopes: {', '.join(extra_scopes)}"
        )

if errors:
    print("GitHub Actions workflow permission policy violations:")
    for error in errors:
        print(f"  - {error}")
    raise SystemExit(1)

print(
    "Workflow permissions aligned: "
    f"{len(paths)} workflows declare explicit least-privilege contents access; "
    f"write access limited to {', '.join(str(path) for path in sorted(WRITE_ALLOWED))}"
)
