#!/usr/bin/env python3
"""Run the dependency-free deterministic portfolio maintenance transforms."""

from __future__ import annotations

import argparse
import py_compile
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAINTENANCE_SCRIPTS = (
    "scripts/maintain_profile_metadata.py",
    "scripts/maintain_research_awards.py",
    "scripts/maintain_toc_fallback.py",
    "scripts/maintain_modal_accessibility.py",
    "scripts/maintain_tabs.py",
    "scripts/maintain_stable_section_ids.py",
    "scripts/maintain_contact_form.py",
    "scripts/maintain_header_controls.py",
    "scripts/maintain_social_profile.py",
    "scripts/maintain_app_thumbnail_dimensions.py",
    "scripts/maintain_tab_deep_links.py",
    "scripts/maintain_header_stat_links.py",
    "scripts/maintain_filter_accessibility.py",
    "scripts/maintain_heading_hierarchy.py",
    "scripts/maintain_scat_grant_status.py",
    "scripts/maintain_storage_resilience.py",
    "scripts/maintain_theme_preference_persistence.py",
    "scripts/maintain_theme_toggle_accessibility.py",
    "scripts/maintain_language_toggle_accessibility.py",
    "scripts/maintain_localized_landmark_labels.py",
    "scripts/maintain_utility_control_localization.py",
    "scripts/maintain_external_links.py",
    "scripts/maintain_resource_link_accessibility.py",
    "scripts/maintain_reduced_motion.py",
    "scripts/maintain_contextual_share_link.py",
    "scripts/maintain_app_repo_links.py",
    "scripts/maintain_static_portfolio_polish.py",
    "scripts/maintain_asset_versions.py",
    "scripts/maintain_static_fallbacks.py",
)


def validate_maintenance_registry() -> None:
    discovered = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "scripts").glob("maintain_*.py")
    }
    registered = set(MAINTENANCE_SCRIPTS)

    missing = sorted(discovered - registered)
    stale = sorted(registered - discovered)
    if not missing and not stale:
        return

    details = []
    if missing:
        details.append("unregistered maintenance scripts: " + ", ".join(missing))
    if stale:
        details.append("missing registered scripts: " + ", ".join(stale))
    raise SystemExit("Maintenance registry mismatch: " + "; ".join(details))


def compile_scripts() -> None:
    validate_maintenance_registry()
    for script_path in sorted((ROOT / "scripts").glob("*.py")):
        py_compile.compile(str(script_path), doraise=True)


def run_scripts() -> None:
    validate_maintenance_registry()
    for relative_path in MAINTENANCE_SCRIPTS:
        subprocess.run(
            [sys.executable, str(ROOT / relative_path)],
            cwd=ROOT,
            check=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Validate the maintenance registry and compile every Python script under scripts/ without executing it.",
    )
    args = parser.parse_args()

    if args.compile_only:
        compile_scripts()
    else:
        run_scripts()


if __name__ == "__main__":
    main()
