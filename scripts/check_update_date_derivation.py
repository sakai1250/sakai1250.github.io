#!/usr/bin/env python3
"""Regression checks for visitor-facing update-date classification."""

from datetime import datetime
from unittest.mock import patch

from maintain_static_fallbacks import TRACKED_PAGE_FILES, git_update_date, normalize_freshness_fields


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
    # CV-only edits must advance the public date, even if HTML/CSS/JS are unchanged.
    def source_timestamp(path: str) -> datetime:
        return datetime.fromisoformat(
            "2026-10-01T12:00:00+09:00" if path == "assets/cv.txt" else "2026-09-19T12:00:00+09:00"
        )

    with patch("maintain_static_fallbacks.effective_git_update_timestamp", side_effect=source_timestamp):
        assert git_update_date(*TRACKED_PAGE_FILES) == "2026-10-01", (
            "CV source changes must advance the homepage update date"
        )

    print("Update-date derivation regression checks passed")


if __name__ == "__main__":
    main()
