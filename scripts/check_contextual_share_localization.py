#!/usr/bin/env python3
from pathlib import Path


main = Path('main.js').read_text(encoding='utf-8')
maintenance = Path('scripts/maintain_contextual_share_link.py').read_text(encoding='utf-8')

shared_markers = (
    "document.documentElement.dataset.lang === 'en' ? 'en' : 'ja'",
    "'坂井泰吾のポートフォリオです。'",
    '"Check out Taigo Sakai\'s Portfolio!"',
    'text: shareText,',
    "via: 'ikaitaig'",
    '`${window.location.origin}${window.location.pathname}${window.location.search}${window.location.hash}`',
)

problems = []
for name, text in (
    ('main.js', main),
    ('scripts/maintain_contextual_share_link.py', maintenance),
):
    for marker in shared_markers:
        if marker not in text:
            problems.append(f'{name}: missing contextual share marker {marker!r}')

if 'text: "Check out Taigo Sakai\'s Portfolio!"' in main:
    problems.append('main.js: share text reverted to an English-only direct assignment')

if problems:
    raise SystemExit('\n'.join(problems))

print('OK: contextual share text follows the current portfolio language and preserves the deep link')
