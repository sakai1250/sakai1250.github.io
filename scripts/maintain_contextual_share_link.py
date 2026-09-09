from pathlib import Path


js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

init_anchor = "    safeInit(initReadingProgress, 'ReadingProgress');\n"
init_line = "    safeInit(initContextualShareLink, 'ContextualShareLink');\n"
if init_line not in js:
    if init_anchor not in js:
        raise SystemExit("Could not find expected initialization anchor")
    js = js.replace(init_anchor, init_anchor + init_line, 1)

share_function = r'''function initContextualShareLink() {
    const link = document.getElementById('share-btn');
    if (!link) return;

    const sync = () => {
        const pageUrl = `${window.location.origin}${window.location.pathname}${window.location.search}${window.location.hash}`;
        const lang = document.documentElement.dataset.lang === 'en' ? 'en' : 'ja';
        const shareText = lang === 'ja'
            ? '坂井泰吾のポートフォリオです。'
            : "Check out Taigo Sakai's Portfolio!";
        const params = new URLSearchParams({
            text: shareText,
            url: pageUrl,
            via: 'ikaitaig'
        });
        link.href = `https://twitter.com/intent/tweet?${params.toString()}`;
    };

    link.addEventListener('focus', sync);
    link.addEventListener('pointerdown', sync);
    link.addEventListener('click', sync);
    window.addEventListener('hashchange', sync);
    sync();
}
'''

function_start = js.find("function initContextualShareLink() {")
if function_start == -1:
    marker = "\n// === Core Functions ===\n"
    if marker not in js:
        raise SystemExit("Could not find core function marker")
    js = js.replace(marker, marker + "\n" + share_function + "\n", 1)
else:
    next_function = js.find("\n\nfunction ", function_start + 1)
    if next_function == -1:
        raise SystemExit("Could not find the end of contextual share function")
    js = js[:function_start] + share_function.rstrip() + js[next_function:]

for marker in (
    "safeInit(initContextualShareLink, 'ContextualShareLink');",
    "const pageUrl = `${window.location.origin}${window.location.pathname}${window.location.search}${window.location.hash}`;",
    "document.documentElement.dataset.lang === 'en' ? 'en' : 'ja'",
    "'坂井泰吾のポートフォリオです。'",
    '"Check out Taigo Sakai\'s Portfolio!"',
    "text: shareText,",
    "via: 'ikaitaig'",
    "link.addEventListener('click', sync);",
    "window.addEventListener('hashchange', sync);",
):
    if marker not in js:
        raise SystemExit(f"Missing contextual share marker: {marker}")

js_path.write_text(js, encoding="utf-8")
