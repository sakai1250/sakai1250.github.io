#!/usr/bin/env python3

from pathlib import Path
from urllib.parse import urlsplit
import re


ROOT = Path('.')
CSS_FILES = (Path('style.css'),)
URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)


problems = []
checked = 0

for css_path in CSS_FILES:
    text = css_path.read_text(encoding='utf-8')
    for match in URL_RE.finditer(text):
        raw = match.group(2).strip()
        if not raw or raw.startswith(('#', 'data:', 'http://', 'https://', '//')):
            continue

        path = urlsplit(raw).path
        if not path:
            continue

        target = (css_path.parent / path).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            problems.append(f'{css_path}: CSS asset escapes repository root: {raw}')
            continue

        checked += 1
        if not target.is_file():
            problems.append(f'{css_path}: missing CSS asset: {raw}')

if problems:
    raise SystemExit('\n'.join(problems))

print(f'OK: {checked} local CSS asset reference(s) resolve to files')
