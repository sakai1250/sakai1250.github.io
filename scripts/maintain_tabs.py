from pathlib import Path


path = Path("main.js")
text = path.read_text(encoding="utf-8")

old = """function initTabs() {
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const validTabs = new Set(Array.from(tabItems, item => item.getAttribute('data-tab')).filter(Boolean));
    const tabFromHash = () => {
        const match = window.location.hash.match(/^#([a-z0-9-]+)-content$/i);
        return match && validTabs.has(match[1]) ? match[1] : null;
    };
    const switchTab = (id, updateHash = false) => {
        if (!validTabs.has(id)) return;
        tabItems.forEach(i => i.classList.toggle('active', i.getAttribute('data-tab') === id));
        tabContents.forEach(c => {
            const active = c.id === `${id}-content`;
            c.classList.toggle('active', active);
            c.style.display = active ? 'block' : 'none';
        });
        if (updateHash) history.replaceState(null, '', `#${id}-content`);
        if (typeof updateTOC === 'function') updateTOC();
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };
    tabItems.forEach(i => {
        const activate = () => switchTab(i.getAttribute('data-tab'), true);
        i.addEventListener('click', activate);
        i.addEventListener('keydown', (e) => {
            if (e.key !== 'Enter' && e.key !== ' ') return;
            e.preventDefault();
            activate();
        });
    });
    const initialTab = tabFromHash();
    if (initialTab) switchTab(initialTab);
    window.addEventListener('hashchange', () => {
        const tab = tabFromHash();
        if (tab) switchTab(tab);
    });
}
"""

new = """function initTabs() {
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const tabNav = document.querySelector('.tab-nav');
    const validTabs = new Set(Array.from(tabItems, item => item.getAttribute('data-tab')).filter(Boolean));
    if (tabNav) tabNav.setAttribute('role', 'tablist');
    tabItems.forEach(i => {
        const id = i.getAttribute('data-tab');
        i.setAttribute('role', 'tab');
        i.setAttribute('aria-controls', `${id}-content`);
    });
    tabContents.forEach(c => {
        c.setAttribute('role', 'tabpanel');
        c.setAttribute('aria-labelledby', `${c.id.replace(/-content$/, '')}-tab`);
    });
    const tabFromHash = () => {
        const match = window.location.hash.match(/^#([a-z0-9-]+)-content$/i);
        return match && validTabs.has(match[1]) ? match[1] : null;
    };
    const switchTab = (id, updateHash = false) => {
        if (!validTabs.has(id)) return;
        tabItems.forEach(i => {
            const active = i.getAttribute('data-tab') === id;
            i.classList.toggle('active', active);
            i.setAttribute('aria-selected', String(active));
            i.tabIndex = active ? 0 : -1;
        });
        tabContents.forEach(c => {
            const active = c.id === `${id}-content`;
            c.classList.toggle('active', active);
            c.style.display = active ? 'block' : 'none';
            c.hidden = !active;
        });
        if (updateHash) history.replaceState(null, '', `#${id}-content`);
        if (typeof updateTOC === 'function') updateTOC();
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };
    tabItems.forEach(i => {
        const id = i.getAttribute('data-tab');
        i.id = `${id}-tab`;
        const activate = () => switchTab(id, true);
        i.addEventListener('click', activate);
        i.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                activate();
                return;
            }
            if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
            e.preventDefault();
            const items = Array.from(tabItems);
            const current = items.indexOf(i);
            const next = e.key === 'ArrowRight'
                ? (current + 1) % items.length
                : (current - 1 + items.length) % items.length;
            items[next].focus();
            switchTab(items[next].getAttribute('data-tab'), true);
        });
    });
    const initialTab = tabFromHash() || Array.from(tabItems).find(i => i.classList.contains('active'))?.getAttribute('data-tab');
    if (initialTab) switchTab(initialTab);
    window.addEventListener('hashchange', () => {
        const tab = tabFromHash();
        if (tab) switchTab(tab);
    });
}
"""

if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise SystemExit("Could not find expected initTabs implementation")

path.write_text(text, encoding="utf-8")

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

old_nav = '<nav class="tab-nav header-tab-nav" aria-label="Primary sections">'
new_nav = '<nav class="tab-nav header-tab-nav" aria-label="Primary sections" role="tablist">'
if old_nav in html:
    html = html.replace(old_nav, new_nav, 1)
elif new_nav not in html:
    raise SystemExit("Could not find expected primary tab navigation")

old_research = '<div class="tab-item active" data-tab="research" role="button" tabindex="0">'
new_research = '<div class="tab-item active" id="research-tab" data-tab="research" role="tab" aria-controls="research-content" aria-selected="true" tabindex="0">'
if old_research in html:
    html = html.replace(old_research, new_research, 1)
elif new_research not in html:
    raise SystemExit("Could not find expected Research tab")

old_engineer = '<div class="tab-item" data-tab="engineer" role="button" tabindex="0">'
new_engineer = '<div class="tab-item" id="engineer-tab" data-tab="engineer" role="tab" aria-controls="engineer-content" aria-selected="false" tabindex="-1">'
if old_engineer in html:
    html = html.replace(old_engineer, new_engineer, 1)
elif new_engineer not in html:
    raise SystemExit("Could not find expected Engineering tab")

for tab_id in ("research", "engineer"):
    marker = f'id="{tab_id}-content" class="tab-content'
    start = html.find(marker)
    if start == -1:
        raise SystemExit(f"Could not find expected {tab_id} tab panel")
    tag_start = html.rfind('<', 0, start)
    tag_end = html.find('>', start)
    tag = html[tag_start:tag_end + 1]
    role = 'role="tabpanel"'
    label = f'aria-labelledby="{tab_id}-tab"'
    if role not in tag or label not in tag:
        attrs = ''
        if role not in tag:
            attrs += f' {role}'
        if label not in tag:
            attrs += f' {label}'
        replacement = tag[:-1] + attrs + '>'
        html = html[:tag_start] + replacement + html[tag_end + 1:]

html_path.write_text(html, encoding="utf-8")
