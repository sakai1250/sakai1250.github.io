#!/usr/bin/env python3
"""Keep visible portfolio fallback counts and sitemap update dates aligned."""

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import html
import re
import subprocess
import xml.etree.ElementTree as ET


INDEX_PATH = Path("index.html")
SITEMAP_PATH = Path("sitemap.xml")
# Public "last updated" dates should describe visitor-facing content, not changes to
# maintenance code that leave the generated page unchanged.
TRACKED_PAGE_FILES = (
    "index.html",
    "main.js",
    "style.css",
    "assets/data.json",
)
HOME_URL = "https://sakai1250.github.io/"
SITE_TIMEZONE = ZoneInfo("Asia/Tokyo")
OPTIMIZER_COMMIT_MESSAGE = "chore: update portfolio assets and optimized images"
OPTIMIZER_PARENT_WINDOW = timedelta(minutes=30)
STATIC_SITEMAP_FILES = {
    "https://sakai1250.github.io/assets/cv.pdf": "assets/cv.pdf",
    "https://sakai1250.github.io/assets/cv.txt": "assets/cv.txt",
    "https://sakai1250.github.io/llms.txt": "llms.txt",
}
QIITA_FALLBACK = '''<li><a href="https://qiita.com/sakai1250" target="_blank" rel="noopener noreferrer"><span lang="ja">Qiitaプロフィールを見る</span><span lang="en">Open Qiita profile</span></a></li>'''


def parse_git_timestamp(value: str, label: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Unexpected {label} timestamp: {value}") from exc
    if timestamp.tzinfo is None:
        raise SystemExit(f"{label.capitalize()} timestamp has no timezone: {value}")
    return timestamp


def effective_git_update_timestamp(tracked_file: str) -> datetime | None:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H%x1f%cI%x1f%s", "--", tracked_file],
        check=True,
        capture_output=True,
        text=True,
    )
    value = result.stdout.strip()
    if not value:
        return None

    try:
        commit_sha, timestamp_value, subject = value.split("\x1f", 2)
    except ValueError as exc:
        raise SystemExit(f"Unexpected git log record for {tracked_file}: {value}") from exc

    timestamp = parse_git_timestamp(timestamp_value, "source update")
    if subject != OPTIMIZER_COMMIT_MESSAGE:
        return timestamp

    parent_result = subprocess.run(
        ["git", "show", "-s", "--format=%cI", f"{commit_sha}^"],
        check=True,
        capture_output=True,
        text=True,
    )
    parent_value = parent_result.stdout.strip()
    if not parent_value:
        return timestamp

    parent_timestamp = parse_git_timestamp(parent_value, "optimizer parent")
    elapsed = timestamp - parent_timestamp
    if not (timedelta(0) <= elapsed <= OPTIMIZER_PARENT_WINDOW):
        return timestamp

    previous_result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", f"{commit_sha}^", "--", tracked_file],
        check=True,
        capture_output=True,
        text=True,
    )
    previous_value = previous_result.stdout.strip()
    if previous_value:
        return parse_git_timestamp(previous_value, "previous content update")

    return parent_timestamp


def git_update_date(*tracked_files: str) -> str:
    dates = []
    for tracked_file in tracked_files:
        timestamp = effective_git_update_timestamp(tracked_file)
        if timestamp is not None:
            dates.append(timestamp.astimezone(SITE_TIMEZONE).date())

    if not dates:
        raise SystemExit(f"Could not resolve an update date for {tracked_files}")

    return max(dates).isoformat()


def update_sitemap(lastmods: dict[str, str]) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    ns = {"sm": namespace}
    tree = ET.parse(SITEMAP_PATH)
    root = tree.getroot()
    updated = set()

    for url in root.findall("sm:url", ns):
        loc = url.find("sm:loc", ns)
        lastmod = url.find("sm:lastmod", ns)
        if loc is None or not loc.text or loc.text not in lastmods:
            continue
        if lastmod is None:
            raise SystemExit(f"Sitemap entry has no lastmod: {loc.text}")
        lastmod.text = lastmods[loc.text]
        updated.add(loc.text)

    missing = sorted(set(lastmods) - updated)
    if missing:
        raise SystemExit(f"Could not resolve sitemap entries: {missing}")

    tree.write(SITEMAP_PATH, encoding="UTF-8", xml_declaration=True)
    sitemap_text = SITEMAP_PATH.read_text(encoding="utf-8")
    SITEMAP_PATH.write_text(sitemap_text.rstrip("\n") + "\n", encoding="utf-8")


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

    for tab_id, is_current in (("research", True), ("engineer", False)):
        pattern = re.compile(rf'<a\b(?=[^>]*\bid="{tab_id}-tab")[^>]*>')
        match = pattern.search(text)
        if not match:
            raise SystemExit(f"Could not find static {tab_id} primary navigation link")
        tag = re.sub(r'\s+aria-current="[^"]*"', '', match.group(0))
        if is_current:
            tag = tag[:-1] + ' aria-current="true">'
        text = text[:match.start()] + tag + text[match.end():]

    qiita_pattern = re.compile(
        r'(<ul\s+class="repo-list"\s+id="qiita-list">)\s*<li>[\s\S]*?</li>\s*(</ul>)',
        re.IGNORECASE,
    )
    text, qiita_count = qiita_pattern.subn(
        rf"\1\n                {QIITA_FALLBACK}\n              \2",
        text,
        count=1,
    )
    if qiita_count != 1:
        raise SystemExit("Could not update the static Qiita fallback")

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
    homepage_date = git_update_date(*TRACKED_PAGE_FILES)
    sitemap_lastmods = {HOME_URL: homepage_date}
    sitemap_lastmods.update(
        {url: git_update_date(path) for url, path in STATIC_SITEMAP_FILES.items()}
    )
    update_sitemap(sitemap_lastmods)
    counts = update_index(homepage_date)
    print(
        f"Portfolio stats: {counts}; homepage date: {homepage_date}; "
        f"sitemap dates: {sitemap_lastmods}"
    )


if __name__ == "__main__":
    main()
