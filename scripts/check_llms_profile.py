#!/usr/bin/env python3
from pathlib import Path


def require(text, needle, source):
    if needle not in text:
        raise SystemExit(f"{source} is missing required profile content: {needle}")


def require_casefold(text, needle, source):
    if needle.casefold() not in text.casefold():
        raise SystemExit(f"{source} is missing required profile content: {needle}")


def main():
    llms_path = Path("llms.txt")
    cv_path = Path("assets/cv.txt")

    llms_text = llms_path.read_text(encoding="utf-8")
    cv_text = cv_path.read_text(encoding="utf-8")

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
    required_profiles = [
        "https://github.com/sakai1250",
        "https://qiita.com/sakai1250",
        "https://www.linkedin.com/in/sakai1250",
        "https://scholar.google.com/citations?user=eS-5wrQAAAAJ",
    ]
    for profile in required_profiles:
        require(llms_text, profile, "llms.txt")
    require(llms_text, f"mailto:{contact_email}", "llms.txt")

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

    print("OK: llms.txt and assets/cv.txt expose a consistent professional profile")


if __name__ == "__main__":
    main()
