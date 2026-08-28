from pathlib import Path
import re

TARGET_FILES = (Path('index.html'), Path('404.html'))
ANCHOR_RE = re.compile(r'<a\b[^>]*\btarget=(?P<q>["\'])_blank(?P=q)[^>]*>', re.IGNORECASE)
REL_RE = re.compile(r'\brel=(?P<q>["\'])(?P<value>.*?)(?P=q)', re.IGNORECASE)
GENERIC_LINK_RE = re.compile(
    r'(?P<open><a\b[^>]*\bhref=(?P<q>["\'])(?P<href>.*?)(?P=q)[^>]*>)'
    r'(?P<label>\[Link\])(?P<close></a>)',
    re.IGNORECASE,
)

PAPER_HOSTS = (
    'arxiv.org/',
    'openaccess.thecvf.com/',
    'link.springer.com/',
    'scitepress.org/',
)
PROGRAM_HOSTS = ('cars-int.org/scientific-program/',)


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


def clarify_resource_label(match: re.Match[str]) -> str:
    href = match.group('href').lower()
    if any(host in href for host in PAPER_HOSTS):
        label = '[Paper]'
    elif any(host in href for host in PROGRAM_HOSTS):
        label = '[Program]'
    else:
        return match.group(0)
    return f"{match.group('open')}{label}{match.group('close')}"


for path in TARGET_FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    updated = ANCHOR_RE.sub(lambda match: secure_anchor(match.group(0)), text)
    updated = GENERIC_LINK_RE.sub(clarify_resource_label, updated)
    path.write_text(updated, encoding='utf-8')
