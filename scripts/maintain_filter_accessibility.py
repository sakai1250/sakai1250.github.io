"""Keep filter buttons' visual and screen-reader selection state aligned."""

from pathlib import Path
import re


js_path = Path("main.js")
text = js_path.read_text(encoding="utf-8")

old_init = """    const input = document.getElementById('search');
    const chips = document.querySelectorAll('.chip');
    let activeTag = 'all', activeYear = 'all';
"""
new_init = """    const input = document.getElementById('search');
    const chips = document.querySelectorAll('.chip');
    let activeTag = 'all', activeYear = 'all';

    chips.forEach(chip => {
        chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
    });
"""

if old_init in text:
    text = text.replace(old_init, new_init, 1)
elif new_init not in text:
    raise SystemExit("Could not find filter initialization block")

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

if old_click in text:
    text = text.replace(old_click, new_click, 1)
elif new_click not in text:
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

html_path.write_text(html, encoding="utf-8")
