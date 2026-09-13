#!/usr/bin/env python3
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import xml.etree.ElementTree as ET

root = Path('.')
html_files = [root / 'index.html', root / '404.html']
problems = []
total_ids = 0
total_refs = 0
html_ids = {}

# The modal image is populated from the selected app card immediately before the
# dialog opens. Keeping its initial src empty avoids shipping a fake placeholder
# asset, so this one dynamic target is intentionally exempt from the generic
# empty-src check. All other empty href/src values remain invalid.
DYNAMIC_EMPTY_SRC_IDS = {'modal-img'}


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.empty_refs = []
        self.aria_id_refs = []
        self.img_without_alt = []
        self.html_lang = None
        self.main_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                ref = attrs[key]
                self.refs.append(ref)
                is_dynamic_modal_image = (
                    tag == 'img'
                    and key == 'src'
                    and attrs.get('id') in DYNAMIC_EMPTY_SRC_IDS
                )
                if (not ref or not ref.strip()) and not is_dynamic_modal_image:
                    self.empty_refs.append(f'<{tag}> {key}')
        for key in ('aria-labelledby', 'aria-describedby', 'aria-controls'):
            if key in attrs:
                self.aria_id_refs.extend((key, ref) for ref in attrs[key].split())

        if tag == 'html':
            self.html_lang = attrs.get('lang', '').strip()
        elif tag == 'main':
            self.main_count += 1
        elif tag == 'img' and 'alt' not in attrs:
            self.img_without_alt.append(attrs.get('src', '<inline image>'))


for html_path in html_files:
    if not html_path.exists():
        problems.append(f'missing HTML file {html_path}')
        continue

    parser = Parser()
    parser.feed(html_path.read_text(encoding='utf-8'))

    duplicates = sorted({x for x in parser.ids if parser.ids.count(x) > 1})
    if duplicates:
        problems.append(f'{html_path}: duplicate HTML ids {duplicates}')

    if not parser.html_lang:
        problems.append(f'{html_path}: <html> is missing a lang attribute')
    if parser.main_count != 1:
        problems.append(
            f'{html_path}: expected exactly one <main> landmark; found {parser.main_count}'
        )
    if parser.img_without_alt:
        problems.append(f'{html_path}: images missing alt attributes {parser.img_without_alt}')
    if parser.empty_refs:
        problems.append(f'{html_path}: empty href/src references {parser.empty_refs}')

    ids = set(parser.ids)
    for attr, ref in parser.aria_id_refs:
        if ref not in ids:
            problems.append(f'{html_path}: {attr} references missing id #{ref}')

    html_ids[html_path.name] = ids
    total_ids += len(ids)
    total_refs += len(parser.refs)

    for ref in parser.refs:
        if not ref or ref.startswith(('http://', 'https://', 'mailto:', 'tel:', 'data:', 'javascript:')):
            continue
        if ref.startswith('#'):
            anchor = ref[1:]
            if anchor and anchor not in ids:
                problems.append(f'{html_path}: missing anchor {ref}')
            continue
        parsed_ref = urlsplit(ref)
        path = parsed_ref.path
        if path == '/' and parsed_ref.fragment:
            index_ids = html_ids.get('index.html', set())
            if parsed_ref.fragment not in index_ids:
                problems.append(
                    f'{html_path}: root deep link #{parsed_ref.fragment} has no matching id in index.html'
                )
            continue
        if not path or path == '/':
            continue
        target = root / path.lstrip('/')
        if not target.exists():
            problems.append(f'{html_path}: missing file {path}')

readme_path = root / 'README.md'
if readme_path.exists():
    readme_text = readme_path.read_text(encoding='utf-8')
    portfolio_fragments = sorted(set(re.findall(
        r'https://sakai1250\.github\.io/#([A-Za-z0-9_-]+)',
        readme_text,
    )))
    index_ids = html_ids.get('index.html', set())
    for fragment in portfolio_fragments:
        if fragment not in index_ids:
            problems.append(
                f'README.md: portfolio deep link #{fragment} has no matching id in index.html'
            )

