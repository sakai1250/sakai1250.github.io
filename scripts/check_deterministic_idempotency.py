#!/usr/bin/env python3
"""Fail if a second deterministic maintenance pass changes repository files."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", "__pycache__", ".pytest_cache"}


def snapshot() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        files[relative.as_posix()] = path.read_bytes()
    return files


def main() -> None:
    before = snapshot()
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/run_deterministic_maintenance.py")],
        cwd=ROOT,
        check=True,
    )
    after = snapshot()

    changed = sorted(
        path for path in before.keys() | after.keys() if before.get(path) != after.get(path)
    )
    if changed:
        formatted = "\n".join(f"- {path}" for path in changed)
        raise SystemExit(
            "Deterministic maintenance is not idempotent; a second pass changed:\n"
            + formatted
        )

    print("Deterministic maintenance is idempotent.")


if __name__ == "__main__":
    main()
