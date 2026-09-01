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
APP_TITLE_ANCHOR_RE = re.compile(
    r'<a\b(?=[^>]*\bclass=(?P<cq>["\'])[^"\']*\bapp-title\b[^"\']*(?P=cq))'
    r'(?=[^>]*\bhref=(?P<hq>["\'])(?P<href>https?://.*?)(?P=hq))[^>]*>',
    re.IGNORECASE,
)
APP_LINKS_BLOCK_RE = re.compile(
    r'(?P<open><div\b[^>]*\bclass=(?P<cq>["\'])[^"\']*\bapp-links\b[^"\']*(?P=cq)[^>]*>)'
    r'(?P<body>.*?)'
    r'(?P<close></div>)',
    re.IGNORECASE | re.DOTALL,
)
HTTP_ANCHOR_RE = re.compile(
    r'<a\b(?=[^>]*\bhref=(?P<hq>["\'])https?://.*?(?P=hq))[^>]*>',
    re.IGNORECASE,
)

PAPER_HOSTS = (
    'arxiv.org/',
    'openaccess.thecvf.com/',
    'link.springer.com/',
    'scitepress.org/',
)
PROGRAM_HOSTS = ('cars-int.org/scientific-program/',)
STALE_PROFILE_HREFS = (
    'https://www.kaggle.com/sakaitt',
)


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


def keep_external_link_non_destructive(match: re.Match[str]) -> str:
    tag = match.group(0)
    if re.search(r'\btarget=(["\'])_blank\1', tag, re.IGNORECASE):
        return secure_anchor(tag)
    return secure_anchor(tag[:-1] + ' target="_blank">')


def keep_external_app_links_non_destructive(match: re.Match[str]) -> str:
    body = HTTP_ANCHOR_RE.sub(keep_external_link_non_destructive, match.group('body'))
    return f"{match.group('open')}{body}{match.group('close')}"


def clarify_resource_label(match: re.Match[str]) -> str:
    href = match.group('href').lower()
    if any(host in href for host in PAPER_HOSTS):
        label = '[Paper]'
    elif any(host in href for host in PROGRAM_HOSTS):
        label = '[Program]'
    else:
        return match.group(0)
    return f"{match.group('open')}{label}{match.group('close')}"


def remove_stale_profile_links(text: str) -> str:
    for href in STALE_PROFILE_HREFS:
        pattern = re.compile(
            rf'<a\b[^>]*\bhref=(["\']){re.escape(href)}\1[^>]*>.*?</a>\s*',
            re.IGNORECASE | re.DOTALL,
        )
        text = pattern.sub('', text)
    return text


for path in TARGET_FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    updated = remove_stale_profile_links(text)
    updated = APP_TITLE_ANCHOR_RE.sub(keep_external_link_non_destructive, updated)
    updated = APP_LINKS_BLOCK_RE.sub(keep_external_app_links_non_destructive, updated)
    updated = ANCHOR_RE.sub(lambda match: secure_anchor(match.group(0)), updated)
    updated = GENERIC_LINK_RE.sub(clarify_resource_label, updated)
    path.write_text(updated, encoding='utf-8')
