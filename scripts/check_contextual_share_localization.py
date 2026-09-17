#!/usr/bin/env python3
from pathlib import Path

from cv_profile import read_cv_field, read_cv_name


main = Path('main.js').read_text(encoding='utf-8')
maintenance = Path('scripts/maintain_contextual_share_link.py').read_text(encoding='utf-8')
cv_text = Path('assets/cv.txt').read_text(encoding='utf-8')
english_name = read_cv_name(cv_text)
japanese_name = read_cv_field(cv_text, 'Japanese name').replace(' ', '')

shared_markers = (
    "document.documentElement.dataset.lang === 'en' ? 'en' : 'ja'",
    'text: shareText,',
    "via: 'ikaitaig'",
    '`${window.location.origin}${window.location.pathname}${window.location.search}${window.location.hash}`',
)
main_markers = (
    f"'{japanese_name}のポートフォリオです。'",
    f'"Check out {english_name}\'s Portfolio!"',
)
maintenance_markers = (
    "'__JAPANESE_NAME__のポートフォリオです。'",
    '"Check out __ENGLISH_NAME__\'s Portfolio!"',
    '.replace("__JAPANESE_NAME__", japanese_name)',
    '.replace("__ENGLISH_NAME__", english_name)',
)

problems = []
for name, text in (
    ('main.js', main),
    ('scripts/maintain_contextual_share_link.py', maintenance),
):
    for marker in shared_markers:
        if marker not in text:
            problems.append(f'{name}: missing contextual share marker {marker!r}')

for marker in main_markers:
    if marker not in main:
        problems.append(f'main.js: missing contextual share marker {marker!r}')
for marker in maintenance_markers:
    if marker not in maintenance:
        problems.append(
            'scripts/maintain_contextual_share_link.py: '
            f'missing contextual share template marker {marker!r}'
        )

if f'text: "Check out {english_name}\'s Portfolio!"' in main:
    problems.append('main.js: share text reverted to an English-only direct assignment')

if problems:
    raise SystemExit('\n'.join(problems))

print('OK: contextual share text follows the current portfolio language and preserves the deep link')
