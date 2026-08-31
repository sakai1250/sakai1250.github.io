#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import re


INDEX = Path("index.html")
STYLE = Path("style.css")
MAIN = Path("main.js")

index = INDEX.read_text(encoding="utf-8")
style = STYLE.read_text(encoding="utf-8")
main = MAIN.read_text(encoding="utf-8")
problems = []


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocking_external_stylesheets = []

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        values = dict(attrs)
        rel = values.get("rel", "").split()
        href = values.get("href", "")
        if (
            "stylesheet" in rel
            and href.startswith(("https://", "http://"))
            and values.get("media") != "print"
        ):
            self.blocking_external_stylesheets.append(href)


if 'id="loading-screen"' in index:
    problems.append(
        "Blocking loading screen detected. Static portfolio content must remain visible even if JavaScript fails."
    )
if "initLoader" in main:
    problems.append(
        "JavaScript loader logic detected. Core portfolio content must not depend on JavaScript removing an overlay."
    )
if "classList.add('reveal-item')" in main or 'classList.add("reveal-item")' in main:
    problems.append(
        "JavaScript hides core content for reveal effects. Core portfolio content must be visible before JavaScript runs."
    )

parser = LinkParser()
parser.feed(index)
if parser.blocking_external_stylesheets:
    problems.append(
        "Render-blocking external stylesheet detected: "
        + ", ".join(parser.blocking_external_stylesheets)
    )

required_index_snippets = {
    'id="main-content"': "Static main content is missing from index.html.",
    'id="research-content" class="tab-content active"': "Research content is not statically visible by default.",
    'id="engineer-content" class="tab-content"': "Engineering content is missing from the static document.",
    'id="research-tab" data-tab="research" href="#research-content"': "Research primary navigation is not a usable static page link.",
    'id="engineer-tab" data-tab="engineer" href="#engineer-content"': "Engineering primary navigation is not a usable static page link.",
    'href="assets/cv.pdf"': "Static CV link is missing from index.html.",
    'href="https://github.com/sakai1250"': "Static GitHub profile link is missing from index.html.",
    'href="https://scholar.google.com/citations?user=eS-5wrQAAAAJ': "Static Google Scholar link is missing from index.html.",
}
for snippet, message in required_index_snippets.items():
    if snippet not in index:
        problems.append(message)

if re.search(r'id="(?:research|engineer)-content"[^>]*\shidden(?:\s*=|>)', index):
    problems.append(
        "A primary content panel is hidden in static HTML and would disappear when JavaScript fails."
    )
if re.search(r"\.tab-content[^}]*display\s*:\s*none", style):
    problems.append("CSS hides primary tab content before JavaScript runs.")
if ".header-actions .header-btn.primary { display: none; }" in style:
    problems.append(
        "Mobile CSS hides the primary GitHub action and makes it depend on JavaScript."
    )

if problems:
    raise SystemExit("Progressive enhancement check failed:\n- " + "\n- ".join(problems))

print("Progressive enhancement check passed.")
