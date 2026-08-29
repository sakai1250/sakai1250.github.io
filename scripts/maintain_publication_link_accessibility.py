"""Give generic publication action links contextual accessible names."""

from html import escape
from pathlib import Path
import re


path = Path("index.html")
text = path.read_text(encoding="utf-8")

ITEM_RE = re.compile(r"<li\b[^>]*>[\s\S]*?</li>", re.IGNORECASE)
RESOURCE_RE = re.compile(
    r"(?P<open><a\b(?P<attrs>[^>]*)>)(?P<label>\[(?:Paper|Program)\])(?P<close></a>)",
    re.IGNORECASE,
)
TITLE_RE = re.compile(r"[“\"]\s*(?P<title>[^”\"]+?)\s*[,”\"]")
ARIA_RE = re.compile(r'\saria-label="[^"]*"', re.IGNORECASE)


def contextualize_item(match: re.Match[str]) -> str:
    item = match.group(0)
    resource = RESOURCE_RE.search(item)
    if not resource:
        return item

    title_match = TITLE_RE.search(item[: resource.start()])
    if not title_match:
        raise SystemExit("Could not extract publication title for a Paper/Program link")

    title = re.sub(r"\s+", " ", title_match.group("title")).strip()
    kind = resource.group("label").strip("[]").capitalize()
    accessible_name = escape(f"{kind}: {title}", quote=True)

    attrs = ARIA_RE.sub("", resource.group("attrs"))
    opening = f'<a{attrs} aria-label="{accessible_name}">'
    replacement = opening + resource.group("label") + resource.group("close")
    return item[: resource.start()] + replacement + item[resource.end() :]


updated = ITEM_RE.sub(contextualize_item, text)
path.write_text(updated, encoding="utf-8")
