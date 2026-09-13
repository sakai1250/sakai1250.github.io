from __future__ import annotations

import re
import subprocess
from pathlib import Path

WORKFLOW_DIR = Path(".github/workflows")
NODE_VERSION = Path(".node-version")
SETUP_NODE_RE = re.compile(r"\bactions/setup-node@")
VERSION_FILE_RE = re.compile(
    r"^\s*node-version-file:\s*['\"]?\.node-version['\"]?\s*(?:#.*)?$",
    re.MULTILINE,
)
HARDCODED_VERSION_RE = re.compile(r"^\s*node-version:\s*", re.MULTILINE)

version_lines = [line.strip() for line in NODE_VERSION.read_text(encoding="utf-8").splitlines() if line.strip()]
if len(version_lines) != 1:
    raise SystemExit(".node-version must contain exactly one non-empty version line")

declared_version = version_lines[0]
if not re.fullmatch(r"\d+", declared_version):
    raise SystemExit(".node-version must contain a single Node major version such as 24")

try:
    runtime_version = subprocess.run(
        ["node", "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
except (FileNotFoundError, subprocess.CalledProcessError) as exc:
    raise SystemExit("Node is unavailable; install the version declared in .node-version") from exc

runtime_match = re.fullmatch(r"v(\d+)(?:\.\d+){2}", runtime_version)
if runtime_match is None:
    raise SystemExit(f"Could not parse `node --version` output: {runtime_version!r}")
if runtime_match.group(1) != declared_version:
    raise SystemExit(
        f"Local Node major version {runtime_match.group(1)} does not match .node-version "
        f"({declared_version})"
    )

failures: list[str] = []
checked_steps = 0

for workflow in sorted((*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml"))):
    text = workflow.read_text(encoding="utf-8")
    setup_count = len(SETUP_NODE_RE.findall(text))
    if not setup_count:
        continue

    checked_steps += setup_count
    source_count = len(VERSION_FILE_RE.findall(text))
    if source_count != setup_count:
        failures.append(
            f"{workflow}: {setup_count} setup-node step(s) but {source_count} .node-version source(s)"
        )
    if HARDCODED_VERSION_RE.search(text):
        failures.append(f"{workflow}: hard-coded node-version found; use node-version-file instead")

if not checked_steps:
    raise SystemExit("No actions/setup-node steps found in GitHub Actions workflows")

if failures:
    print("Node runtime source drift detected:")
    for failure in failures:
        print(f"  - {failure}")
    raise SystemExit(1)

print(
    f"Node runtime aligned: local {runtime_version}; {checked_steps} setup-node step(s) use "
    f".node-version ({declared_version})"
)
