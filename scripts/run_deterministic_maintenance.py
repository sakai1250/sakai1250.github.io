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
    "scripts/maintain_tabs.py",
    "scripts/maintain_stable_section_ids.py",
    "scripts/maintain_tab_deep_links.py",
    "scripts/maintain_contact_form.py",
    "scripts/maintain_header_controls.py",
    "scripts/maintain_filter_accessibility.py",
    "scripts/maintain_heading_hierarchy.py",
    "scripts/maintain_scat_grant_status.py",
    "scripts/maintain_storage_resilience.py",
    "scripts/maintain_theme_toggle_accessibility.py",
    "scripts/maintain_language_toggle_accessibility.py",
    "scripts/maintain_external_links.py",
    "scripts/maintain_resource_link_accessibility.py",
    "scripts/maintain_reduced_motion.py",
    "scripts/maintain_app_repo_links.py",
    "scripts/maintain_asset_versions.py",
    "scripts/maintain_static_fallbacks.py",
)


def compile_scripts() -> None:
    for relative_path in MAINTENANCE_SCRIPTS:
        py_compile.compile(str(ROOT / relative_path), doraise=True)


def run_scripts() -> None:
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
        help="Compile the maintenance scripts without executing them.",
    )
    args = parser.parse_args()

    if args.compile_only:
        compile_scripts()
    else:
        run_scripts()


if __name__ == "__main__":
    main()