required = [
    'assets/cv.pdf',
    'assets/cv.txt',
    'assets/avatar.jpg',
    'assets/data.json',
    'style.css',
    'main.js',
    '404.html',
    'robots.txt',
    'sitemap.xml',
    'llms.txt',
]
for path in required:
    if not (root / path).exists():
        problems.append(f'missing required asset {path}')

# The copy control is bilingual in its idle and success states, so failure
# feedback must follow the same language state. Guard both the generated markup
# and the JavaScript lookup so a maintenance change cannot reintroduce an
# English-only `Error` state.
index_path = root / 'index.html'
main_path = root / 'main.js'
maintenance_path = root / 'scripts/maintain_storage_resilience.py'
if index_path.exists():
    index_text = index_path.read_text(encoding='utf-8')
    for expected in (
        'data-ja-error="コピー失敗"',
        'data-en-error="Copy failed"',
    ):
        if expected not in index_text:
            problems.append(f'index.html: copy control is missing {expected}')
    if 'data-error="Error"' in index_text:
        problems.append('index.html: copy control restored the English-only data-error="Error"')

if main_path.exists():
    main_text = main_path.read_text(encoding='utf-8')
    if "getAttribute(`data-${lang}-error`)" not in main_text:
        problems.append('main.js: copy failure feedback is not selected from the current language')
    if "getAttribute('data-error') || 'Error'" in main_text:
        problems.append('main.js: copy failure feedback restored the English-only Error fallback')

if maintenance_path.exists():
    maintenance_text = maintenance_path.read_text(encoding='utf-8')
    if "data-${lang}-error" not in maintenance_text:
        problems.append('maintain_storage_resilience.py: localized copy failure lookup is missing')
    if "const error = btn.getAttribute('data-error') || 'Error';" in maintenance_text:
        problems.append('maintain_storage_resilience.py: English-only copy failure source was restored')

data_path = root / 'assets/data.json'
if data_path.exists():
    try:
        data = json.loads(data_path.read_text(encoding='utf-8'))
        apps = data.get('apps', {})
        if not isinstance(apps, dict) or not apps:
            problems.append('assets/data.json: apps must be a non-empty object')
        else:
            repo_pattern = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
            for repo, app in apps.items():
                if not repo_pattern.fullmatch(repo):
                    problems.append(f'assets/data.json: invalid app repository key {repo!r}')
                if not isinstance(app, dict):
                    problems.append(f'assets/data.json: app {repo!r} must be an object')
                    continue
                if not str(app.get('desc', '')).strip():
                    problems.append(f'assets/data.json: app {repo!r} has an empty description')
                image = str(app.get('img', '')).strip()
                if not image:
                    problems.append(f'assets/data.json: app {repo!r} has no thumbnail')
                elif not (root / image).exists():
                    problems.append(f'assets/data.json: app {repo!r} thumbnail is missing: {image}')

        badges = data.get('badges', {})
        if not isinstance(badges, dict):
            problems.append('assets/data.json: badges must be an object')
        else:
            for group, items in badges.items():
                if not isinstance(items, list):
                    problems.append(f'assets/data.json: badge group {group!r} must be a list')
                    continue
                for index, badge in enumerate(items):
                    if not isinstance(badge, dict):
                        problems.append(f'assets/data.json: badge {group}[{index}] must be an object')
                        continue
                    if not str(badge.get('alt', '')).strip():
                        problems.append(f'assets/data.json: badge {group}[{index}] has empty alt text')
                    src = str(badge.get('src', '')).strip()
                    if not src.startswith(('https://', 'http://')):
                        problems.append(f'assets/data.json: badge {group}[{index}] has invalid src {src!r}')
    except (json.JSONDecodeError, OSError) as exc:
        problems.append(f'assets/data.json: cannot parse generated data: {exc}')

