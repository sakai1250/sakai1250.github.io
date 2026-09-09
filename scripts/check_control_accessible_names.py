#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path


class ControlNameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_control = None
        self.unnamed_controls = []
        self.document_ids = set()
        self.labelledby_references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get('id', '').strip()
        if element_id:
            self.document_ids.add(element_id)

        if self.current_control is not None and tag == 'img':
            alt = attrs.get('alt', '').strip()
            if alt:
                self.current_control['text'].append(alt)
            return

        is_control = tag == 'button' or (tag == 'a' and attrs.get('href'))
        if not is_control:
            return
        self.current_control = {
            'tag': tag,
            'id': attrs.get('id', ''),
            'href': attrs.get('href', ''),
            'aria_label': attrs.get('aria-label', '').strip(),
            'aria_labelledby': attrs.get('aria-labelledby', '').strip(),
            'text': [],
        }

    def handle_data(self, data):
        if self.current_control is not None:
            self.current_control['text'].append(data)

    def handle_endtag(self, tag):
        if self.current_control is None or tag != self.current_control['tag']:
            return
        control = self.current_control
        accessible_text = ''.join(control['text']).strip()
        if control['id']:
            identifier = f"#{control['id']}"
        elif control['tag'] == 'a':
            identifier = f"<a href={control['href']!r}>"
        else:
            identifier = '<button>'

        if control['aria_labelledby']:
            self.labelledby_references.append(
                (identifier, control['aria_labelledby'].split())
            )

        if not (accessible_text or control['aria_label'] or control['aria_labelledby']):
            self.unnamed_controls.append(identifier)
        self.current_control = None

    def missing_labelledby_references(self):
        missing = []
        for identifier, references in self.labelledby_references:
            unknown = [reference for reference in references if reference not in self.document_ids]
            if unknown:
                missing.append(f"{identifier} -> {unknown}")
        return missing


problems = []
for html_path in (Path('index.html'), Path('404.html')):
    parser = ControlNameParser()
    parser.feed(html_path.read_text(encoding='utf-8'))
    if parser.unnamed_controls:
        problems.append(
            f"{html_path}: interactive controls missing an accessible name "
            f"{parser.unnamed_controls}"
        )
    missing_references = parser.missing_labelledby_references()
    if missing_references:
        problems.append(
            f"{html_path}: aria-labelledby references missing element IDs "
            f"{missing_references}"
        )

index_text = Path('index.html').read_text(encoding='utf-8')
main_text = Path('main.js').read_text(encoding='utf-8')

for mixed_label in (
    'Switch to English / 英語に切り替え',
    'Switch to Japanese / 日本語に切り替え',
    'Switch to light theme / ライトテーマに切り替え',
    'Switch to dark theme / ダークテーマに切り替え',
):
    if mixed_label in index_text or mixed_label in main_text:
        problems.append(
            f'header controls must follow the active site language; mixed label remains: {mixed_label}'
        )

for expected in (
    'id="lang-toggle" type="button" aria-label="英語に切り替え"',
    'id="theme-toggle" type="button" aria-label="ライトテーマに切り替え"',
):
    if expected not in index_text:
        problems.append(f'index.html: missing localized static header control name: {expected}')

for expected in (
    "language === 'ja' ? '英語に切り替え' : 'Switch to Japanese'",
    "lang === 'en' ? 'Switch to light theme' : 'ライトテーマに切り替え'",
    "lang === 'en' ? 'Switch to dark theme' : 'ダークテーマに切り替え'",
    "window.dispatchEvent(new Event('portfolio:languagechange'))",
    "window.addEventListener('portfolio:languagechange'",
):
    if expected not in main_text:
        problems.append(f'main.js: missing language-aware header control behavior: {expected}')

award_marker = '<section class="section-card" id="research-awards">'
award_start = index_text.find(award_marker)
award_end = index_text.find('</section>', award_start)
if award_start == -1 or award_end == -1:
    problems.append('index.html: missing research awards section')
else:
    award_section = index_text[award_start:award_end]
    bilingual_award_link = (
        '<span lang="ja">[詳細]</span><span lang="en">[Details]</span>'
    )
    award_links = award_section.count('<a ')
    localized_links = award_section.count(bilingual_award_link)
    if award_links == 0:
        problems.append('index.html: research awards section has no source links')
    elif localized_links != award_links:
        problems.append(
            'index.html: every award source link must expose [詳細] in Japanese '
            f'and [Details] in English; found {localized_links}/{award_links}'
        )
    if 'aria-label="Award details:' in award_section:
        problems.append(
            'index.html: award links must not override localized visible text '
            'with an English-only aria-label'
        )

if problems:
    raise SystemExit('\n'.join(problems))

print(
    'OK: links and buttons expose valid accessible names; header controls and '
    'award source links follow the selected site language'
)
