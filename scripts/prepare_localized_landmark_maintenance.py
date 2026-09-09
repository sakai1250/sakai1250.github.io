#!/usr/bin/env python3
"""Normalize localized landmark labels for older maintenance transforms."""

from pathlib import Path


path = Path("index.html")
text = path.read_text(encoding="utf-8")

compatibility = {
    '<nav class="tab-nav header-tab-nav" aria-label="研究と開発" data-ja-aria-label="研究と開発" data-en-aria-label="Research and engineering">': (
        '<nav class="tab-nav header-tab-nav" aria-label="Research and engineering / 研究と開発">'
    ),
    '<div class="filter-row year-filter" role="group" aria-label="研究業績を年度で絞り込む" data-ja-aria-label="研究業績を年度で絞り込む" data-en-aria-label="Filter research outputs by year">': (
        '<div class="filter-row year-filter" role="group" aria-label="Filter research outputs by year / 研究業績を年度で絞り込む">'
    ),
    '<div class="filter-row" role="group" aria-label="開発実績を絞り込む" data-ja-aria-label="開発実績を絞り込む" data-en-aria-label="Filter engineering work">': (
        '<div class="filter-row" role="group" aria-label="Filter engineering work / 開発実績を絞り込む">'
    ),
    '<nav id="section-tab-nav" class="section-tab-nav" aria-label="ポートフォリオ内の項目" data-ja-aria-label="ポートフォリオ内の項目" data-en-aria-label="Portfolio sections"></nav>': (
        '<nav id="section-tab-nav" class="section-tab-nav" aria-label="Portfolio sections / ポートフォリオ内の項目"></nav>'
    ),
}

for localized, legacy in compatibility.items():
    if localized in text:
        text = text.replace(localized, legacy, 1)

path.write_text(text, encoding="utf-8")
