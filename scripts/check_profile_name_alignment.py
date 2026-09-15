#!/usr/bin/env python3
"""Keep the public profile name aligned with the canonical CV header."""

from pathlib import Path
import json
import re

from cv_profile import read_cv_name


def require(text: str, marker: str, source: str) -> None:
    if marker not in text:
        raise SystemExit(f"{source} is missing CV-derived profile name marker: {marker!r}")


def main() -> None:
    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    name = read_cv_name(cv_text)

    index = Path("index.html").read_text(encoding="utf-8")
    require(index, f"<title>{name} |", "index.html")
    require(index, f'property="og:title" content="{name} |', "index.html")
    require(index, f'name="twitter:title" content="{name} |', "index.html")
    require(index, f"<h1 class=\"header-name\">{name}</h1>", "index.html")
    require(index, f"<div class=\"profile-name\">{name}</div>", "index.html")
    require(index, f'content="Portrait of {name}"', "index.html")

    person_blocks = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        index,
        flags=re.DOTALL,
    )
    people = []
    for block in person_blocks:
        data = json.loads(block)
        items = data if isinstance(data, list) else [data]
        people.extend(item for item in items if isinstance(item, dict) and item.get("@type") == "Person")
    if len(people) != 1 or people[0].get("name") != name:
        raise SystemExit("Person JSON-LD name must match the assets/cv.txt profile name")

    readme = Path("README.md").read_text(encoding="utf-8")
    require(readme, f"# {name} — Portfolio", "README.md")

    llms = Path("llms.txt").read_text(encoding="utf-8")
    require(llms, f"# {name}", "llms.txt")
    require(llms, f"English name: {name}", "llms.txt")

    not_found = Path("404.html").read_text(encoding="utf-8")
    require(not_found, f"| {name}</title>", "404.html")

    print(f"OK: public profile name is derived consistently from assets/cv.txt ({name})")


if __name__ == "__main__":
    main()
