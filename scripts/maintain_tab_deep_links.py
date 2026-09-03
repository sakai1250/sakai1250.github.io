import re
from pathlib import Path


js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")
html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

static_section_ids = {
    "Research Achievements": "research-research-achievements",
    "Awards": "research-awards",
    "My Apps & Services": "engineer-my-apps-and-services",
}

for english_title, section_id in static_section_ids.items():
    marker = f'id="{section_id}"'
    if marker in html:
        continue

    pattern = re.compile(
        r'<section class="section-card">(?=\s*<h2 class="section-title">\s*'
        r'<span lang="ja">[^<]*</span>\s*'
        rf'<span lang="en">{re.escape(english_title)}</span>)'
    )
    html, count = pattern.subn(
        f'<section class="section-card" id="{section_id}">',
        html,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Could not assign static section ID for {english_title}")

for section_id in static_section_ids.values():
    if html.count(f'id="{section_id}"') != 1:
        raise SystemExit(f"Static section ID must appear exactly once: {section_id}")

html_path.write_text(html, encoding="utf-8")

old = """    const tabFromHash = () => {
        const match = window.location.hash.match(/^#([a-z0-9-]+)-content$/i);
        return match && validTabs.has(match[1]) ? match[1] : null;
    };
"""

resolved = """    const tabFromHash = () => {
        const match = window.location.hash.match(/^#([a-z0-9-]+)-content$/i);
        if (match && validTabs.has(match[1])) return match[1];

        const rawHash = window.location.hash.slice(1);
        if (!rawHash) return null;

        let targetId;
        try { targetId = decodeURIComponent(rawHash); } catch { targetId = rawHash; }
        const target = document.getElementById(targetId);
        const content = target?.closest('.tab-content');
        if (!content?.id.endsWith('-content')) return null;

        const id = content.id.replace(/-content$/, '');
        return validTabs.has(id) ? id : null;
    };
"""

early_section_ids = """    tabContents.forEach(content => {
        content.querySelectorAll('.section-card').forEach((section, index) => {
            section.id = getSectionId(content, section, index);
        });
    });
"""

hash_resolver = early_section_ids + resolved
if hash_resolver not in js:
    if resolved in js:
        js = js.replace(resolved, hash_resolver, 1)
    elif old in js:
        js = js.replace(old, hash_resolver, 1)
    else:
        raise SystemExit("Could not find expected tab hash resolver")

scrolled = hash_resolver + """    const scrollHashTarget = () => {
        const rawHash = window.location.hash.slice(1);
        if (!rawHash) return;

        let targetId;
        try { targetId = decodeURIComponent(rawHash); } catch { targetId = rawHash; }
        const target = document.getElementById(targetId);
        if (!target || target.classList.contains('tab-content')) return;

        window.requestAnimationFrame(() => {
            window.scrollTo({
                top: target.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
                behavior: 'auto'
            });
        });
    };
"""

legacy_scrolled = resolved + """    const scrollHashTarget = () => {
        const rawHash = window.location.hash.slice(1);
        if (!rawHash) return;

        let targetId;
        try { targetId = decodeURIComponent(rawHash); } catch { targetId = rawHash; }
        const target = document.getElementById(targetId);
        if (!target || target.classList.contains('tab-content')) return;

        window.requestAnimationFrame(() => {
            window.scrollTo({
                top: target.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
                behavior: 'auto'
            });
        });
    };
"""

if scrolled not in js:
    if legacy_scrolled in js:
        js = js.replace(legacy_scrolled, scrolled, 1)
    elif hash_resolver in js:
        js = js.replace(hash_resolver, scrolled, 1)
    else:
        raise SystemExit("Could not find expected tab hash resolver with early section IDs")

old_navigation = """    const initialTab = tabFromHash() || Array.from(tabItems).find(i => i.classList.contains('active'))?.getAttribute('data-tab');
    if (initialTab) switchTab(initialTab);
    window.addEventListener('hashchange', () => {
        const tab = tabFromHash();
        if (tab) switchTab(tab);
    });
"""

new_navigation = """    const initialTab = tabFromHash() || Array.from(tabItems).find(i => i.classList.contains('active'))?.getAttribute('data-tab');
    if (initialTab) {
        switchTab(initialTab);
        scrollHashTarget();
    }
    window.addEventListener('hashchange', () => {
        const tab = tabFromHash();
        if (!tab) return;
        switchTab(tab);
        scrollHashTarget();
    });
"""

if new_navigation not in js:
    if old_navigation not in js:
        raise SystemExit("Could not find expected deep-link navigation handling")
    js = js.replace(old_navigation, new_navigation, 1)

for marker in (
    "tabContents.forEach(content => {",
    "section.id = getSectionId(content, section, index);",
    "const target = document.getElementById(targetId);",
    "const content = target?.closest('.tab-content');",
    "return validTabs.has(id) ? id : null;",
    "const scrollHashTarget = () => {",
    "target.getBoundingClientRect().top + window.scrollY - getStickyOffset()",
    "scrollHashTarget();",
):
    if marker not in js:
        raise SystemExit(f"Missing deep-link tab marker: {marker}")

if js.index("section.id = getSectionId(content, section, index);") > js.index("const tabFromHash = () => {"):
    raise SystemExit("Stable section IDs must be assigned before resolving the initial hash")

js_path.write_text(js, encoding="utf-8")
