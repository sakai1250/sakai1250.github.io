#!/usr/bin/env python3
"""Validate local fragment links and unique ids in portfolio HTML files."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])


def parse(path):
    parser = Parser()
    parser.feed(Path(path).read_text(encoding="utf-8"))
    return parser


def main():
    index = parse("index.html")
    problems = []

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

    if problems:
        raise SystemExit("\n".join(problems))

    print("OK: local deep links resolve and HTML ids are unique")


if __name__ == "__main__":
    main()
