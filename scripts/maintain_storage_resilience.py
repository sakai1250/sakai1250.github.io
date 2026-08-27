from pathlib import Path
import re


INDEX = Path("index.html")
MAIN = Path("main.js")
STYLE = Path("style.css")


def update_index() -> None:
    text = INDEX.read_text(encoding="utf-8")
    old = "      const savedTheme = localStorage.getItem('theme');"
    new = "      let savedTheme = null;\n      try { savedTheme = localStorage.getItem('theme'); } catch {}"
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit("Could not find theme storage initialization")

    # The portfolio must remain visible even when JavaScript fails. A stale
    # no-script exception for the removed full-screen loader only suggests that
    # the loader is still part of the supported page behavior.
    text = text.replace(
        '  <noscript><style>#loading-screen{display:none!important}</style></noscript>\n',
        '',
        1,
    )
    INDEX.write_text(text, encoding="utf-8")


def update_main() -> None:
    text = MAIN.read_text(encoding="utf-8")
    marker = "// === Core Functions ===\n"
    helpers = """// === Core Functions ===\n\nfunction safeStorageGet(key) {\n    try { return localStorage.getItem(key); } catch { return null; }\n}\n\nfunction safeStorageSet(key, value) {\n    try { localStorage.setItem(key, value); } catch {}\n}\n"""
    if "function safeStorageGet(key)" not in text:
        if marker not in text:
            raise SystemExit("Could not find storage-helper insertion point")
        text = text.replace(marker, helpers, 1)

    replacements = {
        "localStorage.setItem('theme', t);": "safeStorageSet('theme', t);",
        "set(localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'), false);": "set(safeStorageGet('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'), false);",
        "localStorage.setItem('lang', l);": "safeStorageSet('lang', l);",
        "set(localStorage.getItem('lang') || 'ja');": "set(safeStorageGet('lang') || 'ja');",
        "safeInit(window.initBackgroundParticles || initBackgroundParticles, 'BackgroundParticles');": "safeInit(window.initBackgroundParticles, 'BackgroundParticles');",
        "safeInit(window.initTypingEffect || initTypingEffect, 'TypingEffect');": "safeInit(window.initTypingEffect, 'TypingEffect');",
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"Could not find expected resilient access: {old}")

    # The blocking loader was removed from the HTML after it caused mobile
    # visitors to see only the page background. Remove the dead JavaScript too,
    # so future edits cannot accidentally restore a JS-dependent entrance gate.
    text = text.replace("    // Basic Loader\n    initLoader();\n\n", "", 1)
    text, count = re.subn(
        r"\nfunction initLoader\(\) \{.*?\n\}\n\n(?=function initTabs\(\))",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if "function initLoader()" in text or "initLoader();" in text:
        raise SystemExit("Could not remove obsolete loader JavaScript")

    MAIN.write_text(text, encoding="utf-8")


def update_style() -> None:
    text = STYLE.read_text(encoding="utf-8")
    # Keep no CSS for a full-screen element that no longer exists. This makes
    # the non-blocking behavior obvious from both markup and styles.
    text, _ = re.subn(
        r"/\* Loading and retained CV detail \*/\n#loading-screen \{.*?@keyframes quietPulse \{ 50% \{ opacity: 0\.52; \} \}\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if "#loading-screen" in text or ".spinner" in text or "quietPulse" in text:
        raise SystemExit("Could not remove obsolete loader styles")
    STYLE.write_text(text, encoding="utf-8")


update_index()
update_main()
update_style()
