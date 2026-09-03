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
tab_year_sync = """    const yearFilterRow = document.querySelector('.year-filter');
    const syncYearFilterForTab = (activeContent) => {
        const engineeringActive = activeContent?.id === 'engineer-content';
        if (yearFilterRow) yearFilterRow.hidden = engineeringActive;
        if (!engineeringActive || activeYear === 'all') return;

        activeYear = 'all';
        document.querySelectorAll('.chip[data-year]').forEach(x => {
            const active = x.getAttribute('data-year') === 'all';
            x.classList.toggle('active', active);
            x.setAttribute('aria-pressed', String(active));
        });
    };
"""
expected_generated_init = base_init + "\n" + pressed_init + "\n" + tab_year_sync

if base_init not in text:
    raise SystemExit("Could not find filter initialization block")

# Do not rewrite an already-correct generated block. Repeatedly deleting and
# reinserting it leaves surrounding blank lines behind, which makes every
# maintenance pass change main.js even though behavior is already correct.
if expected_generated_init not in text:
    text = text.replace("\n" + pressed_init, "")
    text = re.sub(
        r"\n    const yearFilterRow = document\.querySelector\('\.year-filter'\);\n"
        r"    const syncYearFilterForTab = \(activeContent\) => \{[\s\S]*?\n    \};\n",
        "\n",
        text,
        count=1,
    )
    text = text.replace(base_init, expected_generated_init, 1)

old_apply_head = """    const apply = () => {
        const q = input ? input.value.toLowerCase().trim() : '';
        const activeContent = document.querySelector('.tab-content.active') || document;
        let count = 0;
"""
new_apply_head = """    const apply = () => {
        const q = input ? input.value.toLowerCase().trim() : '';
        const activeContent = document.querySelector('.tab-content.active') || document;
        syncYearFilterForTab(activeContent);
        let count = 0;
"""
if new_apply_head not in text:
    if old_apply_head in text:
        text = text.replace(old_apply_head, new_apply_head, 1)
    else:
        raise SystemExit("Could not find filter apply block")

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

old_count = """        const countEl = document.getElementById('search-count');
        if (countEl) countEl.textContent = count;
"""
new_count = """        const countEl = document.getElementById('search-count');
        if (countEl) {
            const ja = countEl.querySelector('[lang=\"ja\"]');
            const en = countEl.querySelector('[lang=\"en\"]');
            if (ja) ja.textContent = `${count}件`;
            if (en) en.textContent = `${count} items`;
        }
"""
if new_count not in text:
    if old_count in text:
        text = text.replace(old_count, new_count, 1)
    else:
        raise SystemExit("Could not find filter result count block")

# Keep section navigation derived from the same visible section set as the
# sticky section tabs. Filters can hide whole sections, so rebuilding the TOC
# from every section leaves links pointing to currently hidden content.
old_toc_loop = "    content.querySelectorAll('.section-card').forEach((s, i) => {"
visible_toc_loop = "    getActiveSections().forEach((s, i) => {"
if visible_toc_loop not in text:
    if old_toc_loop in text:
        text = text.replace(old_toc_loop, visible_toc_loop, 1)
    else:
        raise SystemExit("Could not find table-of-contents section loop")

old_filter_nav_update = """        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };
"""
new_filter_nav_update = """        if (typeof updateTOC === 'function') updateTOC();
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };
"""
if new_filter_nav_update not in text:
    if old_filter_nav_update in text:
        text = text.replace(old_filter_nav_update, new_filter_nav_update, 1)
    else:
        raise SystemExit("Could not find filter navigation update block")

old_listener_end = """        apply();
    }));
}
"""
new_listener_end = """        apply();
    }));
    window.addEventListener('portfolio:tabchange', apply);
    apply();
}
"""
old_listener_with_initial_apply = """        apply();
    }));
    apply();
}
"""
if new_listener_end not in text:
    if old_listener_with_initial_apply in text:
        text = text.replace(old_listener_with_initial_apply, new_listener_end, 1)
    elif old_listener_end in text:
        text = text.replace(old_listener_end, new_listener_end, 1)
    else:
        raise SystemExit("Could not find filter listener block")

old_tab_update = """        if (typeof updateTOC === 'function') updateTOC();
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
"""
new_tab_update = """        if (typeof updateTOC === 'function') updateTOC();
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
        window.dispatchEvent(new Event('portfolio:tabchange'));
"""
if new_tab_update not in text:
    if old_tab_update in text:
        text = text.replace(old_tab_update, new_tab_update, 1)
    else:
        raise SystemExit("Could not find tab update block")

if "engineering-content" in text:
    raise SystemExit("Stale Engineering tab id remains in generated filter code")
if "activeContent?.id === 'engineer-content'" not in text:
    raise SystemExit("Engineering year-filter synchronization was not generated")
if visible_toc_loop not in text or new_filter_nav_update not in text:
    raise SystemExit("Filtered section navigation synchronization was not generated")

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

# The filter chips act as one control set, not a collection of unrelated
# buttons. Group and name both rows so screen readers announce the purpose
# before users move through the individual filter choices.
filter_groups = {
    '<div class="filter-row year-filter">': (
        '<div class="filter-row year-filter" role="group" '
        'aria-label="Filter research outputs by year / 研究業績を年度で絞り込む">'
    ),
    '<div class="filter-row">': (
        '<div class="filter-row" role="group" '
        'aria-label="Filter engineering work / 開発実績を絞り込む">'
    ),
}
for plain_row, named_row in filter_groups.items():
    if plain_row in html:
        html = html.replace(plain_row, named_row, 1)
    elif named_row not in html:
        raise SystemExit(f"Could not find filter group: {plain_row}")

status_html = (
    '<span id="search-count" class="filter-label" role="status" '
    'aria-live="polite" aria-atomic="true">'
    '<span lang="ja"></span>'
    '<span lang="en"></span>'
    '</span>'
)
if status_html not in html:
    year_filter = re.search(r'(<div class="filter-row year-filter"[^>]*>[\s\S]*?)(\n\s*</div>)', html)
    if not year_filter:
        raise SystemExit("Could not find year filter row for result status")
    block = year_filter.group(1)
    if 'id="search-count"' in block:
        block = re.sub(r'<span id="search-count"[\s\S]*?</span>\s*</span>', status_html, block, count=1)
    else:
        block += "\n            " + status_html
    html = html[:year_filter.start(1)] + block + html[year_filter.end(1):]

if html.count('id="search-count"') != 1:
    raise SystemExit("Expected exactly one filter result status element")

html_path.write_text(html, encoding="utf-8")