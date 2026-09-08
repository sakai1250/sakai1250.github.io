from html import escape
from pathlib import Path
import re


INDEX = Path("index.html")
PUBLICATION_LINKS = {"[Paper]", "[Program]"}
APP_CARD_MARKER = '<div class="app-card"'
ORGANIZATION_LINK_LABELS = {
    "https://github.com/RM-NAGOYASHACHIHOKO": "Organization: RM-NAGOYASHACHIHOKO",
    "https://github.com/jphacks": "Organization: JPHacks",
    "https://www.jogiken.com/": "Organization: Jogiken",
}
AWARD_LINK_BODY = '<span lang="ja">[詳細]</span><span lang="en">[Details]</span>'
AWARD_LINK_LABELS = {"[Link]", "[Details]", "[詳細]", "[詳細] [Details]", "[詳細][Details]"}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()


def normalize_publication_title(value: str) -> str:
    return normalize_text(value).rstrip(" ,.;:")


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


def remove_aria_label(anchor: str) -> str:
    opening_end = anchor.find(">")
    if opening_end == -1:
        return anchor
    opening = re.sub(r'\saria-label="[^"]*"', "", anchor[:opening_end])
    return opening + anchor[opening_end:]


def replace_anchor_body(anchor: str, body: str) -> str:
    opening_end = anchor.find(">")
    closing_start = anchor.rfind("</a>")
    if opening_end == -1 or closing_start == -1 or closing_start < opening_end:
        return anchor
    return anchor[: opening_end + 1] + body + anchor[closing_start:]


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
        title = normalize_publication_title(title_match.group(1))
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


def update_award_links(text: str) -> tuple[str, int]:
    item_pattern = re.compile(r'<li\b[^>]*data-year="[^"]+"[^>]*>[\s\S]*?</li>')
    anchor_pattern = re.compile(r'<a\b[^>]*>[\s\S]*?</a>')
    updated_count = 0

    def update_item(match: re.Match[str]) -> str:
        nonlocal updated_count
        item = match.group(0)

        def update_anchor(anchor_match: re.Match[str]) -> str:
            nonlocal updated_count
            anchor = anchor_match.group(0)
            label = normalize_text(anchor)
            if label not in AWARD_LINK_LABELS:
                return anchor
            updated_count += 1
            anchor = remove_aria_label(anchor)
            return replace_anchor_body(anchor, AWARD_LINK_BODY)

        return anchor_pattern.sub(update_anchor, item)

    return item_pattern.sub(update_item, text), updated_count


def update_app_links(text: str) -> tuple[str, int]:
    links_pattern = re.compile(
        r'(<div class="app-links">)([\s\S]*?)(</div>)'
    )
    anchor_pattern = re.compile(r'<a\b[^>]*>[\s\S]*?</a>')
    parts = text.split(APP_CARD_MARKER)
    if len(parts) == 1:
        return text, 0

    updated_count = 0
    updated_parts = [parts[0]]

    for remainder in parts[1:]:
        card = APP_CARD_MARKER + remainder
        title_match = re.search(
            r'<a\b[^>]*class="app-title"[^>]*>([\s\S]*?)</a>',
            card,
        )
        if not title_match:
            updated_parts.append(card)
            continue

        title = normalize_text(title_match.group(1))
        if not title:
            updated_parts.append(card)
            continue

        def update_links(links_match: re.Match[str]) -> str:
            nonlocal updated_count
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

        updated_parts.append(links_pattern.sub(update_links, card, count=1))

    return "".join(updated_parts), updated_count


def update_organization_links(text: str) -> tuple[str, int]:
    section_match = re.search(
        r'(<div class="badge-row" id="badges-orgs">)([\s\S]*?)(</div>)',
        text,
    )
    if not section_match:
        return text, 0

    prefix, body, suffix = section_match.groups()
    anchor_pattern = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>[\s\S]*?</a>')
    updated_count = 0

    def update_anchor(match: re.Match[str]) -> str:
        nonlocal updated_count
        href = match.group(1)
        label = ORGANIZATION_LINK_LABELS.get(href)
        if not label:
            return match.group(0)
        updated_count += 1
        return set_aria_label(match.group(0), label)

    updated_body = anchor_pattern.sub(update_anchor, body)
    start, end = section_match.span()
    return text[:start] + prefix + updated_body + suffix + text[end:], updated_count


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")
    text, publication_count = update_publication_links(text)
    text, award_count = update_award_links(text)
    text, app_count = update_app_links(text)
    text, organization_count = update_organization_links(text)

    if publication_count == 0:
        raise SystemExit("No publication resource links were found")
    if award_count == 0:
        raise SystemExit("No award detail links were found")
    if app_count == 0:
        raise SystemExit("No app resource links were found")
    if organization_count != len(ORGANIZATION_LINK_LABELS):
        raise SystemExit(
            f"Expected {len(ORGANIZATION_LINK_LABELS)} organization links, "
            f"found {organization_count}"
        )

    INDEX.write_text(text, encoding="utf-8")
    print(
        f"Kept contextual accessible names on {publication_count} publication links, "
        f"localized {award_count} award detail links, kept {app_count} app resource links, and "
        f"{organization_count} organization links"
    )


if __name__ == "__main__":
    main()
