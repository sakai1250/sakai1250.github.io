#!/usr/bin/env python3
"""Keep the SCAT Research Grant status consistent across Japanese and English."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

text = INDEX.read_text(encoding="utf-8")

stale = "SCAT Research Grant, Encouragement Prize (Declined due to duplicate funding)"
current = "SCAT Research Grant, Encouragement Prize (Declined)"

if stale in text:
    text = text.replace(stale, current)

if "SCAT研究助成 研究奨励金 採択(辞退)" not in text:
    raise SystemExit("Expected Japanese SCAT grant status was not found")
if current not in text:
    raise SystemExit("Expected English SCAT grant status was not found")
if stale in text:
    raise SystemExit("Stale SCAT grant decline reason remains")

INDEX.write_text(text, encoding="utf-8")
