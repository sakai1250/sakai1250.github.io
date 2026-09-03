#!/usr/bin/env python3
"""Keep header portfolio counts linked to their corresponding evidence sections."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLE = ROOT / "style.css"

LINKS = {
    "stat-papers": "#research-research-achievements",
    "stat-awards": "#research-awards",
    "stat-apps": "#engineer-my-apps-and-services",
}


def link_stat_block(text: str, stat_id: str, href: str) -> str:
    marker = f'id="{stat_id}"'
    marker_index = text.find(marker)
    if marker_index < 0:
        raise SystemExit(f"Could not find {stat_id} in index.html")

    block_start = text.rfind('            <div class="stat-item">', 0, marker_index)
    if block_start < 0:
        # Already maintained: verify the expected link rather than rewriting it.
        anchor_start = text.rfind('            <a class="stat-item"', 0, marker_index)
        if anchor_start >= 0:
            tag_end = text.find('>', anchor_start)
            opening_tag = text[anchor_start:tag_end]
            if f'href="{href}"' in opening_tag:
                return text
        raise SystemExit(f"Could not find the stat-item wrapper for {stat_id}")

    block_end = text.find('            </div>', marker_index)
    if block_end < 0:
        raise SystemExit(f"Could not find the stat-item closing tag for {stat_id}")
    block_end += len('            </div>')

    block = text[block_start:block_end]
    linked = block.replace(
        '            <div class="stat-item">',
        f'            <a class="stat-item" href="{href}">',
        1,
    )
    linked = linked.rsplit('            </div>', 1)[0] + '            </a>'
    return text[:block_start] + linked + text[block_end:]


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    for stat_id, href in LINKS.items():
        html = link_stat_block(html, stat_id, href)
    INDEX.write_text(html, encoding="utf-8")

    css = STYLE.read_text(encoding="utf-8")
    marker = "/* Header stat navigation */"
    rules = """

/* Header stat navigation */
.stat-item[href] {
  color: inherit;
  text-decoration: none;
}

.stat-item[href]:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 4px;
  border-radius: 4px;
}
"""
    if marker not in css:
        css = css.rstrip() + rules + "\n"
        STYLE.write_text(css, encoding="utf-8")

    # Guard the contract used by the links: these IDs must remain static.
    current = INDEX.read_text(encoding="utf-8")
    for stat_id, href in LINKS.items():
        target_id = href.removeprefix("#")
        if f'id="{target_id}"' not in current:
            raise SystemExit(f"Header stat target is not static: {target_id}")
        if f'class="stat-item" href="{href}"' not in current:
            raise SystemExit(f"Header stat link was not maintained: {stat_id}")


if __name__ == "__main__":
    main()
