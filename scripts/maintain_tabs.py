from pathlib import Path
import re


js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

# Once JavaScript is running, the Research / Engineering controls become a real
# tab interface. Keep the ARIA semantics and selected state in the runtime code,
# where they accurately describe what the page is doing.
required_runtime_markers = (
    "if (tabNav) tabNav.setAttribute('role', 'tablist');",
    "i.setAttribute('role', 'tab');",
    "i.setAttribute('aria-controls', `${id}-content`);",
    "c.setAttribute('role', 'tabpanel');",
    "i.setAttribute('aria-selected', String(active));",
    "c.hidden = !active;",
)
for marker in required_runtime_markers:
    if marker not in js:
        raise SystemExit(f"Missing runtime tab accessibility marker: {marker}")

# Native buttons already handle Enter and Space. Retain only the custom arrow-key
# behavior so the tab interaction does not have duplicate activation logic.
legacy_keyboard = """        const activate = () => switchTab(id, true);
        i.addEventListener('click', activate);
        i.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                activate();
                return;
            }
"""
native_keyboard = """        i.addEventListener('click', () => switchTab(id, true));
        i.addEventListener('keydown', (e) => {
"""
if legacy_keyboard in js:
    js = js.replace(legacy_keyboard, native_keyboard, 1)
elif native_keyboard not in js:
    raise SystemExit("Could not find expected primary tab keyboard handling")

old_section_state = "    tabs.forEach((tab, index) => tab.classList.toggle('active', index === activeIndex));"
new_section_state = """    tabs.forEach((tab, index) => {
        const active = index === activeIndex;
        tab.classList.toggle('active', active);
        if (active) tab.setAttribute('aria-current', 'true');
        else tab.removeAttribute('aria-current');
    });"""
if old_section_state in js:
    js = js.replace(old_section_state, new_section_state, 1)
elif new_section_state not in js:
    raise SystemExit("Could not find expected section tab state update")

js_path.write_text(js, encoding="utf-8")

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

# Without JavaScript both primary sections remain visible. Do not claim that the
# static document is already a tab interface: aria-selected=false would conflict
# with Engineering content that is intentionally visible as a fallback. Runtime
# JavaScript adds the tab semantics only after it starts hiding inactive panels.
html = re.sub(
    r'(<nav class="tab-nav header-tab-nav" aria-label="Primary sections") role="tablist"(>)',
    r'\1\2',
    html,
    count=1,
)

for tab_id in ("research", "engineer"):
    pattern = re.compile(rf'<button\s+([^>]*\bid="{tab_id}-tab"[^>]*)>')
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find expected {tab_id} tab button")
    attrs = match.group(1)
    for attr_pattern in (
        r'\s+role="tab"',
        r'\s+aria-controls="[^"]+"',
        r'\s+aria-selected="(?:true|false)"',
        r'\s+tabindex="-?\d+"',
    ):
        attrs = re.sub(attr_pattern, '', attrs)
    html = html[:match.start()] + f'<button {attrs}>' + html[match.end():]

for tab_id in ("research", "engineer"):
    pattern = re.compile(rf'<div\s+([^>]*\bid="{tab_id}-content"[^>]*)>')
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find expected {tab_id} content panel")
    attrs = match.group(1)
    attrs = re.sub(r'\s+role="tabpanel"', '', attrs)
    attrs = re.sub(r'\s+aria-labelledby="[^"]+"', '', attrs)
    html = html[:match.start()] + f'<div {attrs}>' + html[match.end():]

html_path.write_text(html, encoding="utf-8")

css_path = Path("style.css")
css = css_path.read_text(encoding="utf-8")
old_css = """.tab-item {
  padding: 9px 17px;
  border-radius: 999px;
  color: var(--muted);
"""
new_css = """.tab-item {
  padding: 9px 17px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--muted);
"""
if old_css in css:
    css = css.replace(old_css, new_css, 1)
elif new_css not in css:
    raise SystemExit("Could not find expected tab styling")

css_path.write_text(css, encoding="utf-8")
