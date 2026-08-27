"""Keep filter buttons' visual, language, and screen-reader state aligned."""

from pathlib import Path
import re


js_path = Path("main.js")
text = js_path.read_text(encoding="utf-8")

base_init = """    const input = document.getElementById('search');
    const chips = document.querySelectorAll('.chip');
    let activeTag = 'all', activeYear = 'all';
"""
pressed_init = """    chips.forEach(chip => {
        chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
    });
"""

if base_init not in text:
    raise SystemExit("Could not find filter initialization block")

# Normalize the generated block instead of repeatedly inserting after a prefix
# that remains present inside the generated output.
text = text.replace("\n" + pressed_init, "")
text = text.replace(base_init, base_init + "\n" + pressed_init, 1)

old_click = """        if (t) { activeTag = t; document.querySelectorAll('.chip[data-filter]').forEach(x => x.classList.toggle('active', x === c)); }
        if (y) { activeYear = y; document.querySelectorAll('.chip[data-year]').forEach(x => x.classList.toggle('active', x === c)); }
"""
new_click = """        if (t) {
            activeTag = t;
            document.querySelectorAll('.chip[data-filter]').forEach(x => {
                const active = x === c;
                x.classList.toggle('active', active);
                x.setAttribute('aria-pressed', String(active));
            });
        }
        if (y) {
            activeYear = y;
            document.querySelectorAll('.chip[data-year]').forEach(x => {
                const active = x === c;
                x.classList.toggle('active', active);
                x.setAttribute('aria-pressed', String(active));
            });
        }
"""

if new_click not in text:
    if old_click in text:
        text = text.replace(old_click, new_click, 1)
    else:
        raise SystemExit("Could not find filter click block")

js_path.write_text(text, encoding="utf-8")

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")


def sync_static_pressed(match: re.Match[str]) -> str:
    tag = match.group(0)
    classes = re.search(r'class="([^"]*)"', tag)
    active = bool(classes and "active" in classes.group(1).split())
    value = "true" if active else "false"
    if re.search(r'\saria-pressed="(?:true|false)"', tag):
        return re.sub(r'\saria-pressed="(?:true|false)"', f' aria-pressed="{value}"', tag, count=1)
    return tag[:-1] + f' aria-pressed="{value}">'


html, count = re.subn(
    r'<button\b(?=[^>]*\bclass="[^"]*\bchip\b[^"]*")(?=[^>]*\bdata-(?:year|filter)=)[^>]*>',
    sync_static_pressed,
    html,
)
if count == 0:
    raise SystemExit("Could not find static filter buttons")

# Keep the Engineering filter understandable in either page language.
engineer_filter_label = (
    '<span class="filter-label">'
    '<span lang="ja">フィルター</span>'
    '<span lang="en">Filter</span>'
    '</span>'
)
html = re.sub(
    r'<span class="filter-label">(?:フィルター|\s*<span lang="ja">フィルター</span>\s*<span lang="en">Filter</span>\s*)</span>',
    engineer_filter_label,
    html,
    count=1,
)

all_filter_button = (
    '<button class="chip active" data-filter="all" type="button" aria-pressed="true">'
    '<span lang="ja">すべて</span>'
    '<span lang="en">All</span>'
    '</button>'
)
html = re.sub(
    r'<button class="chip active" data-filter="all" type="button" aria-pressed="true">(?:すべて|\s*<span lang="ja">すべて</span>\s*<span lang="en">All</span>\s*)</button>',
    all_filter_button,
    html,
    count=1,
)

if engineer_filter_label not in html or all_filter_button not in html:
    raise SystemExit("Could not normalize Engineering filter language labels")

html_path.write_text(html, encoding="utf-8")
