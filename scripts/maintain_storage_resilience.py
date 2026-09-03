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
        "safeInit(window.initBackgroundParticles || initBackgroundParticles, 'BackgroundParticles');": "safeInit(window.initBackgroundParticles, 'BackgroundParticles');",
        "safeInit(window.initTypingEffect || initTypingEffect, 'TypingEffect');": "safeInit(window.initTypingEffect, 'TypingEffect');",
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise SystemExit(f"Could not find expected resilient access: {old}")

    legacy_language_get = "set(localStorage.getItem('lang') || 'ja');"
    resilient_language_get = "set(safeStorageGet('lang') || 'ja');"
    browser_aware_language_get = """const browserLanguage = (navigator.languages?.[0] || navigator.language || 'ja').toLowerCase();
    set(safeStorageGet('lang') || (browserLanguage.startsWith('en') ? 'en' : 'ja'));"""
    if legacy_language_get in text:
        text = text.replace(legacy_language_get, resilient_language_get, 1)
    elif resilient_language_get not in text and browser_aware_language_get not in text:
        raise SystemExit("Could not find resilient language storage access")

    # Keep the toggle's programmatic state aligned with the applied theme. The
    # moon/sun glyph is intentionally hidden from screen readers, so without a
    # pressed state assistive technology cannot tell whether dark mode is active.
    theme_icon_update = "        if (icon) icon.textContent = t === 'dark' ? '☾' : '☀︎';"
    theme_state_update = (
        theme_icon_update
        + "\n        if (btn) btn.setAttribute('aria-pressed', String(t === 'dark'));"
    )
    if theme_state_update not in text:
        if theme_icon_update not in text:
            raise SystemExit("Could not find theme state update point")
        text = text.replace(theme_icon_update, theme_state_update, 1)

    # The blocking loader was removed from the HTML after it caused mobile
    # visitors to see only the page background. Remove the dead JavaScript too,
    # so future edits cannot accidentally restore a JS-dependent entrance gate.
    text = text.replace("    // Basic Loader\n    initLoader();\n\n", "", 1)
    text, _ = re.subn(
        r"\nfunction initLoader\(\) \{.*?\n\}\n\n(?=function initTabs\(\))",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if "function initLoader()" in text or "initLoader();" in text:
        raise SystemExit("Could not remove obsolete loader JavaScript")

    # Scroll reveal is decoration, not content. It temporarily hides every
    # section card and depends on IntersectionObserver to show it again. If a
    # mobile browser stops that path after classes are added, useful content can
    # disappear even though the HTML is valid. Keep core content visible by
    # default and remove this JavaScript-dependent reveal step entirely.
    text = text.replace("    safeInit(initScrollReveal, 'ScrollReveal');\n", "", 1)
    text, _ = re.subn(
        r"\nfunction initScrollReveal\(\) \{.*?\n\}\n\n(?=function initReadingProgress\(\))",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    if "initScrollReveal" in text:
        raise SystemExit("Could not remove JavaScript-dependent scroll reveal")

    # Clipboard permission and API support vary across mobile browsers. Do not
    # let the visible Copy action fail silently when navigator.clipboard is
    # unavailable or rejects a write. Use a conservative textarea fallback and
    # surface the existing error label if both paths fail.
    resilient_copy = """function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const value = btn.getAttribute('data-copy') || '';
            const lang = document.documentElement.getAttribute('data-lang') || 'ja';
            const success = btn.getAttribute(`data-${lang}-success`) || 'Copied!';
            const error = btn.getAttribute('data-error') || 'Error';
            const spans = btn.querySelectorAll('span');
            const originals = Array.from(spans).map(s => s.textContent);

            const fallbackCopy = () => {
                const textarea = document.createElement('textarea');
                textarea.value = value;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                textarea.setSelectionRange(0, textarea.value.length);
                let copied = false;
                try { copied = document.execCommand('copy'); } catch {}
                textarea.remove();
                return copied;
            };

            let copied = false;
            try {
                if (navigator.clipboard?.writeText) {
                    await navigator.clipboard.writeText(value);
                    copied = true;
                } else {
                    copied = fallbackCopy();
                }
            } catch {
                copied = fallbackCopy();
            }

            spans.forEach(s => s.textContent = copied ? success : error);
            btn.classList.toggle('success', copied);
            setTimeout(() => {
                spans.forEach((s, i) => s.textContent = originals[i]);
                btn.classList.remove('success');
            }, 2000);
        });
    });
}
"""
    current_copy_pattern = re.compile(
        r"function initCopyButtons\(\) \{.*?\n\}\n\n(?=function initStickyHeader\(\))",
        re.DOTALL,
    )
    copy_match = current_copy_pattern.search(text)
    if not copy_match:
        raise SystemExit("Could not find copy-button handler")
    if copy_match.group(0).rstrip() != resilient_copy.rstrip():
        text = current_copy_pattern.sub(resilient_copy + "\n", text, count=1)

    if "navigator.clipboard?.writeText" not in text or "fallbackCopy" not in text:
        raise SystemExit("Clipboard resilience is incomplete")

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

    # Do not make a core recruiter-facing action depend on JavaScript. The CV
    # link is marked primary in the static HTML, so hiding every primary header
    # button on mobile makes the CV disappear whenever effects.js does not run.
    text = text.replace(
        "  .header-actions .header-btn.primary { display: none; }\n",
        "",
    )
    if ".header-actions .header-btn.primary { display: none; }" in text:
        raise SystemExit("Mobile CSS still hides the primary CV action")

    # English translations appear in both inline elements such as button labels
    # and block elements such as profile text. Restoring every English element as
    # display:block changes layout semantics after a language switch. Let each
    # element return to its native display type instead.
    forced_english_block = 'html[data-lang="en"] [lang="en"] { display: block !important; }'
    semantic_english_display = 'html[data-lang="en"] [lang="en"] { display: revert !important; }'
    if forced_english_block in text:
        text = text.replace(forced_english_block, semantic_english_display, 1)
    elif semantic_english_display not in text:
        raise SystemExit("Could not find English language display rule")

    # Remove styles whose only purpose is to hide content before the scroll
    # observer restores it. Important portfolio sections should never start at
    # opacity zero just to provide an entrance animation.
    text, _ = re.subn(
        r"\.reveal-item \{\n  opacity: 0;\n  transform: translateY\(12px\);\n  transition: opacity 0\.52s ease, transform 0\.52s var\(--ease-organic\);\n\}\n\.reveal-active \{ opacity: 1; transform: translateY\(0\); \}\n\n",
        "",
        text,
        count=1,
    )
    text = text.replace(
        "  .reveal-item { opacity: 1 !important; transform: none !important; }\n",
        "",
    )
    text = text.replace(
        "  .reveal-item { opacity: 1; transform: none; }\n",
        "",
    )
    if ".reveal-item" in text or ".reveal-active" in text:
        raise SystemExit("Could not remove scroll reveal styles")

    # Mobile browsers do not need decorative viewport compositing to read the
    # portfolio. A fixed full-screen pseudo-element plus backdrop filters can
    # trigger expensive GPU layers and has previously correlated with the page
    # getting stuck on its background in mobile Chrome. Keep the mobile path
    # deliberately simple while preserving the desktop design.
    mobile_marker = "/* Mobile rendering safety: keep core content off decorative compositing layers. */"
    mobile_rules = """

/* Mobile rendering safety: keep core content off decorative compositing layers. */
@media (max-width: 768px) {
  body::before { display: none !important; }
  .header-bar,
  .modal-overlay {
    -webkit-backdrop-filter: none !important;
    backdrop-filter: none !important;
  }
  .header-bar { background: var(--bg-2) !important; }
}
"""
    if mobile_marker not in text:
        text = text.rstrip() + mobile_rules

    required_mobile_rules = (
        "body::before { display: none !important; }",
        "-webkit-backdrop-filter: none !important;",
        "backdrop-filter: none !important;",
        ".header-bar { background: var(--bg-2) !important; }",
    )
    if any(rule not in text for rule in required_mobile_rules):
        raise SystemExit("Mobile rendering safety rules are incomplete")

    STYLE.write_text(text, encoding="utf-8")


update_index()
update_main()
update_style()
