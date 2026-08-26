from pathlib import Path
import re

TARGET_FILES = (Path('index.html'), Path('404.html'))
ANCHOR_RE = re.compile(r'<a\b[^>]*\btarget=(?P<q>["\'])_blank(?P=q)[^>]*>', re.IGNORECASE)
REL_RE = re.compile(r'\brel=(?P<q>["\'])(?P<value>.*?)(?P=q)', re.IGNORECASE)


def secure_anchor(tag: str) -> str:
    rel_match = REL_RE.search(tag)
    required = ('noopener', 'noreferrer')

    if rel_match:
        tokens = rel_match.group('value').split()
        lowered = {token.lower() for token in tokens}
        tokens.extend(token for token in required if token not in lowered)
        value = ' '.join(tokens)
        start, end = rel_match.span('value')
        return tag[:start] + value + tag[end:]

    return tag[:-1] + ' rel="noopener noreferrer">'


for path in TARGET_FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    updated = ANCHOR_RE.sub(lambda match: secure_anchor(match.group(0)), text)
    path.write_text(updated, encoding='utf-8')
