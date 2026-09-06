#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit
import re


def main() -> None:
    path = Path('.well-known/security.txt')
    if not path.exists():
        raise SystemExit('Missing .well-known/security.txt')

    fields: dict[str, list[str]] = {}
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            raise SystemExit(f'Invalid security.txt line: {raw_line!r}')
        key, value = line.split(':', 1)
        fields.setdefault(key.strip(), []).append(value.strip())

    required = ['Contact', 'Canonical', 'Preferred-Languages', 'Expires']
    missing = [key for key in required if not fields.get(key)]
    if missing:
        raise SystemExit(f'Missing required security.txt fields: {missing}')

    canonical = fields['Canonical'][0]
    expected = 'https://sakai1250.github.io/.well-known/security.txt'
    parsed = urlsplit(canonical)
    if canonical != expected or parsed.scheme != 'https':
        raise SystemExit(f'Canonical must be {expected}')

    contacts = fields['Contact']
    if not any(value.startswith(('mailto:', 'https://')) for value in contacts):
        raise SystemExit('Contact must include a mailto: or https:// URI')

    cv_text = Path('assets/cv.txt').read_text(encoding='utf-8')
    cv_email_match = re.search(r'^Email:\s*(\S+@\S+)\s*$', cv_text, flags=re.MULTILINE)
    if not cv_email_match:
        raise SystemExit('assets/cv.txt is missing a machine-readable Email field')
    profile_email = cv_email_match.group(1)
    expected_mailto = f'mailto:{profile_email}'
    if expected_mailto not in contacts:
        raise SystemExit(
            'security.txt Contact is out of sync with assets/cv.txt: '
            f'expected {expected_mailto}'
        )

    policy_text = Path('SECURITY.md').read_text(encoding='utf-8')
    if profile_email not in policy_text:
        raise SystemExit(
            'SECURITY.md is out of sync with the profile contact email: '
            f'expected {profile_email}'
        )

    expires_raw = fields['Expires'][0]
    try:
        expires = datetime.fromisoformat(expires_raw.replace('Z', '+00:00'))
    except ValueError as exc:
        raise SystemExit(f'Invalid Expires timestamp: {expires_raw}') from exc
    if expires.tzinfo is None:
        raise SystemExit('Expires must include a timezone')

    now = datetime.now(timezone.utc)
    if expires <= now:
        raise SystemExit(f'security.txt expired at {expires.isoformat()}')
    if expires - now < timedelta(days=30):
        raise SystemExit(
            f'security.txt expires in fewer than 30 days: {expires.isoformat()}'
        )

    policy = fields.get('Policy', [])
    if policy and not all(urlsplit(value).scheme == 'https' for value in policy):
        raise SystemExit('Policy URLs must use HTTPS')

    print(
        f'OK: security.txt matches the public profile contact and is valid through {expires.isoformat()}'
    )


if __name__ == '__main__':
    main()
