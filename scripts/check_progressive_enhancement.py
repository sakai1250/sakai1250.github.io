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


def extract_braced_block(text, marker):
    marker_start = text.find(marker)
    if marker_start < 0:
        return None

    brace_start = text.find("{", marker_start + len(marker))
    if brace_start < 0:
        return None

    depth = 0
    for index in range(brace_start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[marker_start:index + 1]
    return None


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocking_external_stylesheets = []
        self.in_qiita_list = False
        self.qiita_profile_fallback = False
        self.primary_tab_classes = {}
        self.primary_tab_aria_current = {}
        self.toc_hidden = {}

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        attr_names = {name for name, _ in attrs}
        element_id = values.get("id")
        if tag == "a" and element_id in {"research-tab", "engineer-tab"}:
            self.primary_tab_classes[element_id] = set(values.get("class", "").split())
            self.primary_tab_aria_current[element_id] = values.get("aria-current")
        if element_id in {"toc-fab", "toc-menu"}:
            self.toc_hidden[element_id] = "hidden" in attr_names
        if tag == "ul" and values.get("id") == "qiita-list":
            self.in_qiita_list = True
        if (
            tag == "a"
            and self.in_qiita_list
            and values.get("href") == "https://qiita.com/sakai1250"
        ):
            self.qiita_profile_fallback = True
        if tag != "link":
            return
        rel = values.get("rel", "").split()
        href = values.get("href", "")
        if (
            "stylesheet" in rel
            and href.startswith(("https://", "http://"))
            and values.get("media") != "print"
        ):
            self.blocking_external_stylesheets.append(href)

    def handle_endtag(self, tag):
        if tag == "ul" and self.in_qiita_list:
            self.in_qiita_list = False


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
if not parser.qiita_profile_fallback:
    problems.append("Qiita section has no usable static profile fallback.")

research_tab_classes = parser.primary_tab_classes.get("research-tab", set())
engineer_tab_classes = parser.primary_tab_classes.get("engineer-tab", set())
if "active" not in research_tab_classes:
    problems.append("Research primary navigation is not visibly active in static HTML.")
if "active" in engineer_tab_classes:
    problems.append("Engineering primary navigation must not be active by default in static HTML.")
if parser.primary_tab_aria_current.get("research-tab") != "true":
    problems.append('Research primary navigation must expose aria-current="true" in static HTML.')
if parser.primary_tab_aria_current.get("engineer-tab") is not None:
    problems.append("Engineering primary navigation must not expose aria-current by default in static HTML.")
if "i.removeAttribute('aria-current');" not in main:
    problems.append(
        "Enhanced primary tabs must remove static aria-current before exposing aria-selected state."
    )

for element_id in ("toc-fab", "toc-menu"):
    if parser.toc_hidden.get(element_id) is not True:
        problems.append(
            f"#{element_id} must be hidden in static HTML until JavaScript finishes TOC setup."
        )

required_toc_runtime_markers = (
    "safeInit(initTOCAndReveal, 'TOC');",
    "function initTOCAndReveal() {",
    "    initTOC();",
    "    if (!fab || !menu || !fab.hasAttribute('aria-controls')) return;",
    "    fab.hidden = false;",
    "    menu.hidden = false;",
)
for marker in required_toc_runtime_markers:
    if marker not in main:
        problems.append(
            "TOC controls must be revealed only after successful TOC runtime initialization."
        )
        break

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

mobile_media_marker = (
    "/* Mobile rendering safety: keep core content off decorative compositing layers. */\n"
    "@media (max-width: 768px)"
)
mobile_media_block = extract_braced_block(style, mobile_media_marker)
if mobile_media_block is None:
    problems.append(
        "Scoped mobile rendering safety block is missing or malformed."
    )
else:
    required_mobile_rules = {
        "body::before { display: none !important; }":
            "Mobile CSS must disable the decorative body::before layer.",
        "-webkit-backdrop-filter: none !important;":
            "Mobile CSS must disable -webkit-backdrop-filter in the safety block.",
        "backdrop-filter: none !important;":
            "Mobile CSS must disable backdrop-filter in the safety block.",
        ".header-bar { background: var(--bg-2) !important; }":
            "Mobile CSS must give the header an opaque fallback background.",
    }
    for rule, message in required_mobile_rules.items():
        if rule not in mobile_media_block:
            problems.append(message)

if problems:
    raise SystemExit("Progressive enhancement check failed:\n- " + "\n- ".join(problems))

print("Progressive enhancement check passed.")
