#!/usr/bin/env python3
"""Keep Person JSON-LD research areas aligned with assets/cv.txt."""

from pathlib import Path
import json
import re

from cv_profile import read_cv_section_bullets

INDEX_PATH = Path("index.html")
CV_PATH = Path("assets/cv.txt")


def main() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    cv_text = CV_PATH.read_text(encoding="utf-8")
    areas = read_cv_section_bullets(cv_text, "RESEARCH AREAS")
    desired = json.dumps(areas, ensure_ascii=False)

    pattern = re.compile(r'("knowsAbout":\s*)\[[^\]]*\]')
    if pattern.search(text):
        text, count = pattern.subn(rf'\g<1>{desired}', text, count=1)
        if count != 1:
            raise SystemExit("Could not update Person JSON-LD knowsAbout")
    else:
        marker = re.compile(r'(\s+"image":\s*"[^"]+",\n)')
        text, count = marker.subn(
            lambda match: match.group(1) + f'    "knowsAbout": {desired},\n',
            text,
            count=1,
        )
        if count != 1:
            raise SystemExit("Could not find Person JSON-LD image insertion point")

    INDEX_PATH.write_text(text, encoding="utf-8")
    print("Updated Person JSON-LD research areas from assets/cv.txt")


if __name__ == "__main__":
    main()
