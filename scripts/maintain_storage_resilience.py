from pathlib import Path


INDEX = Path("index.html")
MAIN = Path("main.js")


def update_index() -> None:
    text = INDEX.read_text(encoding="utf-8")
    old = "      const savedTheme = localStorage.getItem('theme');"
    new = "      let savedTheme = null;\n      try { savedTheme = localStorage.getItem('theme'); } catch {}"
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise SystemExit("Could not find theme storage initialization")
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
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"Could not find expected storage access: {old}")

    MAIN.write_text(text, encoding="utf-8")


update_index()
update_main()
