#!/usr/bin/env python3
"""Keep research award highlights aligned with the machine-readable CV."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CV = ROOT / "assets/cv.txt"

HCV_AWARD_LINE = "- HCV2026 Outstanding Paper Award - 2026"
HCV_CV_PUBLICATION_LINE = (
    '1. T. Sakai, K. Hotta. "NeuroGuard: Neural Gradient Update Aware of Representation Damage." '
    'ECCV 2026 Workshop on Human-inspired Computer Vision - Oral, Outstanding Paper Award.'
)
HCV_PUBLICATION_MARKER = (
    'NeuroGuard: Neural Gradient Update Aware of Representation Damage,”\n'
    '                  <div class="muted">ECCV 2026 Workshop on Human-inspired Computer Vision, Oral, Malmö, Sweden.</div>'
)
HCV_PUBLICATION_WITH_AWARD = (
    'NeuroGuard: Neural Gradient Update Aware of Representation Damage,”\n'
    '                  <div class="muted">ECCV 2026 Workshop on Human-inspired Computer Vision, Oral, Outstanding Paper Award, Malmö, Sweden.</div>'
)
HCV_AWARD_LABEL = "HCV2026 Outstanding Paper Award"
HCV_AWARD_ITEM = f"""                <li data-year="2026"><span class="badge-year">2026</span>
                  <span lang="ja">{HCV_AWARD_LABEL}</span>
                  <span lang="en">{HCV_AWARD_LABEL}</span>
                </li>
"""
HCV_AWARD_LEGACY_LABELS = (
    "ECCV 2026 Human-inspired Computer Vision Workshop Outstanding Paper Award",
    "ECCV 2026 Human-inspired Computer Vision Workshop, Outstanding Paper Award",
)
IEICE_AWARD_LABEL = "IEICE Tokai Branch Student Research Encouragement Award"
IEICE_AWARD_URL = "https://www.ieice.org/tokai/student/student-shorei/"
POWER_ACADEMY_FIRST_PRIZE_LABEL = "Power Academy Electrical Education Content Contest, First Prize"
POWER_ACADEMY_FIRST_PRIZE_URL = "https://www.power-academy.jp/info/2024/003795.html"
POWER_ACADEMY_EXCELLENCE_LABEL = "Power Academy Electrical Education Content Contest, Excellence Award"
POWER_ACADEMY_EXCELLENCE_URL = "https://www.power-academy.jp/event/contest/search/"
ROBOMASTER_AWARD_LEGACY_LABEL = "RoboMaster in NorthAmerica 2024 SecondPrize"
ROBOMASTER_AWARD_LABEL = "RoboMaster in North America 2024, Second Prize"
ATLASFUSION_AUTHOR_LEGACY = "K.Toida,"
ATLASFUSION_AUTHOR_LABEL = "K. Toida,"
ATLASFUSION_TITLE = "ATLASFusion: Aggregation Tracking with Location-Aware Sparse Fusion for Robust Spatio-Temporal Multi-View Pedestrian Tracking"


def sync_award_link(text: str, year: str, label: str, url: str) -> str:
    award_item_pattern = re.compile(
        rf'(<li\b[^>]*data-year="{re.escape(year)}"[^>]*>.*?{re.escape(label)}.*?<a\s+href=")([^"]+)(")',
        flags=re.DOTALL,
    )
    text, count = award_item_pattern.subn(
        rf'\g<1>{url}\g<3>',
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Could not find the {label} detail link")
    return text


def maintain_award_links(text: str) -> str:
    text = sync_award_link(text, "2026", IEICE_AWARD_LABEL, IEICE_AWARD_URL)
    text = sync_award_link(
        text,
        "2023",
        POWER_ACADEMY_FIRST_PRIZE_LABEL,
        POWER_ACADEMY_FIRST_PRIZE_URL,
    )
    text = sync_award_link(
        text,
        "2021",
        POWER_ACADEMY_EXCELLENCE_LABEL,
        POWER_ACADEMY_EXCELLENCE_URL,
    )
    return text


def maintain_award_labels(text: str) -> str:
    if ROBOMASTER_AWARD_LEGACY_LABEL in text:
        text = text.replace(
            ROBOMASTER_AWARD_LEGACY_LABEL,
            ROBOMASTER_AWARD_LABEL,
            1,
        )
    if ROBOMASTER_AWARD_LABEL not in text:
        raise SystemExit("Could not find the normalized RoboMaster award label")
    return text


def maintain_publication_labels(text: str) -> str:
    publication_pattern = re.compile(
        rf'(<li\b[^>]*data-year="2026"[^>]*>\s*<span class="badge-year">2026</span>\s*){re.escape(ATLASFUSION_AUTHOR_LEGACY)}(.*?{re.escape(ATLASFUSION_TITLE)})',
        flags=re.DOTALL,
    )
    text, count = publication_pattern.subn(
        rf'\g<1>{ATLASFUSION_AUTHOR_LABEL}\g<2>',
        text,
        count=1,
    )
    if count == 0 and f"{ATLASFUSION_AUTHOR_LABEL} <b>T. Sakai</b>" not in text:
        raise SystemExit("Could not find the normalized ATLASFusion author entry")
    return text


def maintain_hcv_award(text: str, cv_text: str) -> str:
    if HCV_AWARD_LINE not in cv_text:
        return text

    if HCV_CV_PUBLICATION_LINE not in cv_text:
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
    for legacy_label in HCV_AWARD_LEGACY_LABELS:
        awards = awards.replace(legacy_label, HCV_AWARD_LABEL)

    if HCV_AWARD_LABEL not in awards:
        awards = HCV_AWARD_ITEM + awards

    text = text[: match.start(2)] + awards + text[match.end(2) :]
    match = awards_pattern.search(text)
    if not match:
        raise SystemExit("Awards section became invalid after HCV2026 synchronization")
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
    updated = maintain_award_links(updated)
    updated = maintain_award_labels(updated)
    updated = maintain_publication_labels(updated)
    if updated != text:
        INDEX.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
