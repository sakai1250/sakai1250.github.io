#!/usr/bin/env python3
import html
import json
import re
from pathlib import Path

from cv_profile import read_cv_field, read_cv_header_profile


def require(text, needle, source):
    if needle not in text:
        raise SystemExit(f"{source} is missing required profile content: {needle}")


def require_casefold(text, needle, source):
    if needle.casefold() not in text.casefold():
        raise SystemExit(f"{source} is missing required profile content: {needle}")


def normalize_text(text):
    return " ".join(text.split())


def visible_html_text(fragment):
    return normalize_text(html.unescape(re.sub(r"<[^>]+>", " ", fragment)))


def read_person_json_ld(index_text):
    blocks = re.findall(
        r'<script\s+type=["\']application/ld\+json["\']\s*>(.*?)</script>',
        index_text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for block in blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"index.html contains invalid JSON-LD: {exc}") from exc
        if data.get("@type") == "Person":
            return data
    raise SystemExit("index.html is missing Person JSON-LD")


def main():
    llms_path = Path("llms.txt")
    cv_path = Path("assets/cv.txt")
    index_path = Path("index.html")
    not_found_path = Path("404.html")
    main_js_path = Path("main.js")
    readme_path = Path("README.md")

    llms_text = llms_path.read_text(encoding="utf-8")
    cv_text = cv_path.read_text(encoding="utf-8")
    index_text = index_path.read_text(encoding="utf-8")
    not_found_text = not_found_path.read_text(encoding="utf-8")
    main_js_text = main_js_path.read_text(encoding="utf-8")
    readme_text = readme_path.read_text(encoding="utf-8")

    cv_roles, cv_affiliation = read_cv_header_profile(cv_text)
    role_text = " | ".join(cv_roles)
    expected_summary_role = f"> {role_text} @ {cv_affiliation}"
    expected_current_role = f"- Current role: {role_text} @ {cv_affiliation}"

    required_identity = [
        "# Taigo Sakai",
        expected_summary_role,
        "English name: Taigo Sakai",
        "Japanese name: 坂井 泰吾",
        "Publication name: T. Sakai",
        expected_current_role,
    ]
    for item in required_identity:
        require(llms_text, item, "llms.txt")

    required_routes = [
        "https://sakai1250.github.io/assets/cv.txt",
        "https://sakai1250.github.io/assets/cv.pdf",
        "https://sakai1250.github.io/",
        "https://sakai1250.github.io/#research-content",
        "https://sakai1250.github.io/#research-research-achievements",
        "https://sakai1250.github.io/#research-education",
        "https://sakai1250.github.io/#research-awards",
        "https://sakai1250.github.io/#research-internship",
        "https://sakai1250.github.io/#engineer-content",
        "https://sakai1250.github.io/#engineer-my-apps-and-services",
        "https://github.com/sakai1250/sakai1250.github.io",
    ]
    for route in required_routes:
        require(llms_text, route, "llms.txt")

    contact_email = read_cv_field(cv_text, "Email")
    contact_mailto = f"mailto:{contact_email}"
    profile_fields = ("GitHub", "Qiita", "LinkedIn", "Google Scholar")
    required_profiles = [read_cv_field(cv_text, label) for label in profile_fields]
    recovery_profiles = [
        read_cv_field(cv_text, label)
        for label in ("GitHub", "LinkedIn", "Google Scholar")
    ]
    for profile in required_profiles:
        require(llms_text, profile, "llms.txt")
    require(llms_text, contact_mailto, "llms.txt")

    require_casefold(cv_text, "Taigo Sakai", "assets/cv.txt")
    require(cv_text, "https://sakai1250.github.io/", "assets/cv.txt")

    # Publication resources in the machine-readable CV should stay attached to
    # the same publication in the human-facing portfolio. Checking only that a
    # URL exists somewhere in index.html would miss accidentally swapped links.
    cv_publications = re.findall(
        r'^\d+\.\s+[^\n]*?"([^"\n]+)"[^\n]*\n\s+(Paper|Program):\s+(https?://\S+)\s*$',
        cv_text,
        flags=re.MULTILINE,
    )
    if not cv_publications:
        raise SystemExit("assets/cv.txt is missing publication resource links")

    publication_items = re.findall(r"<li\b[^>]*>.*?</li>", index_text, flags=re.DOTALL | re.IGNORECASE)
    for title, resource_label, publication_url in cv_publications:
        linked_items = [
            item
            for item in publication_items
            if f'href="{publication_url}"' in item
        ]
        if len(linked_items) != 1:
            raise SystemExit(
                "index.html must contain exactly one publication item for CV resource: "
                f"{publication_url} (found {len(linked_items)})"
            )
        item_text = visible_html_text(linked_items[0])
        if normalize_text(title).casefold() not in item_text.casefold():
            raise SystemExit(
                f"index.html {resource_label} link is attached to the wrong publication: "
                f"{title} -> {publication_url}"
            )

    # Human-facing recovery and contact routes must stay aligned with the
    # machine-readable profile so stale links do not survive on secondary pages.
    require(index_text, contact_mailto, "index.html")
    require(not_found_text, contact_mailto, "404.html")
    require(main_js_text, contact_mailto, "main.js")
    require(readme_text, contact_mailto, "README.md")
    for profile in recovery_profiles:
        require(not_found_text, profile, "404.html")

    # Search engines and professional profile consumers rely on the Person JSON-LD.
    # Parse it as JSON so malformed metadata cannot pass as a simple string match.
    person = read_person_json_ld(index_text)
    expected_fields = {
        "name": "Taigo Sakai",
        "url": "https://sakai1250.github.io/",
    }
    for field, expected in expected_fields.items():
        if person.get(field) != expected:
            raise SystemExit(f"index.html Person JSON-LD has unexpected {field}: {person.get(field)!r}")

    expected_job_title = " / ".join(cv_roles)
    if person.get("jobTitle") != expected_job_title:
        raise SystemExit(
            "index.html Person JSON-LD jobTitle must match assets/cv.txt: "
            f"expected={expected_job_title!r}, actual={person.get('jobTitle')!r}"
        )

    same_as = person.get("sameAs")
    if not isinstance(same_as, list):
        raise SystemExit("index.html Person JSON-LD sameAs must be a list")
    for profile in required_profiles:
        if profile not in same_as:
            raise SystemExit(f"index.html Person JSON-LD sameAs is missing profile: {profile}")

    affiliation = person.get("affiliation")
    if not isinstance(affiliation, dict) or affiliation.get("name") != cv_affiliation:
        raise SystemExit("index.html Person JSON-LD affiliation must match assets/cv.txt")

    print("OK: portfolio, recovery navigation, CV, structured metadata, and machine-readable sources expose a consistent professional profile")


if __name__ == "__main__":
    main()
