from pathlib import Path


js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

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

scrolled = resolved + """    const scrollHashTarget = () => {
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
    if resolved in js:
        js = js.replace(resolved, scrolled, 1)
    elif old in js:
        js = js.replace(old, scrolled, 1)
    else:
        raise SystemExit("Could not find expected tab hash resolver")

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
    "const target = document.getElementById(targetId);",
    "const content = target?.closest('.tab-content');",
    "return validTabs.has(id) ? id : null;",
    "const scrollHashTarget = () => {",
    "target.getBoundingClientRect().top + window.scrollY - getStickyOffset()",
    "scrollHashTarget();",
):
    if marker not in js:
        raise SystemExit(f"Missing deep-link tab marker: {marker}")

js_path.write_text(js, encoding="utf-8")
