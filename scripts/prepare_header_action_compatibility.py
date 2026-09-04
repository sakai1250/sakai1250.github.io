#!/usr/bin/env python3
"""Normalize header action classes for legacy header maintenance.

`maintain_header_controls.py` predates the static CV-primary state and still
recognizes the GitHub action only when it carries `primary`. Normalize that
intermediate input here; `maintain_static_portfolio_polish.py` restores the
canonical CV-primary state later in the deterministic maintenance sequence.
"""

from pathlib import Path

PATH = Path("index.html")


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    old = text

    text = text.replace(
        'href="assets/cv.pdf" target="_blank" class="header-btn primary" rel="noopener noreferrer"',
        'href="assets/cv.pdf" target="_blank" class="header-btn" rel="noopener noreferrer"',
        1,
    )
    text = text.replace(
        'href="https://github.com/sakai1250" target="_blank" class="header-btn" rel="noopener noreferrer"',
        'href="https://github.com/sakai1250" target="_blank" class="header-btn primary" rel="noopener noreferrer"',
        1,
    )

    if 'href="https://github.com/sakai1250" target="_blank" class="header-btn primary"' not in text:
        raise SystemExit("Could not normalize GitHub header action for legacy maintenance")

    if text != old:
        PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
