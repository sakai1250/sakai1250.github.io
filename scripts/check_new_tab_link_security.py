#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path


HTML_FILES = [Path('index.html'), Path('404.html')]
REQUIRED_REL_TOKENS = {'noopener', 'noreferrer'}
problems = []
checked_links = 0


class LinkParser(HTMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    def handle_starttag(self, tag, attrs):
        global checked_links
        if tag != 'a':
            return

        attrs = dict(attrs)
        if attrs.get('target', '').lower() != '_blank':
            return

        checked_links += 1
        rel_tokens = {token.lower() for token in attrs.get('rel', '').split()}
        missing_tokens = sorted(REQUIRED_REL_TOKENS - rel_tokens)
        if missing_tokens:
            href = attrs.get('href', '<missing href>')
            missing = ' '.join(missing_tokens)
            problems.append(
                f'{self.path}: target="_blank" link is missing rel token(s) {missing}: {href}'
            )


for html_path in HTML_FILES:
    if not html_path.exists():
        problems.append(f'missing HTML file {html_path}')
        continue

    parser = LinkParser(html_path)
    parser.feed(html_path.read_text(encoding='utf-8'))

if problems:
    raise SystemExit('\n'.join(problems))

print(
    f'OK: {checked_links} new-tab links include '
    'rel="noopener noreferrer"'
)
