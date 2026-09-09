#!/usr/bin/env python3
"""Keep research award highlights aligned with the machine-readable CV."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CV = ROOT / "assets/cv.txt"

HCV_AWARD_LINE = "- HCV2026 Outstanding Paper Award - 2026"
HCV_PUBLICATION_MARKER = (
    'NeuroGuard: Neural Gradient Update Aware of Representation Damage,”\n'
    '                  <div class="muted">ECCV 2026 Workshop on Human-inspired Computer Vision, Oral, Malmö, Sweden.</div>'
)
HCV_PUBLICATION_WITH_AWARD = (
    'NeuroGuard: Neural Gradient Update Aware of Representation Damage,”\n'
    '                  <div class="muted">ECCV 2026 Workshop on Human-inspired Computer Vision, Oral, Outstanding Paper Award, Malmö, Sweden.</div>'
)
HCV_AWARD_ITEM = """                <li data-year="2026"><span class="badge-year">2026</span>
                  <span lang="ja">ECCV 2026 Human-inspired Computer Vision Workshop Outstanding Paper Award</span>
                  <span lang="en">ECCV 2026 Human-inspired Computer Vision Workshop, Outstanding Paper Award</span>
                </li>
"""
HCV_AWARD_VISIBLE_MARKER = (
    "ECCV 2026 Human-inspired Computer Vision Workshop, Outstanding Paper Award"
)


def maintain_hcv_award(text: str, cv_text: str) -> str:
    if HCV_AWARD_LINE not in cv_text:
        return text

    if "Outstanding Paper Award." not in cv_text:
        raise SystemExit("HCV2026 award is listed in the CV but missing from the NeuroGuard publication entry")

    if HCV_PUBLICATION_WITH_AWARD not in text:
        if HCV_PUBLICATION_MARKER not in text:
            raise SystemExit("Could not find the NeuroGuard HCV2026 publication entry")
        text = text.replace(HCV_PUBLICATION_MARKER, HCV_PUBLICATION_WITH_AWARD, 1)

    awards_pattern = re.compile(
        r'(<section class="section-card" id="research-awards">.*?<ul class="repo-list">\n)(.*?)(\n\s*</ul>\n\s*</section>)',
        flags=re.DOTALL,
    )
    match = awards_pattern.search(text)
    if not match:
        raise SystemExit("Could not find the public Awards section")

    awards = match.group(2)
    if HCV_AWARD_VISIBLE_MARKER not in awards:
        awards = HCV_AWARD_ITEM + awards
        text = text[: match.start(2)] + awards + text[match.end(2) :]
        match = awards_pattern.search(text)
        if not match:
            raise SystemExit("Awards section became invalid after HCV2026 insertion")
        awards = match.group(2)

    award_count = len(re.findall(r'<li\b[^>]*data-year="\d{4}"', awards))
    text, count = re.subn(
        r'(<div class="stat-value" id="stat-awards">)\d+(</div>)',
        rf'\g<1>{award_count}\g<2>',
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit("Could not update the static award count")

    return text


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    cv_text = CV.read_text(encoding="utf-8")
    updated = maintain_hcv_award(text, cv_text)
    if updated != text:
        INDEX.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
