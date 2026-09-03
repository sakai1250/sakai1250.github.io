#!/usr/bin/env python3
"""Validate local fragment links and unique static/runtime section ids."""

from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit


GENERATED_SECTION_ID = re.compile(r"^(?:(?:research|engineer|portfolio)-)?section-\d+$")
DOCUMENTED_FILES = ("README.md", "llms.txt")
PORTFOLIO_HOST = "sakai1250.github.io"
URL_PATTERN = re.compile(r"https?://[^\s<>\"'`)\]]+")


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.sections = []
        self._current_tab = None
        self._current_section = None
        self._in_section_title = False
        self._capture_english_title = False
        self._div_states = []
        self._span_states = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set(attrs.get("class", "").split())

        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])

        if tag == "div":
            self._div_states.append(
                (self._current_tab, self._current_section, self._in_section_title)
            )

            element_id = attrs.get("id", "")
            if "tab-content" in classes and element_id.endswith("-content"):
                self._current_tab = element_id.removesuffix("-content")

            if "section-card" in classes and self._current_tab:
                self._current_section = {
                    "tab": self._current_tab,
                    "explicit_id": attrs.get("id", ""),
                    "english_title_parts": [],
                }
                self.sections.append(self._current_section)

            if "section-title" in classes and self._current_section is not None:
                self._in_section_title = True

        elif tag == "span":
            self._span_states.append(self._capture_english_title)
            if (
                self._current_section is not None
                and self._in_section_title
                and attrs.get("lang") == "en"
            ):
                self._capture_english_title = True

    def handle_data(self, data):
        if self._capture_english_title and self._current_section is not None:
            self._current_section["english_title_parts"].append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self._span_states:
            self._capture_english_title = self._span_states.pop()
        elif tag == "div" and self._div_states:
            (
                self._current_tab,
                self._current_section,
                self._in_section_title,
            ) = self._div_states.pop()


def parse(path):
    parser = Parser()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    return parser


def slugify_section_title(title):
    return re.sub(r"^-+|-+$", "", re.sub(r"[^a-z0-9]+", "-", title.lower().replace("&", " and ")))


def generated_section_ids(page):
    indexes = defaultdict(int)
    generated = []

    for section in page.sections:
        tab = section["tab"] or "portfolio"
        index = indexes[tab]
        indexes[tab] += 1

        current_id = section["explicit_id"]
        if current_id and not GENERATED_SECTION_ID.fullmatch(current_id):
            section_id = current_id
        else:
            english_title = "".join(section["english_title_parts"]).strip()
            slug = slugify_section_title(english_title)
            section_id = f"{tab}-{slug}" if slug else f"{tab}-section-{index}"

        generated.append((section_id, section))

    return generated


def documented_portfolio_fragments(path):
    text = Path(path).read_text(encoding="utf-8")
    for raw_url in URL_PATTERN.findall(text):
        url = raw_url.rstrip(".,;:")
        parsed = urlsplit(url)
        if (
            (parsed.hostname or "").lower() == PORTFOLIO_HOST
            and parsed.path in ("", "/")
            and parsed.fragment
        ):
            yield url, parsed.fragment


def main():
    index = parse("index.html")
    problems = []

    runtime_sections = generated_section_ids(index)
    runtime_counts = Counter(section_id for section_id, _ in runtime_sections)
    for section_id, count in sorted(runtime_counts.items()):
        if count > 1:
            problems.append(
                f"index.html: runtime section id {section_id!r} would be generated {count} times"
            )

    for source in ("index.html", "404.html"):
        page = parse(source)
        duplicate_ids = sorted(
            element_id for element_id, count in Counter(page.ids).items() if count > 1
        )
        for element_id in duplicate_ids:
            problems.append(f"{source}: duplicate id {element_id!r}")

        page_ids = set(page.ids)
        index_ids = set(index.ids)
        for href in page.hrefs:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.fragment:
                continue

            if parsed.path in ("", "/"):
                target_ids = page_ids if parsed.path == "" else index_ids
                if parsed.fragment not in target_ids:
                    problems.append(
                        f"{source}: local deep link {href!r} points to missing id {parsed.fragment!r}"
                    )

    index_ids = set(index.ids)
    for source in DOCUMENTED_FILES:
        for url, fragment in documented_portfolio_fragments(source):
            if fragment not in index_ids:
                problems.append(
                    f"{source}: documented portfolio deep link {url!r} points to missing id {fragment!r}"
                )

    if problems:
        raise SystemExit("\n".join(problems))

    print("OK: local and documented deep links resolve and static/runtime section ids are unique")


if __name__ == "__main__":
    main()
