from __future__ import annotations

import subprocess
import sys

CHECKS = [
    "scripts/check_app_repo_links.py",
    "scripts/check_thumbnail_cache_policy.py",
    "scripts/check_contextual_share_localization.py",
    "scripts/check_local_deep_links.py",
    "scripts/check_site_integrity.py",
    "scripts/check_profile_name_alignment.py",
    "scripts/check_css_asset_references.py",
    "scripts/check_research_award_alignment.py",
    "scripts/check_control_accessible_names.py",
    "scripts/check_utility_control_localization.py",
    "scripts/check_form_control_names.py",
    "scripts/check_new_tab_link_security.py",
    "scripts/check_progressive_enhancement.py",
    "scripts/check_security_contact.py",
    "scripts/check_structured_profile.py",
    "scripts/check_sidebar_role_derivation.py",
    "scripts/check_social_profile_derivation.py",
    "scripts/check_llms_profile.py",
    "scripts/check_year_filter_coverage.py",
    "scripts/check_python_runtime_alignment.py",
    "scripts/check_node_runtime_alignment.py",
    "scripts/check_github_action_pins.py",
    "scripts/check_workflow_permissions.py",
    "scripts/check_workflow_timeouts.py",
    "scripts/check_validation_docs.py",
]

MAINTAINED_PATHS = [
    "index.html",
    "404.html",
    "main.js",
    "style.css",
    "sitemap.xml",
    "README.md",
    "llms.txt",
    "SECURITY.md",
    ".well-known/security.txt",
]


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, check=True)


def main() -> None:
    python = sys.executable
    run(python, "scripts/run_deterministic_maintenance.py", "--compile-only")
    run("node", "--check", "main.js")
    for check in CHECKS:
        run(python, check)

    run(python, "scripts/run_deterministic_maintenance.py")
    run("git", "diff", "--exit-code", "--", *MAINTAINED_PATHS)
    run(python, "scripts/maintain_static_fallbacks.py")
    run("git", "diff", "--exit-code", "--", "index.html", "sitemap.xml")


if __name__ == "__main__":
    main()
