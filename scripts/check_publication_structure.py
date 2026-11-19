#!/usr/bin/env python3
"""Verify the research achievements are typeset as authors / title / venue without changing their text."""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

from maintain_publication_structure import PUB_TAGS, structure_entry

INDEX = Path("index.html")
SECTION = re.compile(
    r'(<section class="section-card" id="research-research-achievements">)(.*?)(</section>)', re.S
)
ENTRY = re.compile(r'<li data-year="(\d{4})">(.*?)</li>', re.S)

INTERNATIONAL = """<li data-year="2026">
                  <span class="badge-year">2026</span> <b>T. Sakai</b>, K. Hotta, “
                  NeuroGuard: Neural Gradient Update Aware of Representation Damage,”
                  <div class="muted">ECCV 2026 Workshop on Human-inspired Computer Vision, Oral, Outstanding Paper Award, Malmö, Sweden.</div>
                  <a href="https://arxiv.org/abs/2608.08068" target="_blank" rel="noopener noreferrer" aria-label="Paper">[Paper]</a>
                </li>"""
INTERNATIONAL_TIGHT = """<li data-year="2025">
                  <span class="badge-year">2025</span> <b>T. Sakai</b>, K. Hotta, “Long-Tailed Data Classification by Increasing and Decreasing Neurons During Training,”
                  <div class="muted">ICCV 2025 Workshop on Human-inspired Computer Vision, Poster, Hawaii, USA.</div>
                </li>"""
DOMESTIC = """<li data-year="2025">
                  <span class="badge-year">2025</span> 神谷 聡，<b>坂井 泰吾</b>，小嶋 華，堀田 一弘, 「少ない教師付きデータからのゼニゴケ仮根の先端追跡法」 <div class="muted">動的画像処理実利用化ワークショップ (DIA2025), 福井, ポスター（査読あり）。</div>
                </li>"""


def visible_text(fragment: str) -> str:
    # Tags are removed without inserting spaces: the markup may add elements, never whitespace.
    return " ".join(html_lib.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def problems_in_entry(li_html: str) -> list[str]:
    problems: list[str] = []
    label = visible_text(li_html)[:48]
    positions = []
    for name in ("pub-authors", "pub-title", "pub-venue"):
        found = [m.start() for m in re.finditer(rf'class="[^"]*\b{name}\b[^"]*"', li_html)]
        if len(found) != 1:
            problems.append(f"{label}: expected exactly one .{name}, found {len(found)}")
        positions.append(found[0] if found else -1)
    if -1 not in positions and positions != sorted(positions):
        problems.append(f"{label}: .pub-authors, .pub-title, .pub-venue must appear in that order")
    if len(re.findall(r'<span class="pub-q" aria-hidden="true">', li_html)) != 2:
        problems.append(f"{label}: the title needs exactly two aria-hidden .pub-q quote marks")
    year_text = re.search(r'<span class="badge-year">(\d{4})</span>', li_html)
    data_year = re.match(r'<li data-year="(\d{4})"', li_html)
    if not year_text or not data_year or year_text.group(1) != data_year.group(1):
        problems.append(f"{label}: .badge-year must match data-year")
    return problems


def problems_in_index(index_html: str) -> list[str]:
    section = SECTION.search(index_html)
    if not section:
        return ["index.html: research achievements section is missing"]
    items = [m.group(0) for m in ENTRY.finditer(section.group(2))]
    if not items:
        return ["index.html: research achievements list has no entries"]
    problems: list[str] = []
    for item in items:
        problems += problems_in_entry(item)
    return problems


def self_test() -> None:
    for name, fixture in (("international", INTERNATIONAL), ("tight quote", INTERNATIONAL_TIGHT), ("domestic", DOMESTIC)):
        out = structure_entry(fixture)
        assert problems_in_entry(out) == [], (name, problems_in_entry(out))
        assert visible_text(out) == visible_text(fixture), f"{name}: visible text changed"
        assert structure_entry(out) == out, f"{name}: structure_entry is not idempotent"

    out = structure_entry(INTERNATIONAL)
    assert '<span class="pub-authors"><b>T. Sakai</b>, K. Hotta</span>, <span class="pub-title"><span class="pub-q" aria-hidden="true">“</span>' in out
    assert '<span class="pub-q" aria-hidden="true">,”</span></span>' in out
    assert '<div class="muted pub-venue">' in out
    assert '<span class="pub-tag">Outstanding Paper Award</span>' in out
    assert 'href="https://arxiv.org/abs/2608.08068"' in out and ">[Paper]</a>" in out, "link must survive"
    assert "<span class=\"pub-tag\">" not in structure_entry(INTERNATIONAL_TIGHT), "only PUB_TAGS are wrapped"

    domestic = structure_entry(DOMESTIC)
    assert '<span class="pub-q" aria-hidden="true">「</span>' in domestic and '<span class="pub-q" aria-hidden="true">」</span>' in domestic
    assert "<a " not in domestic, "domestic entries have no link and must not gain one"
    assert PUB_TAGS == ("Outstanding Paper Award",)

    try:
        structure_entry('<li data-year="2026"><span class="badge-year">2026</span> No quoted title here <div class="muted">v</div></li>')
    except SystemExit as error:
        assert "unrecognized publication entry" in str(error)
    else:
        raise AssertionError("an entry without a quoted title must be rejected")
    try:
        structure_entry('<li data-year="2026"><span class="badge-year">2026</span> <b>A</b>, “T,” no venue</li>')
    except SystemExit as error:
        assert "unrecognized publication entry" in str(error)
    else:
        raise AssertionError("an entry without a venue must be rejected")


def main() -> None:
    self_test()
    problems = problems_in_index(INDEX.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Publication structure problems:\n  - " + "\n  - ".join(problems))
    print("OK: every research achievement has authors, title, and venue in order; quotes are decorative")


if __name__ == "__main__":
    main()
