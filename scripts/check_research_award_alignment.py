#!/usr/bin/env python3
"""Guard the HCV2026 award label against CV/source and generated-page drift."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CV = (ROOT / "assets/cv.txt").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
MAINTENANCE = (ROOT / "scripts/maintain_research_awards.py").read_text(encoding="utf-8")

AWARD_LINE = "- HCV2026 Outstanding Paper Award - 2026"
NEUROGUARD_AWARD_LINE = (
    '1. T. Sakai, K. Hotta. "NeuroGuard: Neural Gradient Update Aware of Representation Damage." '
    'ECCV 2026 Workshop on Human-inspired Computer Vision - Oral, Outstanding Paper Award.'
)
PUBLIC_LABEL = "HCV2026 Outstanding Paper Award"
LEGACY_LABELS = (
    "ECCV 2026 Human-inspired Computer Vision Workshop Outstanding Paper Award",
    "ECCV 2026 Human-inspired Computer Vision Workshop, Outstanding Paper Award",
)
SOURCE_ONLY = "--source-only" in sys.argv[1:]

if AWARD_LINE not in CV:
    raise SystemExit("assets/cv.txt: HCV2026 award entry is missing")

if NEUROGUARD_AWARD_LINE not in CV:
    raise SystemExit("assets/cv.txt: HCV2026 award is not tied to the NeuroGuard publication entry")

if 'HCV_AWARD_LABEL = "HCV2026 Outstanding Paper Award"' not in MAINTENANCE:
    raise SystemExit("maintain_research_awards.py: CV-aligned public award label is not guarded at source")

if "HCV_CV_PUBLICATION_LINE" not in MAINTENANCE:
    raise SystemExit("maintain_research_awards.py: NeuroGuard-specific CV award validation is missing")

if not SOURCE_ONLY:
    if INDEX.count(f">{PUBLIC_LABEL}</span>") < 2:
        raise SystemExit("index.html: Japanese and English HCV2026 award labels are not aligned with the CV")

    if "NeuroGuard: Neural Gradient Update Aware of Representation Damage" not in INDEX or "Oral, Outstanding Paper Award, Malmö, Sweden." not in INDEX:
        raise SystemExit("index.html: HCV2026 award is not attached to the NeuroGuard publication entry")

    for legacy in LEGACY_LABELS:
        if legacy in INDEX:
            raise SystemExit(f"index.html: expanded legacy HCV2026 award label remains: {legacy}")

    print("OK: HCV2026 award is tied to NeuroGuard across CV, public page, and maintenance source")
else:
    print("OK: HCV2026 award source is tied to the NeuroGuard publication entry")
