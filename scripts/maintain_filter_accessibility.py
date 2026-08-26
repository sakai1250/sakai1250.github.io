from pathlib import Path


path = Path("main.js")
text = path.read_text(encoding="utf-8")

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

path.write_text(text, encoding="utf-8")
