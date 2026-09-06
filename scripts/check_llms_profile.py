#!/usr/bin/env python3
import json
import re
from pathlib import Path


def require(text, needle, source):
    if needle not in text:
        raise SystemExit(f"{source} is missing required profile content: {needle}")


def require_casefold(text, needle, source):
    if needle.casefold() not in text.casefold():
        raise SystemExit(f"{source} is missing required profile content: {needle}")


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

    required_identity = [
        "# Taigo Sakai",
        "English name: Taigo Sakai",
        "Japanese name: 坂井 泰吾",
        "Publication name: T. Sakai",
        "Current role: Ph.D. student and Special Assistant at Meijo University",
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

    contact_email = "263441505@ccmailg.meijo-u.ac.jp"
    contact_mailto = f"mailto:{contact_email}"
    required_profiles = [
        "https://github.com/sakai1250",
        "https://qiita.com/sakai1250",
        "https://www.linkedin.com/in/sakai1250",
        "https://scholar.google.com/citations?user=eS-5wrQAAAAJ",
    ]
    recovery_profiles = [
        "https://github.com/sakai1250",
        "https://www.linkedin.com/in/sakai1250",
        "https://scholar.google.com/citations?user=eS-5wrQAAAAJ",
    ]
    for profile in required_profiles:
        require(llms_text, profile, "llms.txt")
    require(llms_text, contact_mailto, "llms.txt")

    shared_identity = [
        "Taigo Sakai",
        "Ph.D. Student",
        "Special Assistant",
        "Meijo University",
    ]
    for item in shared_identity:
        require_casefold(cv_text, item, "assets/cv.txt")
    require(cv_text, "https://sakai1250.github.io/", "assets/cv.txt")

    for profile in required_profiles:
        require(cv_text, profile, "assets/cv.txt")
    require(cv_text, f"Email: {contact_email}", "assets/cv.txt")

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

    job_title = str(person.get("jobTitle", ""))
    for role in ("Ph.D. Student", "Special Assistant", "Researcher", "Engineer"):
        if role.casefold() not in job_title.casefold():
            raise SystemExit(f"index.html Person JSON-LD jobTitle is missing role: {role}")

    same_as = person.get("sameAs")
    if not isinstance(same_as, list):
        raise SystemExit("index.html Person JSON-LD sameAs must be a list")
    for profile in required_profiles:
        if profile not in same_as:
            raise SystemExit(f"index.html Person JSON-LD sameAs is missing profile: {profile}")

    affiliation = person.get("affiliation")
    if not isinstance(affiliation, dict) or affiliation.get("name") != "Meijo University":
        raise SystemExit("index.html Person JSON-LD affiliation must identify Meijo University")

    print("OK: portfolio, recovery navigation, CV, structured metadata, and machine-readable sources expose a consistent professional profile")


if __name__ == "__main__":
    main()
