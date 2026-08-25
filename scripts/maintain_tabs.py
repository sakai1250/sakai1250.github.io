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
