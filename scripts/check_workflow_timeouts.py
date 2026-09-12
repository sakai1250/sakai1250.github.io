from __future__ import annotations

import re
from pathlib import Path

WORKFLOWS_DIR = Path(".github/workflows")
MAX_TIMEOUT_MINUTES = 30
JOB_RE = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")
RUNS_ON_RE = re.compile(r"^    runs-on:\s*(?:\S.*)?$")
TIMEOUT_RE = re.compile(r"^    timeout-minutes:\s*(\d+)\s*(?:#.*)?$")


def workflow_jobs(text: str) -> list[tuple[str, list[str]]]:
    lines = text.splitlines()
    try:
        jobs_start = next(i for i, line in enumerate(lines) if line == "jobs:")
    except StopIteration:
        return []

    jobs: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []

    for line in lines[jobs_start + 1 :]:
        if line and not line.startswith(" "):
            break

        match = JOB_RE.match(line)
        if match:
            if current_name is not None:
                jobs.append((current_name, current_lines))
            current_name = match.group(1)
            current_lines = []
        elif current_name is not None:
            current_lines.append(line)

    if current_name is not None:
        jobs.append((current_name, current_lines))
    return jobs


problems: list[str] = []
runner_jobs = 0

for pattern in ("*.yml", "*.yaml"):
    for workflow in sorted(WORKFLOWS_DIR.glob(pattern)):
        text = workflow.read_text(encoding="utf-8")
        for job_name, job_lines in workflow_jobs(text):
            if not any(RUNS_ON_RE.match(line) for line in job_lines):
                continue

            runner_jobs += 1
            timeout_values = [
                int(match.group(1))
                for line in job_lines
                if (match := TIMEOUT_RE.match(line))
            ]

            if len(timeout_values) != 1:
                problems.append(
                    f"{workflow}:{job_name}: expected exactly one numeric timeout-minutes value"
                )
                continue

            timeout = timeout_values[0]
            if not 1 <= timeout <= MAX_TIMEOUT_MINUTES:
                problems.append(
                    f"{workflow}:{job_name}: timeout-minutes must be between 1 and "
                    f"{MAX_TIMEOUT_MINUTES}, found {timeout}"
                )

if runner_jobs == 0:
    problems.append("No runner-backed workflow jobs found")

if problems:
    print("Workflow timeout policy violations:")
    for problem in problems:
        print(f"  - {problem}")
    raise SystemExit(1)

print(
    f"Workflow timeout policy valid: {runner_jobs} runner-backed job(s), "
    f"all capped at {MAX_TIMEOUT_MINUTES} minutes or less"
)
