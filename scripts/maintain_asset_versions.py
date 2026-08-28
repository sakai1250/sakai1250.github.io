from __future__ import annotations

import hashlib
import re
from pathlib import Path


INDEX = Path("index.html")
ASSETS = ("style.css", "effects.js", "main.js")
FAVICON = "assets/avatar.jpg"
LEGACY_FAVICON = "1770375438872~2.png"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def main() -> None:
    text = INDEX.read_text(encoding="utf-8")

    for asset in ASSETS:
        path = Path(asset)
        if not path.is_file():
            raise SystemExit(f"Missing asset: {asset}")

        version = digest(path)
        pattern = re.compile(rf'(["\']){re.escape(asset)}\?v=[^"\']+\1')
        replacement = f'"{asset}?v={version}"'
        text, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            raise SystemExit(f"Expected one versioned reference for {asset}")

    favicon = Path(FAVICON)
    if not favicon.is_file():
        raise SystemExit(f"Missing favicon asset: {FAVICON}")

    legacy_tag = f'<link rel="icon" href="{LEGACY_FAVICON}">'
    favicon_tag = f'<link rel="icon" href="{FAVICON}" type="image/jpeg">'
    if legacy_tag in text:
        text = text.replace(legacy_tag, favicon_tag, 1)
    elif favicon_tag not in text:
        raise SystemExit("Could not find expected favicon reference")

    INDEX.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
