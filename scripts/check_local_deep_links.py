#!/usr/bin/env python3
"""Validate local fragment links in the portfolio HTML files."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
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
        for href in page.hrefs:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.fragment:
                continue

            if parsed.path in ("", "/"):
                target_ids = page.ids if parsed.path == "" else index.ids
                if parsed.fragment not in target_ids:
                    problems.append(
                        f"{source}: local deep link {href!r} points to missing id {parsed.fragment!r}"
                    )

    if problems:
        raise SystemExit("\n".join(problems))

    print("OK: local tab deep links resolve to existing ids")


if __name__ == "__main__":
    main()
