#!/usr/bin/env python3
"""Guard the public HCV2026 award label against CV/source drift."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CV = (ROOT / "assets/cv.txt").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
MAINTENANCE = (ROOT / "scripts/maintain_research_awards.py").read_text(encoding="utf-8")

AWARD_LINE = "- HCV2026 Outstanding Paper Award - 2026"
PUBLIC_LABEL = "HCV2026 Outstanding Paper Award"
LEGACY_LABELS = (
    "ECCV 2026 Human-inspired Computer Vision Workshop Outstanding Paper Award",
    "ECCV 2026 Human-inspired Computer Vision Workshop, Outstanding Paper Award",
)

if AWARD_LINE not in CV:
    raise SystemExit("assets/cv.txt: HCV2026 award entry is missing")

if INDEX.count(f">{PUBLIC_LABEL}</span>") < 2:
    raise SystemExit("index.html: Japanese and English HCV2026 award labels are not aligned with the CV")

for legacy in LEGACY_LABELS:
    if legacy in INDEX:
        raise SystemExit(f"index.html: expanded legacy HCV2026 award label remains: {legacy}")

if 'HCV_AWARD_LABEL = "HCV2026 Outstanding Paper Award"' not in MAINTENANCE:
    raise SystemExit("maintain_research_awards.py: CV-aligned public award label is not guarded at source")

print("OK: HCV2026 award label is aligned across CV, public page, and maintenance source")
