#!/usr/bin/env python3
"""Keep visible year-filter choices aligned with dated research/profile entries."""

from pathlib import Path
import re


html = Path("index.html").read_text(encoding="utf-8")

research_start = html.find('<div id="research-content"')
engineer_start = html.find('<div id="engineer-content"')
if research_start == -1 or engineer_start == -1 or engineer_start <= research_start:
    raise SystemExit("Could not isolate Research content")

research_html = html[research_start:engineer_start]
content_years = set(
    re.findall(r'<li\b[^>]*\bdata-year="(\d{4})"', research_html)
)
filter_years = set(
    re.findall(r'<button\b[^>]*\bdata-year="(\d{4})"', html[:research_start])
)

if not content_years:
    raise SystemExit("Research content has no dated entries")
if not filter_years:
    raise SystemExit("Year filter has no numeric choices")

missing = sorted(content_years - filter_years, reverse=True)
stale = sorted(filter_years - content_years, reverse=True)
problems = []
if missing:
    problems.append(f"year filter is missing content years: {', '.join(missing)}")
if stale:
    problems.append(f"year filter contains years with no dated content: {', '.join(stale)}")
if problems:
    raise SystemExit("\n".join(problems))

print(
    "OK: year filter covers all dated Research entries: "
    + ", ".join(sorted(content_years, reverse=True))
)
