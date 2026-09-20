#!/usr/bin/env python3
"""Regression checks for visitor-facing update-date classification."""

from maintain_static_fallbacks import normalize_freshness_fields


def page(date: str, research_area: str = "Continual Learning") -> str:
    return f'''<!doctype html>
<script type="application/ld+json">{{"knowsAbout":["{research_area}"]}}</script>
<footer>
  <span id="last-updated">{date}</span>
  <span id="last-updated-en">{date}</span>
</footer>
'''


def main() -> None:
    before = page("2026-09-17")
    freshness_only = page("2026-09-19")
    semantic_change = page("2026-09-19", "Multi-View Detection & Tracking")

    assert normalize_freshness_fields(before) == normalize_freshness_fields(freshness_only), (
        "footer-date-only changes must not count as visitor-facing updates"
    )
    assert normalize_freshness_fields(before) != normalize_freshness_fields(semantic_change), (
        "semantic homepage changes must still advance the public update date"
    )
    print("Update-date derivation regression checks passed")


if __name__ == "__main__":
    main()
