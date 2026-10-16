#!/usr/bin/env python3
"""Reject reintroduction of the declined SCAT award into public achievements."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SOURCES = ("index.html", "assets/cv.txt")

for relative_path in PUBLIC_SOURCES:
    content = (ROOT / relative_path).read_text(encoding="utf-8")
    if "SCAT" in content or "SCAT研究助成" in content:
        raise SystemExit(
            f"Declined SCAT award must not be listed as a public achievement: {relative_path}"
        )