cv_text_path = root / 'assets/cv.txt'
if cv_text_path.exists():
    cv_text = cv_text_path.read_text(encoding='utf-8')
    required_sections = [
        'SUMMARY',
        'RESEARCH AREAS',
        'TECHNICAL SKILLS',
        'EXPERIENCE',
        'EDUCATION',
        'PUBLICATIONS',
        'ACADEMIC SERVICE',
        'AWARDS & GRANTS',
        'CERTIFICATIONS',
    ]
    for section in required_sections:
        if f'\n{section}\n' not in cv_text:
            problems.append(f'assets/cv.txt: missing section {section!r}')

    publication_numbers = [
        int(match.group(1))
        for match in re.finditer(r'(?m)^(\d+)\.\s+', cv_text)
    ]
    expected_publications = list(range(1, len(publication_numbers) + 1))
    if not publication_numbers:
        problems.append('assets/cv.txt: publications must contain at least one numbered entry')
    elif publication_numbers != expected_publications:
        problems.append(
            'assets/cv.txt: publications must be numbered consecutively from 1; '
            f'found {publication_numbers}'
        )

sitemap = root / 'sitemap.xml'
if sitemap.exists():
    try:
        tree = ET.parse(sitemap)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        url_nodes = tree.findall('.//sm:url', ns)
        locs = []
        for url_node in url_nodes:
            loc_node = url_node.find('sm:loc', ns)
            if loc_node is None or not loc_node.text or not loc_node.text.strip():
                problems.append('sitemap.xml: <url> entry is missing a non-empty <loc>')
                continue
            loc = loc_node.text.strip()
            locs.append(loc)

            lastmod_node = url_node.find('sm:lastmod', ns)
            if lastmod_node is None or not lastmod_node.text or not lastmod_node.text.strip():
                problems.append(f'sitemap.xml: {loc} is missing <lastmod>')
            else:
                lastmod = lastmod_node.text.strip()
                try:
                    date.fromisoformat(lastmod)
                except ValueError:
                    problems.append(
                        f'sitemap.xml: {loc} has invalid ISO date in <lastmod>: {lastmod!r}'
                    )

        if not locs:
            problems.append('sitemap.xml: no <loc> entries')
        duplicate_locs = sorted({loc for loc in locs if locs.count(loc) > 1})
        if duplicate_locs:
            problems.append(f'sitemap.xml: duplicate <loc> entries {duplicate_locs}')
        required_locs = {
            'https://sakai1250.github.io/',
            'https://sakai1250.github.io/assets/cv.pdf',
            'https://sakai1250.github.io/assets/cv.txt',
            'https://sakai1250.github.io/llms.txt',
        }
        missing_locs = sorted(required_locs.difference(locs))
        if missing_locs:
            problems.append(
                f'sitemap.xml: missing required primary URLs {missing_locs}'
            )
        for loc in locs:
            parsed = urlsplit(loc)
            if parsed.netloc != 'sakai1250.github.io':
                problems.append(f'sitemap.xml: unexpected host in {loc}')
                continue
            path = parsed.path or '/'
            if path == '/':
                continue
            target = root / path.lstrip('/')
            if not target.exists():
                problems.append(f'sitemap.xml: missing local target {path}')
    except ET.ParseError as exc:
        problems.append(f'sitemap.xml: invalid XML: {exc}')

robots = root / 'robots.txt'
if robots.exists():
    lines = [line.strip() for line in robots.read_text(encoding='utf-8').splitlines() if line.strip()]
    expected_sitemap = 'Sitemap: https://sakai1250.github.io/sitemap.xml'
    sitemap_lines = [line for line in lines if line.lower().startswith('sitemap:')]
    if sitemap_lines != [expected_sitemap]:
        problems.append(
            'robots.txt: expected exactly one canonical sitemap declaration; '
            f'found {sitemap_lines}'
        )
    if 'User-agent: *' not in lines:
        problems.append('robots.txt: wildcard user-agent policy is missing')
    if 'Allow: /' not in lines:
        problems.append('robots.txt: root allow directive is missing')
    if 'Disallow: /' in lines:
        problems.append('robots.txt: root is blocked from crawling')

if problems:
    raise SystemExit('\n'.join(problems))

print(
    f'OK: {len(html_files)} HTML files, {total_ids} unique ids, '
    f'{total_refs} references, ARIA relationships, accessibility basics, generated data, CV text, sitemap and robots checked'
)
