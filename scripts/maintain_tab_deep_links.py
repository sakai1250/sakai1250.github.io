from pathlib import Path


js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

old = """    const tabFromHash = () => {
        const match = window.location.hash.match(/^#([a-z0-9-]+)-content$/i);
        return match && validTabs.has(match[1]) ? match[1] : null;
    };
"""

new = """    const tabFromHash = () => {
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

if new not in js:
    if old not in js:
        raise SystemExit("Could not find expected tab hash resolver")
    js = js.replace(old, new, 1)

for marker in (
    "const target = document.getElementById(targetId);",
    "const content = target?.closest('.tab-content');",
    "return validTabs.has(id) ? id : null;",
):
    if marker not in js:
        raise SystemExit(f"Missing deep-link tab marker: {marker}")

js_path.write_text(js, encoding="utf-8")
