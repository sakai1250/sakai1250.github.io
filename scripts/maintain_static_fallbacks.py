#!/usr/bin/env python3
"""Keep visible portfolio fallback counts and update dates aligned."""

from pathlib import Path
import html
import re
import subprocess
import xml.etree.ElementTree as ET


INDEX_PATH = Path("index.html")
SITEMAP_PATH = Path("sitemap.xml")
TRACKED_PAGE_FILES = ("index.html", "main.js", "style.css", "effects.js")
HOME_URL = "https://sakai1250.github.io/"


def source_update_date() -> str:
    dates = []
    for tracked_file in TRACKED_PAGE_FILES:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", tracked_file],
            check=True,
            capture_output=True,
            text=True,
        )
        value = result.stdout.strip()
        if value:
            dates.append(value)

    if not dates:
        raise SystemExit("Could not resolve a source update date")

    latest = max(dates)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", latest):
        raise SystemExit(f"Unexpected source update date: {latest}")
    return latest


def update_sitemap(lastmod_value: str) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    ns = {"sm": namespace}
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()

    for url in root.findall("sm:url", ns):
        loc = url.find("sm:loc", ns)
        lastmod = url.find("sm:lastmod", ns)
        if loc is not None and loc.text == HOME_URL and lastmod is not None:
            lastmod.text = lastmod_value
            tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)
            return

    raise SystemExit("Could not resolve homepage lastmod in sitemap.xml")


def plain_text(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def section_block(text: str, english_title: str) -> str:
    section_pattern = re.compile(
        r'<section\b[^>]*class="[^"]*\bsection-card\b[^"]*"[^>]*>[\s\S]*?</section>',
        re.IGNORECASE,
    )
    heading_pattern = re.compile(
        r'<h2\b[^>]*class="[^"]*\bsection-title\b[^"]*"[^>]*>([\s\S]*?)</h2>',
        re.IGNORECASE,
    )
    english_title_pattern = re.compile(
        r'<span\s+lang="en">([\s\S]*?)</span>',
        re.IGNORECASE,
    )

    for match in section_pattern.finditer(text):
        block = match.group(0)
        heading = heading_pattern.search(block)
        if not heading:
            continue
        title_match = english_title_pattern.search(heading.group(1))
        if title_match and plain_text(title_match.group(1)) == english_title:
            return block

    raise SystemExit(f"Could not find section: {english_title}")


def update_index(lastmod_value: str) -> dict[str, int]:
    text = INDEX_PATH.read_text(encoding="utf-8")
    counts = {
        "stat-papers": len(re.findall(r"<li\b", section_block(text, "Research Achievements"))),
        "stat-awards": len(re.findall(r"<li\b", section_block(text, "Awards"))),
        "stat-apps": len(
            re.findall(
                r'<div\s+class="app-card"(?:\s|>)',
                section_block(text, "My Apps & Services"),
            )
        ),
    }
    if any(value <= 0 for value in counts.values()):
        raise SystemExit(f"Unexpected zero count: {counts}")

    for element_id, value in counts.items():
        pattern = rf'(<div\s+class="stat-value"\s+id="{re.escape(element_id)}">)[^<]*(</div>)'
        text, replacements = re.subn(pattern, rf"\g<1>{value}\g<2>", text, count=1)
        if replacements != 1:
            raise SystemExit(f"Could not update {element_id}")

    text, ja_count = re.subn(
        r'(<span\s+id="last-updated">)\d{4}-\d{2}-\d{2}(</span>)',
        rf"\g<1>{lastmod_value}\g<2>",
        text,
        count=1,
    )
    text, en_count = re.subn(
        r'(<span\s+id="last-updated-en">)\d{4}-\d{2}-\d{2}(</span>)',
        rf"\g<1>{lastmod_value}\g<2>",
        text,
        count=1,
    )
    if ja_count != 1 or en_count != 1:
        raise SystemExit("Could not update both footer dates")

    INDEX_PATH.write_text(text, encoding="utf-8")
    return counts


def main() -> None:
    latest = source_update_date()
    update_sitemap(latest)
    counts = update_index(latest)
    print(f"Portfolio stats: {counts}; source/footer/sitemap date: {latest}")


if __name__ == "__main__":
    main()
