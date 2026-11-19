#!/usr/bin/env python3
"""Mark up each research achievement as authors / title / venue without changing its visible text."""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

INDEX = Path("index.html")

# Phrases inside the venue text that are emphasised as award tags. The text itself
# is never added to or removed; the phrase is only wrapped.
PUB_TAGS: tuple[str, ...] = ("Outstanding Paper Award",)

SECTION = re.compile(
    r'(<section class="section-card" id="research-research-achievements">)(.*?)(</section>)', re.S
)
ITEM = re.compile(r'<li data-year="\d{4}">.*?</li>', re.S)
ENTRY = re.compile(
    r'(?P<open><li data-year="\d{4}">)'
    r'(?P<lead>\s*<span class="badge-year">\d{4}</span>\s*)'
    r'(?P<authors>.+?)(?P<sep>[,，]\s*|\s+)'
    r'(?P<q_open>[“「])(?P<body>.*?)(?P<q_close>,?”|」)'
    r'(?P<gap>\s*)<div class="muted">(?P<venue>.*?)</div>'
    r'(?P<tail>.*?)(?P<close></li>)',
    re.S,
)
QUOTE = '<span class="pub-q" aria-hidden="true">{}</span>'


def _plain(fragment: str) -> str:
    return " ".join(html_lib.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def structure_entry(li_html: str) -> str:
    """Return the `<li>` with authors, title (quotes decorative), and venue in their own elements."""
    if 'class="pub-authors"' in li_html:
        return li_html
    match = ENTRY.fullmatch(li_html)
    if match is None:
        raise SystemExit(f"unrecognized publication entry: {_plain(li_html)[:80]}")
    venue = match["venue"]
    for tag in PUB_TAGS:
        venue = venue.replace(tag, f'<span class="pub-tag">{tag}</span>')
    title = (
        '<span class="pub-title">'
        f'{QUOTE.format(match["q_open"])}{match["body"]}{QUOTE.format(match["q_close"])}</span>'
    )
    return (
        f'{match["open"]}{match["lead"]}<span class="pub-authors">{match["authors"]}</span>'
        f'{match["sep"]}{title}{match["gap"]}<div class="muted pub-venue">{venue}</div>'
        f'{match["tail"]}{match["close"]}'
    )


def structure_achievements(html: str) -> str:
    """Structure every entry of the research achievements list; already structured entries are untouched."""
    section = SECTION.search(html)
    if section is None:
        raise SystemExit("research achievements section not found in index.html")
    body = ITEM.sub(lambda item: structure_entry(item.group(0)), section.group(2))
    return html[: section.start(2)] + body + html[section.end(2):]


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    updated = structure_achievements(text)
    if updated != text:
        INDEX.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
