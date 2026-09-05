#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import json


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = False
        self.blocks = []
        self.current = []
        self.in_title = False
        self.title_seen = False
        self.title_parts = []
        self.meta = {}
        self.canonical_urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.capture = True
            self.current = []
        elif tag == "title" and not self.title_seen:
            self.in_title = True
            self.title_seen = True
        elif tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            content = attrs.get("content")
            if key and content is not None:
                self.meta.setdefault(key, []).append(content)
        elif tag == "link":
            rel_tokens = set(attrs.get("rel", "").lower().split())
            href = attrs.get("href")
            if "canonical" in rel_tokens and href:
                self.canonical_urls.append(href)

    def handle_data(self, data):
        if self.capture:
            self.current.append(data)
        if self.in_title:
            self.title_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.capture:
            self.blocks.append("".join(self.current))
            self.capture = False
            self.current = []
        elif tag == "title" and self.in_title:
            self.in_title = False


def single_value(values, label):
    if len(values) != 1:
        raise SystemExit(f"expected exactly one {label}, found {len(values)}")
    value = values[0].strip()
    if not value:
        raise SystemExit(f"{label} must not be empty")
    return value


def main():
    parser = JsonLdParser()
    parser.feed(Path("index.html").read_text(encoding="utf-8"))

    people = []
    for raw in parser.blocks:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON-LD: {exc}")
        items = data if isinstance(data, list) else [data]
        people.extend(
            item
            for item in items
            if isinstance(item, dict) and item.get("@type") == "Person"
        )

    if len(people) != 1:
        raise SystemExit(
            f"expected exactly one Person JSON-LD object, found {len(people)}"
        )

    person = people[0]
    required_text = ["name", "jobTitle", "url"]
    for key in required_text:
        if not str(person.get(key, "")).strip():
            raise SystemExit(f"Person JSON-LD is missing {key}")

    job_title = str(person["jobTitle"])
    required_roles = ("Ph.D. Student", "Special Assistant")
    for required_role in required_roles:
        if required_role not in job_title:
            raise SystemExit(
                f"Person JSON-LD jobTitle is missing current role: {required_role}"
            )

    if person["url"] != "https://sakai1250.github.io/":
        raise SystemExit(f'unexpected profile URL: {person["url"]}')

    canonical_url = single_value(parser.canonical_urls, "canonical URL")
    og_url = single_value(parser.meta.get("og:url", []), "og:url")
    if canonical_url != person["url"] or og_url != person["url"]:
        raise SystemExit(
            "canonical URL, og:url, and Person JSON-LD url must match: "
            f"canonical={canonical_url!r}, og:url={og_url!r}, person={person['url']!r}"
        )

    document_title = "".join(parser.title_parts).strip()
    if not document_title:
        raise SystemExit("document title must not be empty")
    og_title = single_value(parser.meta.get("og:title", []), "og:title")
    twitter_title = single_value(parser.meta.get("twitter:title", []), "twitter:title")
    if len({document_title, og_title, twitter_title}) != 1:
        raise SystemExit(
            "document, Open Graph, and Twitter titles must match: "
            f"title={document_title!r}, og:title={og_title!r}, twitter:title={twitter_title!r}"
        )

    description = single_value(parser.meta.get("description", []), "meta description")
    og_description = single_value(parser.meta.get("og:description", []), "og:description")
    twitter_description = single_value(
        parser.meta.get("twitter:description", []), "twitter:description"
    )
    if description != og_description:
        raise SystemExit(
            "meta and Open Graph descriptions must match: "
            f"description={description!r}, og:description={og_description!r}"
        )
    required_twitter_terms = (
        "Ph.D. Student",
        "Special Assistant",
        "Meijo University",
        "Computer Vision",
    )
    missing_twitter_terms = [
        term for term in required_twitter_terms if term not in twitter_description
    ]
    if missing_twitter_terms:
        raise SystemExit(
            "Twitter description is missing current professional context: "
            + ", ".join(missing_twitter_terms)
        )

    og_image = single_value(parser.meta.get("og:image", []), "og:image")
    twitter_image = single_value(parser.meta.get("twitter:image", []), "twitter:image")
    if og_image != twitter_image:
        raise SystemExit(
            "Open Graph and Twitter preview images must match: "
            f"og:image={og_image!r}, twitter:image={twitter_image!r}"
        )

    og_image_alt = single_value(parser.meta.get("og:image:alt", []), "og:image:alt")
    twitter_image_alt = single_value(
        parser.meta.get("twitter:image:alt", []), "twitter:image:alt"
    )
    if og_image_alt != twitter_image_alt:
        raise SystemExit(
            "Open Graph and Twitter preview image alt text must match: "
            f"og:image:alt={og_image_alt!r}, twitter:image:alt={twitter_image_alt!r}"
        )

    same_as = person.get("sameAs")
    if not isinstance(same_as, list):
        raise SystemExit("Person JSON-LD sameAs must be a list")
    required_profiles = {
        "https://github.com/sakai1250",
        "https://qiita.com/sakai1250",
        "https://www.linkedin.com/in/sakai1250",
        "https://scholar.google.com/citations?user=eS-5wrQAAAAJ",
    }
    missing_profiles = sorted(required_profiles - set(same_as))
    if missing_profiles:
        raise SystemExit(
            f"Person JSON-LD is missing professional profile links: {missing_profiles}"
        )

    affiliation = person.get("affiliation")
    if not isinstance(affiliation, dict) or affiliation.get("name") != "Meijo University":
        raise SystemExit(
            "Person JSON-LD must identify Meijo University as the current affiliation"
        )
    if affiliation.get("@type") != "CollegeOrUniversity":
        raise SystemExit("Person JSON-LD affiliation must use CollegeOrUniversity")

    if "alumniOf" in person:
        raise SystemExit(
            "Person JSON-LD uses alumniOf for a current affiliation; use affiliation instead"
        )

    cv_text = Path("assets/cv.txt").read_text(encoding="utf-8")
    if person["name"].upper() not in cv_text.upper():
        raise SystemExit("assets/cv.txt is missing the JSON-LD person name")
    for required_role in required_roles:
        if required_role not in cv_text:
            raise SystemExit(f"assets/cv.txt is missing current role: {required_role}")
    if affiliation["name"] not in cv_text:
        raise SystemExit("assets/cv.txt is missing the current affiliation")
    if person["url"] not in cv_text:
        raise SystemExit("assets/cv.txt is missing the canonical portfolio URL")
    missing_cv_profiles = sorted(
        profile for profile in required_profiles if profile not in cv_text
    )
    if missing_cv_profiles:
        raise SystemExit(
            "assets/cv.txt is missing professional profile links from JSON-LD: "
            + ", ".join(missing_cv_profiles)
        )

    print(
        "OK: public metadata, localized social previews, Person JSON-LD, and assets/cv.txt contain a consistent professional identity"
    )


if __name__ == "__main__":
    main()
