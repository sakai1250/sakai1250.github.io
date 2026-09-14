#!/usr/bin/env python3
"""Keep the Person JSON-LD portrait aligned with the canonical social image."""

from pathlib import Path
import re

INDEX_PATH = Path("index.html")
PROFILE_IMAGE_URL = "https://sakai1250.github.io/assets/avatar.jpg"


def main() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")

    person_pattern = re.compile(
        r'(<script type="application/ld\+json">\s*\{.*?"@type":\s*"Person".*?"url":\s*"https://sakai1250\.github\.io/",)(.*?)(\n\s*"sameAs":\s*\[)',
        flags=re.DOTALL,
    )
    match = person_pattern.search(text)
    if not match:
        raise SystemExit("Could not find Person JSON-LD profile URL before sameAs")

    middle = match.group(2)
    image_entry = f'\n    "image": "{PROFILE_IMAGE_URL}",'
    image_pattern = re.compile(r'\n\s*"image":\s*"[^"]*",?')

    if image_pattern.search(middle):
        middle = image_pattern.sub(image_entry, middle, count=1)
    else:
        middle = image_entry + middle

    updated = text[: match.start(2)] + middle + text[match.end(2) :]
    INDEX_PATH.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
