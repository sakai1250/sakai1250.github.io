#!/usr/bin/env python3
"""Keep portfolio profile metadata and visible role fallbacks aligned."""

from pathlib import Path
import re


INDEX_PATH = Path("index.html")


def maintain_page_titles(text: str) -> str:
    old_title = "Taigo Sakai | Ph.D. Student &amp; Computer Vision Researcher"
    new_title = "Taigo Sakai | Ph.D. Student, Special Assistant &amp; Computer Vision Researcher"

    title_fields = (
        f"<title>{old_title}</title>",
        f'<meta property="og:title" content="{old_title}">',
        f'<meta name="twitter:title" content="{old_title}">',
    )
    updated_fields = (
        f"<title>{new_title}</title>",
        f'<meta property="og:title" content="{new_title}">',
        f'<meta name="twitter:title" content="{new_title}">',
    )

    for old, new in zip(title_fields, updated_fields):
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"Could not find expected profile title field: {old}")

    return text


def maintain_structured_profile(text: str) -> str:
    old_title = '"jobTitle": "Ph.D. Student / Researcher / Engineer"'
    new_title = '"jobTitle": "Ph.D. Student / Special Assistant / Researcher / Engineer"'
    if old_title in text:
        text = text.replace(old_title, new_title, 1)
    elif new_title not in text:
        raise SystemExit("Could not find expected JSON-LD jobTitle")

    old_affiliation = '"alumniOf": "Meijo University"'
    new_affiliation = (
        '"affiliation": {"@type": "CollegeOrUniversity", "name": "Meijo University"}'
    )
    if old_affiliation in text:
        text = text.replace(old_affiliation, new_affiliation, 1)
    elif new_affiliation not in text:
        raise SystemExit("Could not find expected JSON-LD affiliation")

    old_context = '"@context": "http://schema.org"'
    new_context = '"@context": "https://schema.org"'
    if old_context in text:
        text = text.replace(old_context, new_context, 1)
    elif new_context not in text:
        raise SystemExit("Could not find expected JSON-LD schema context")

    scholar_url = "https://scholar.google.com/citations?user=eS-5wrQAAAAJ"
    jsonld_start = text.find('<script type="application/ld+json">')
    jsonld_end = text.find("</script>", jsonld_start)
    if jsonld_start == -1 or jsonld_end == -1:
        raise SystemExit("Could not find JSON-LD profile block")
    jsonld = text[jsonld_start:jsonld_end]
    if scholar_url not in jsonld:
        marker = '      "https://www.linkedin.com/in/sakai1250"\n'
        if marker not in jsonld:
            raise SystemExit("Could not find JSON-LD profile-link insertion point")
        text = text.replace(
            marker,
            '      "https://www.linkedin.com/in/sakai1250",\n'
            f'      "{scholar_url}"\n',
            1,
        )

    old_description = (
        "名城大学大学院 博士後期課程 坂井泰吾のポートフォリオ。"
        "Deep Learning, Computer Visionの研究や、iOS/Webアプリ開発の実績を紹介しています。"
    )
    new_description = (
        "名城大学大学院 博士後期課程・Special Assistant 坂井泰吾のポートフォリオ。"
        "Computer Vision、Continual Learning、Multi-View Trackingの研究とiOS/Web開発実績を紹介しています。"
    )
    count = text.count(old_description)
    if count:
        text = text.replace(old_description, new_description)
    elif text.count(new_description) < 2:
        raise SystemExit("Could not find expected profile meta descriptions")

    return text


def maintain_visible_profile(text: str) -> str:
    role = "Ph.D. Student · Special Assistant · Computer Vision Researcher"
    empty = '<span id="typing-text"></span>'
    filled = f'<span id="typing-text">{role}</span>'
    if empty in text:
        text = text.replace(empty, filled, 1)
    elif filled not in text:
        raise SystemExit("Could not find expected visible profile role")

    ja_pattern = re.compile(
        r"(理工学研究科 電気電子・情報・材料工学専攻<br>\n\s*博士後期課程)(?: · Special Assistant)+"
    )
    text, ja_count = ja_pattern.subn(r"\1 · Special Assistant", text, count=1)
    if ja_count != 1:
        raise SystemExit("Could not normalize Japanese sidebar role")

    en_pattern = re.compile(
        r"(Dept\. of Electrical, Electronic, Information and Materials Engineering<br>\n\s*)"
        r"Ph\.D\. (?:Course|Student)(?: · Special Assistant)+"
    )
    text, en_count = en_pattern.subn(r"\1Ph.D. Student · Special Assistant", text, count=1)
    if en_count != 1:
        raise SystemExit("Could not normalize English sidebar role")

    return text


def maintain_canonical_url(text: str) -> str:
    canonical = '  <link rel="canonical" href="https://sakai1250.github.io/">\n'
    if canonical not in text:
        marker = '  <meta property="og:url" content="https://sakai1250.github.io/">\n'
        if marker not in text:
            raise SystemExit("Could not find canonical insertion point")
        text = text.replace(marker, marker + canonical, 1)
    return text


def main() -> None:
    text = INDEX_PATH.read_text(encoding="utf-8")
    text = maintain_page_titles(text)
    text = maintain_structured_profile(text)
    text = maintain_visible_profile(text)
    text = maintain_canonical_url(text)
    INDEX_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
