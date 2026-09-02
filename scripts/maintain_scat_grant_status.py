#!/usr/bin/env python3
"""Keep the SCAT Research Grant status consistent across portfolio sources."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CV_TEXT = ROOT / "assets" / "cv.txt"

index_text = INDEX.read_text(encoding="utf-8")
cv_text = CV_TEXT.read_text(encoding="utf-8")

stale_index = "SCAT Research Grant, Encouragement Prize (Declined due to duplicate funding)"
current_index = "SCAT Research Grant, Encouragement Prize (Declined)"
stale_cv = "SCAT Research Grant, Encouragement Prize, declined due to duplicate funding - 2026"
current_cv = "SCAT Research Grant, Encouragement Prize (Declined) - 2026"

if stale_index in index_text:
    index_text = index_text.replace(stale_index, current_index)
if stale_cv in cv_text:
    cv_text = cv_text.replace(stale_cv, current_cv)

if "SCAT研究助成 研究奨励金 採択(辞退)" not in index_text:
    raise SystemExit("Expected Japanese SCAT grant status was not found")
if current_index not in index_text:
    raise SystemExit("Expected English SCAT grant status was not found")
if stale_index in index_text:
    raise SystemExit("Stale SCAT grant decline reason remains in index.html")
if current_cv not in cv_text:
    raise SystemExit("Expected SCAT grant status was not found in assets/cv.txt")
if stale_cv in cv_text:
    raise SystemExit("Stale SCAT grant decline reason remains in assets/cv.txt")

INDEX.write_text(index_text, encoding="utf-8")
CV_TEXT.write_text(cv_text, encoding="utf-8")
