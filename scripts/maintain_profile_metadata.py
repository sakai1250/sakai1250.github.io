#!/usr/bin/env python3
"""Keep portfolio profile metadata and visible role fallbacks aligned."""

from pathlib import Path
import re


INDEX_PATH = Path("index.html")
NOT_FOUND_PATH = Path("404.html")
README_PATH = Path("README.md")
CV_PATH = Path("assets/cv.txt")
PROFILE_FIELDS = ("GitHub", "Qiita", "LinkedIn", "Google Scholar")


def read_cv_field(cv_text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(\S+)\s*$", cv_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit(f"assets/cv.txt is missing a machine-readable {label} field")
    return match.group(1)


def read_cv_education_label(cv_text: str, prefix: str) -> str:
    match = re.search(rf"^({re.escape(prefix)}[^\n]*)$", cv_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit(f"assets/cv.txt is missing an EDUCATION entry starting with {prefix}")
    return match.group(1)


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


def maintain_structured_profile(text: str, profile_urls: list[str]) -> str:
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

    same_as_pattern = re.compile(r'("sameAs": \[\n)(.*?)(\n    \])', flags=re.DOTALL)
    match = same_as_pattern.search(text)
    if not match:
        raise SystemExit("Could not find JSON-LD sameAs profile block")
    desired_profiles = ",\n".join(f'      "{url}"' for url in profile_urls)
    if match.group(2) != desired_profiles:
        text = text[: match.start(2)] + desired_profiles + text[match.end(2) :]

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


def maintain_visible_profile_links(text: str, profile_urls: dict[str, str]) -> str:
    block_pattern = re.compile(
        r'(<div class="profile-links">)(.*?)(\n\s*</div>\n\s*</div>\n\s*</aside>)',
        flags=re.DOTALL,
    )
    match = block_pattern.search(text)
    if not match:
        raise SystemExit("Could not find visible profile links block")

    block = match.group(2)
    labels = {
        "GitHub": "GitHub",
        "Qiita": "Qiita",
        "LinkedIn": "LinkedIn",
        "Google Scholar": "Google Scholar",
    }
    for field, label in labels.items():
        anchor_pattern = re.compile(
            rf'(<a\b[^>]*\bhref=")([^"]+)("[^>]*>(?:(?!</a>).)*?{re.escape(label)}(?:(?!</a>).)*?</a>)',
            flags=re.DOTALL,
        )

        def sync_anchor(anchor_match: re.Match[str]) -> str:
            current_url = anchor_match.group(2)
            desired_url = profile_urls[field]
            if current_url == desired_url or current_url.startswith(desired_url + "&"):
                return anchor_match.group(0)
            return f"{anchor_match.group(1)}{desired_url}{anchor_match.group(3)}"

        block, count = anchor_pattern.subn(sync_anchor, block, count=1)
        if count != 1:
            raise SystemExit(f"Could not find visible {field} profile link")

    return text[: match.start(2)] + block + text[match.end(2) :]


def maintain_visible_contact(text: str, contact_email: str) -> str:
    block_pattern = re.compile(
        r'(<div class="profile-links">)(.*?)(\n\s*</div>\n\s*</div>\n\s*</aside>)',
        flags=re.DOTALL,
    )
    match = block_pattern.search(text)
    if not match:
        raise SystemExit("Could not find visible profile links block for contact")

    block = match.group(2)
    email_pattern = re.compile(
        r'(<a\b[^>]*\bhref=")mailto:[^"]+("[^>]*>(?:(?!</a>).)*?Email(?:(?!</a>).)*?</a>)',
        flags=re.DOTALL,
    )
    block, email_count = email_pattern.subn(
        rf'\g<1>mailto:{contact_email}\g<2>', block, count=1
    )
    if email_count != 1:
        raise SystemExit("Could not find visible email contact link")

    copy_pattern = re.compile(
        r'(<button\b(?=[^>]*\bclass="copy-btn")[^>]*\bdata-copy=")[^"]+("[^>]*>)',
        flags=re.DOTALL,
    )
    block, copy_count = copy_pattern.subn(
        rf'\g<1>{contact_email}\g<2>', block, count=1
    )
    if copy_count != 1:
        raise SystemExit("Could not find visible email copy control")

    return text[: match.start(2)] + block + text[match.end(2) :]


def maintain_readme_contact(text: str, contact_email: str) -> str:
    contact_pattern = re.compile(r"(?m)^- \*\*Contact:\*\* mailto:\S+\s*$")
    desired = f"- **Contact:** mailto:{contact_email}"
    text, count = contact_pattern.subn(desired, text, count=1)
    if count != 1:
        raise SystemExit("Could not find README contact quick link")
    return text


def maintain_recovery_links(
    text: str, profile_urls: dict[str, str], contact_email: str
) -> str:
    recovery_fields = ("GitHub", "LinkedIn", "Google Scholar")
    for field in recovery_fields:
        label = field
        anchor_pattern = re.compile(
            rf'(<a\b[^>]*\bhref=")([^"]+)("[^>]*>{re.escape(label)}</a>)'
        )
        text, count = anchor_pattern.subn(
            rf'\g<1>{profile_urls[field]}\g<3>', text, count=1
        )
        if count != 1:
            raise SystemExit(f"Could not find 404 {field} profile link")

    contact_pattern = re.compile(
        r'(<a\b[^>]*\bhref=")mailto:[^"]+("[^>]*><span lang="ja">連絡</span>)'
    )
    text, count = contact_pattern.subn(
        rf'\g<1>mailto:{contact_email}\g<2>', text, count=1
    )
    if count != 1:
        raise SystemExit("Could not find 404 contact link")

    return text


def maintain_visible_profile(text: str) -> str:
    role = "Ph.D. Student · Special Assistant · Computer Vision Researcher"
    empty = '<span id="typing-text"></span>'
    filled = f'<span id="typing-text">{role}</span>'
    if empty in text:
        text = text.replace(empty, filled, 1)
    elif filled not in text:
        raise SystemExit("Could not find expected visible profile role")

    old_ja_department = "理工学研究科 電気電子・情報・材料工学専攻"
    current_ja_department = "理工学研究科 電気・情報・材料・物質工学専攻"
    if old_ja_department in text:
        text = text.replace(old_ja_department, current_ja_department)
    if text.count(current_ja_department) < 2:
        raise SystemExit("Could not find current Japanese doctoral program wording")

    old_en_department = "Dept. of Electrical, Electronic, Information and Materials Engineering"
    current_en_department = "Department of Electrical, Information, and Materials Science Engineering"
    if old_en_department in text:
        text = text.replace(old_en_department, current_en_department)
    if current_en_department not in text:
        raise SystemExit("Could not find current English doctoral program wording")

    ja_pattern = re.compile(
        r"(理工学研究科 電気・情報・材料・物質工学専攻<br>\n\s*博士後期課程)(?: · Special Assistant)+"
    )
    text, ja_count = ja_pattern.subn(r"\1 · Special Assistant", text, count=1)
    if ja_count != 1:
        raise SystemExit("Could not normalize Japanese sidebar role")

    en_pattern = re.compile(
        r"(Department of Electrical, Information, and Materials Science Engineering<br>\n\s*)"
        r"Ph\.D\. (?:Course|Student)(?: · Special Assistant)+"
    )
    text, en_count = en_pattern.subn(r"\1Ph.D. Student · Special Assistant", text, count=1)
    if en_count != 1:
        raise SystemExit("Could not normalize English sidebar role")

    return text


def maintain_visible_education(text: str, cv_text: str) -> str:
    phd_label = read_cv_education_label(cv_text, "Ph.D. Course,")
    masters_label = read_cv_education_label(cv_text, "Master's Course,")
    desired_labels = (
        ("博士後期課程", f"Meijo University Graduate School, {phd_label}"),
        ("修士課程", f"Meijo University Graduate School, {masters_label}"),
    )

    section_pattern = re.compile(
        r'(<section class="section-card" id="research-education">)(.*?)(</section>)',
        flags=re.DOTALL,
    )
    section_match = section_pattern.search(text)
    if not section_match:
        raise SystemExit("Could not find visible Education section")

    section = section_match.group(2)
    for japanese_marker, desired_label in desired_labels:
        label_pattern = re.compile(
            rf'(<b lang="ja">[^<]*{re.escape(japanese_marker)}</b>\s*<b lang="en">)([^<]+)(</b>)'
        )
        section, count = label_pattern.subn(
            lambda match: f"{match.group(1)}{desired_label}{match.group(3)}",
            section,
            count=1,
        )
        if count != 1:
            raise SystemExit(f"Could not find visible Education label for {japanese_marker}")

    return text[: section_match.start(2)] + section + text[section_match.end(2) :]


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
    not_found_text = NOT_FOUND_PATH.read_text(encoding="utf-8")
    readme_text = README_PATH.read_text(encoding="utf-8")
    cv_text = CV_PATH.read_text(encoding="utf-8")
    profile_urls = {label: read_cv_field(cv_text, label) for label in PROFILE_FIELDS}
    contact_email = read_cv_field(cv_text, "Email")
    text = maintain_page_titles(text)
    text = maintain_structured_profile(text, [profile_urls[label] for label in PROFILE_FIELDS])
    text = maintain_visible_profile_links(text, profile_urls)
    text = maintain_visible_contact(text, contact_email)
    text = maintain_visible_profile(text)
    text = maintain_visible_education(text, cv_text)
    text = maintain_canonical_url(text)
    not_found_text = maintain_recovery_links(not_found_text, profile_urls, contact_email)
    readme_text = maintain_readme_contact(readme_text, contact_email)
    INDEX_PATH.write_text(text, encoding="utf-8")
    NOT_FOUND_PATH.write_text(not_found_text, encoding="utf-8")
    README_PATH.write_text(readme_text, encoding="utf-8")


if __name__ == "__main__":
    main()
