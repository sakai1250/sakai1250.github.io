#!/usr/bin/env python3
"""Regression checks for visitor-facing update-date resolution."""

from datetime import datetime
from types import SimpleNamespace

import maintain_static_fallbacks as target


OPTIMIZER = target.OPTIMIZER_COMMIT_MESSAGE
CONTENT_TIME = "2026-09-17T10:00:00+09:00"
FIRST_OPTIMIZER_TIME = "2026-09-19T10:10:00+09:00"
SECOND_OPTIMIZER_TIME = "2026-09-19T10:25:00+09:00"


def completed(stdout: str) -> SimpleNamespace:
    return SimpleNamespace(stdout=stdout)


def check_consecutive_safe_optimizers() -> None:
    history = "\n".join(
        [
            f"opt2\x1f{SECOND_OPTIMIZER_TIME}\x1f{OPTIMIZER}",
            f"opt1\x1f{FIRST_OPTIMIZER_TIME}\x1f{OPTIMIZER}",
            f"content\x1f{CONTENT_TIME}\x1ffeat: update research portfolio",
        ]
    )
    responses = {
        ("git", "log", "--format=%H%x1f%cI%x1f%s", "--", "index.html"): history,
        ("git", "show", "-s", "--format=%cI", "opt2^"): "2026-09-19T10:20:00+09:00",
        ("git", "show", "-s", "--format=%cI", "opt1^"): "2026-09-19T10:00:00+09:00",
    }

    original_run = target.subprocess.run
    target.subprocess.run = lambda args, **kwargs: completed(responses[tuple(args)])
    try:
        resolved = target.effective_git_update_timestamp("index.html")
    finally:
        target.subprocess.run = original_run

    expected = datetime.fromisoformat(CONTENT_TIME)
    if resolved != expected:
        raise SystemExit(f"Expected {expected.isoformat()}, got {resolved}")


def check_unsafe_optimizer_is_preserved() -> None:
    history = f"opt\x1f2026-09-19T12:00:00+09:00\x1f{OPTIMIZER}"
    responses = {
        ("git", "log", "--format=%H%x1f%cI%x1f%s", "--", "index.html"): history,
        ("git", "show", "-s", "--format=%cI", "opt^"): "2026-09-19T10:00:00+09:00",
    }

    original_run = target.subprocess.run
    target.subprocess.run = lambda args, **kwargs: completed(responses[tuple(args)])
    try:
        resolved = target.effective_git_update_timestamp("index.html")
    finally:
        target.subprocess.run = original_run

    expected = datetime.fromisoformat("2026-09-19T12:00:00+09:00")
    if resolved != expected:
        raise SystemExit(f"Expected unsafe optimizer timestamp {expected.isoformat()}, got {resolved}")


check_consecutive_safe_optimizers()
check_unsafe_optimizer_is_preserved()
print("Static update-date history checks passed.")
