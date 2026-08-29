from html import escape
from pathlib import Path
import re


INDEX = Path("index.html")
PUBLICATION_LINKS = {"[Paper]", "[Program]"}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def set_aria_label(anchor: str, label: str) -> str:
    escaped = escape(label, quote=True)
    opening_end = anchor.find(">")
    if opening_end == -1:
        return anchor

    opening = anchor[:opening_end]
    body = anchor[opening_end:]
    if re.search(r'\saria-label="[^"]*"', opening):
        opening = re.sub(
            r'\saria-label="[^"]*"',
            f' aria-label="{escaped}"',
            opening,
            count=1,
        )
    else:
        opening += f' aria-label="{escaped}"'
    return opening + body


def update_publication_links(text: str) -> tuple[str, int]:
    item_pattern = re.compile(r'<li\b[^>]*data-year="[^"]+"[^>]*>[\s\S]*?</li>')
    anchor_pattern = re.compile(r'<a\b[^>]*>[\s\S]*?</a>')
    updated_count = 0

    def update_item(match: re.Match[str]) -> str:
        nonlocal updated_count
        item = match.group(0)
        title_match = re.search(r'“\s*([^”]+?)\s*”', item)
        if not title_match:
            return item
        title = normalize_text(title_match.group(1))
        if not title:
            return item

        def update_anchor(anchor_match: re.Match[str]) -> str:
            nonlocal updated_count
            anchor = anchor_match.group(0)
            label = normalize_text(anchor)
            if label not in PUBLICATION_LINKS:
                return anchor
            resource = label.strip("[]")
            updated_count += 1
            return set_aria_label(anchor, f"{resource}: {title}")

        return anchor_pattern.sub(update_anchor, item)

    return item_pattern.sub(update_item, text), updated_count


def update_app_links(text: str) -> tuple[str, int]:
    card_pattern = re.compile(
        r'(<div class="app-card"\b[\s\S]*?)(?=\n\s*<div class="app-card"\b|\n\s*</div>\n\s*</section>)'
    )
    links_pattern = re.compile(
        r'(<div class="app-links">)([\s\S]*?)(</div>)'
    )
    anchor_pattern = re.compile(r'<a\b[^>]*>[\s\S]*?</a>')
    updated_count = 0

    def update_card(match: re.Match[str]) -> str:
        nonlocal updated_count
        card = match.group(1)
        title_match = re.search(
            r'<a\b[^>]*class="app-title"[^>]*>([\s\S]*?)</a>',
            card,
        )
        if not title_match:
            return card
        title = normalize_text(title_match.group(1))
        if not title:
            return card

        def update_links(links_match: re.Match[str]) -> str:
            prefix, links, suffix = links_match.groups()

            def update_anchor(anchor_match: re.Match[str]) -> str:
                nonlocal updated_count
                anchor = anchor_match.group(0)
                resource = normalize_text(anchor)
                if not resource:
                    return anchor
                updated_count += 1
                return set_aria_label(anchor, f"{resource}: {title}")

            return prefix + anchor_pattern.sub(update_anchor, links) + suffix

        return links_pattern.sub(update_links, card, count=1)

    return card_pattern.sub(update_card, text), updated_count


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    text, publication_count = update_publication_links(text)
    text, app_count = update_app_links(text)

    if publication_count == 0:
        raise SystemExit("No publication resource links were found")
    if app_count == 0:
        raise SystemExit("No app resource links were found")

    INDEX.write_text(text, encoding="utf-8")
    print(
        f"Kept contextual accessible names on {publication_count} publication links "
        f"and {app_count} app resource links"
    )


if __name__ == "__main__":
    main()
