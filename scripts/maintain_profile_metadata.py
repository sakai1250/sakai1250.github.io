#!/usr/bin/env python3
"""Keep portfolio profile metadata and visible role fallbacks aligned."""

from pathlib import Path
import html
import re

from maintain_social_profile import build_search_description


INDEX_PATH = Path("index.html")
NOT_FOUND_PATH = Path("404.html")
README_PATH = Path("README.md")
LLMS_PATH = Path("llms.txt")
SECURITY_POLICY_PATH = Path("SECURITY.md")
SECURITY_CONTACT_PATH = Path(".well-known/security.txt")
MAIN_JS_PATH = Path("main.js")
CV_PATH = Path("assets/cv.txt")
PROFILE_FIELDS = ("GitHub", "Qiita", "LinkedIn", "Google Scholar")


def read_cv_field(cv_text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*(\S+)\s*$", cv_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit(f"assets/cv.txt is missing a machine-readable {label} field")
    return match.group(1)


def read_cv_header_profile(cv_text: str) -> tuple[list[str], str]:
    lines = [line.strip() for line in cv_text.splitlines() if line.strip()]
    role_indexes = [
        index
        for index, line in enumerate(lines[:-1])
        if " | " in line and not re.match(r"^[A-Za-z][A-Za-z ]*:\s*", line)
    ]
    if len(role_indexes) != 1:
        raise SystemExit("assets/cv.txt must contain exactly one role header followed by affiliation")

    role_index = role_indexes[0]
    roles = [role.strip() for role in lines[role_index].split("|") if role.strip()]
    affiliation = lines[role_index + 1].split(",", 1)[0].strip()
    if len(roles) < 2 or not affiliation or ":" in affiliation:
        raise SystemExit("assets/cv.txt has an incomplete role or affiliation header")
    return roles, affiliation


def build_sidebar_roles(cv_text: str) -> tuple[str, str]:
    roles, _ = read_cv_header_profile(cv_text)
    sidebar_roles = roles[:2]
    if not sidebar_roles:
        raise SystemExit("assets/cv.txt is missing roles for the profile sidebar")

    localized_roles = {
        "Ph.D. Student": "博士後期課程",
    }
    japanese = " · ".join(localized_roles.get(role, role) for role in sidebar_roles)
    english = " · ".join(sidebar_roles)
    return japanese, english


def read_cv_education_label(cv_text: str, prefix: str) -> str:
    match = re.search(rf"^({re.escape(prefix)}[^\n]*)$", cv_text, flags=re.MULTILINE)
    if not match:
        raise SystemExit(f"assets/cv.txt is missing an EDUCATION entry starting with {prefix}")
    return match.group(1)


def build_page_title(cv_text: str) -> str:
    roles, _ = read_cv_header_profile(cv_text)
    role_title = roles[0] if len(roles) == 1 else ", ".join(roles[:-1]) + " & " + roles[-1]
    return f"Taigo Sakai | {role_title}"


def maintain_page_titles(text: str, cv_text: str) -> str:
    desired_title = html.escape(build_page_title(cv_text), quote=True)
    patterns = (
        (re.compile(r"<title>Taigo Sakai \| [^<]+</title>"), f"<title>{desired_title}</title>", "document title"),
        (re.compile(r'<meta property="og:title" content="Taigo Sakai \| [^"]+">'), f'<meta property="og:title" content="{desired_title}">', "Open Graph title"),
        (re.compile(r'<meta name="twitter:title" content="Taigo Sakai \| [^"]+">'), f'<meta name="twitter:title" content="{desired_title}">', "Twitter title"),
    )
    for pattern, replacement, label in patterns:
        text, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not find expected {label}")
    return text


def maintain_structured_profile(text: str, profile_urls: list[str], cv_text: str) -> str:
    cv_roles, cv_affiliation = read_cv_header_profile(cv_text)
    desired_title = f'"jobTitle": "{" / ".join(cv_roles)}"'
    title_pattern = re.compile(r'"jobTitle":\s*"[^"]*"')
    text, title_count = title_pattern.subn(desired_title, text, count=1)
    if title_count != 1:
        raise SystemExit("Could not find expected JSON-LD jobTitle")

    old_affiliation = '"alumniOf": "Meijo University"'
    new_affiliation = (
        f'"affiliation": {{"@type": "CollegeOrUniversity", "name": "{cv_affiliation}"}}'
    )
    if old_affiliation in text:
        text = text.replace(old_affiliation, new_affiliation, 1)
    elif new_affiliation not in text:
        affiliation_pattern = re.compile(
            r'"affiliation":\s*\{"@type":\s*"CollegeOrUniversity",\s*"name":\s*"[^"]*"\}'
        )
        text, affiliation_count = affiliation_pattern.subn(new_affiliation, text, count=1)
        if affiliation_count != 1:
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

    desired_description = html.escape(build_search_description(cv_text), quote=True)
    description_patterns = (
        (
            re.compile(r'<meta name="description"\s+content="[^"]*">', flags=re.DOTALL),
            f'<meta name="description"\n    content="{desired_description}">',
            "search description",
        ),
        (
            re.compile(r'<meta property="og:description"\s+content="[^"]*">', flags=re.DOTALL),
            f'<meta property="og:description"\n    content="{desired_description}">',
            "Open Graph description",
        ),
    )
    for pattern, replacement, label in description_patterns:
        text, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            raise SystemExit(f"Could not find expected {label}")

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
    contact_pattern = re.compile(
        r"(?m)^- \*\*Contact:\*\* (?:mailto:\S+|\[[^\]]+\]\(mailto:[^)]+\))[ \t]*$"
    )
    desired = f"- **Contact:** [{contact_email}](mailto:{contact_email})"
    text, count = contact_pattern.subn(desired, text, count=1)
    if count != 1:
        raise SystemExit("Could not find README contact quick link")
    return text


def maintain_llms_contact(text: str, contact_email: str) -> str:
    contact_pattern = re.compile(r"(?m)^- Contact: mailto:\S+[ \t]*$")
    text, count = contact_pattern.subn(
        f"- Contact: mailto:{contact_email}", text, count=1
    )
    if count != 1:
        raise SystemExit("Could not find llms.txt contact field")
    return text


def maintain_security_policy_contact(text: str, contact_email: str) -> str:
    contact_pattern = re.compile(
        r"(please report it privately by email to `)[^`]+(`\.)"
    )
    text, count = contact_pattern.subn(
        rf"\g<1>{contact_email}\g<2>", text, count=1
    )
    if count != 1:
        raise SystemExit("Could not find SECURITY.md private contact")
    return text


def maintain_security_contact(text: str, contact_email: str) -> str:
    contact_pattern = re.compile(r"(?m)^Contact: mailto:\S+[ \t]*$")
    text, count = contact_pattern.subn(
        f"Contact: mailto:{contact_email}", text, count=1
    )
    if count != 1:
        raise SystemExit("Could not find security.txt contact field")
    return text


def maintain_form_fallback_contact(text: str, contact_email: str) -> str:
    contact_pattern = re.compile(r"(link\.href = 'mailto:)[^']+(';)")
    text, count = contact_pattern.subn(
        rf"\g<1>{contact_email}\g<2>", text, count=1
    )
    if count != 1:
        raise SystemExit("Could not find contact form email fallback")
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


def maintain_visible_profile(text: str, cv_text: str) -> str:
    roles, _ = read_cv_header_profile(cv_text)
    role = " · ".join(roles)
    role_pattern = re.compile(r'(<span id="typing-text">)[^<]*(</span>)')
    text, role_count = role_pattern.subn(
        lambda match: f"{match.group(1)}{html.escape(role)}{match.group(2)}",
        text,
        count=1,
    )
    if role_count != 1:
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

    japanese_sidebar_role, english_sidebar_role = build_sidebar_roles(cv_text)
    ja_pattern = re.compile(
        r"(理工学研究科 電気・情報・材料・物質工学専攻<br>\n\s*)[^\n<]+"
    )
    text, ja_count = ja_pattern.subn(
        lambda match: f"{match.group(1)}{html.escape(japanese_sidebar_role)}",
        text,
        count=1,
    )
    if ja_count != 1:
        raise SystemExit("Could not synchronize Japanese sidebar role")

    en_pattern = re.compile(
        r"(Department of Electrical, Information, and Materials Science Engineering<br>\n\s*)[^\n<]+"
    )
    text, en_count = en_pattern.subn(
        lambda match: f"{match.group(1)}{html.escape(english_sidebar_role)}",
        text,
        count=1,
    )
    if en_count != 1:
        raise SystemExit("Could not synchronize English sidebar role")

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
    llms_text = LLMS_PATH.read_text(encoding="utf-8")
    security_policy_text = SECURITY_POLICY_PATH.read_text(encoding="utf-8")
    security_contact_text = SECURITY_CONTACT_PATH.read_text(encoding="utf-8")
    main_js_text = MAIN_JS_PATH.read_text(encoding="utf-8")
    cv_text = CV_PATH.read_text(encoding="utf-8")
    profile_urls = {label: read_cv_field(cv_text, label) for label in PROFILE_FIELDS}
    contact_email = read_cv_field(cv_text, "Email")
    text = maintain_page_titles(text, cv_text)
    text = maintain_structured_profile(
        text, [profile_urls[label] for label in PROFILE_FIELDS], cv_text
    )
    text = maintain_visible_profile_links(text, profile_urls)
    text = maintain_visible_contact(text, contact_email)
    text = maintain_visible_profile(text, cv_text)
    text = maintain_visible_education(text, cv_text)
    text = maintain_canonical_url(text)
    not_found_text = maintain_recovery_links(not_found_text, profile_urls, contact_email)
    readme_text = maintain_readme_contact(readme_text, contact_email)
    llms_text = maintain_llms_contact(llms_text, contact_email)
    security_policy_text = maintain_security_policy_contact(security_policy_text, contact_email)
    security_contact_text = maintain_security_contact(security_contact_text, contact_email)
    main_js_text = maintain_form_fallback_contact(main_js_text, contact_email)
    INDEX_PATH.write_text(text, encoding="utf-8")
    NOT_FOUND_PATH.write_text(not_found_text, encoding="utf-8")
    README_PATH.write_text(readme_text, encoding="utf-8")
    LLMS_PATH.write_text(llms_text, encoding="utf-8")
    SECURITY_POLICY_PATH.write_text(security_policy_text, encoding="utf-8")
    SECURITY_CONTACT_PATH.write_text(security_contact_text, encoding="utf-8")
    MAIN_JS_PATH.write_text(main_js_text, encoding="utf-8")


if __name__ == "__main__":
    main()
