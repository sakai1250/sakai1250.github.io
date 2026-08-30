from pathlib import Path
import re


js_path = Path("main.js")
js = js_path.read_text(encoding="utf-8")

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

plain_anchor_click = """        i.addEventListener('click', () => switchTab(id, true));
        i.addEventListener('keydown', (e) => {
"""
enhanced_anchor_click = """        i.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(id, true);
        });
        i.addEventListener('keydown', (e) => {
"""
if plain_anchor_click in js:
    js = js.replace(plain_anchor_click, enhanced_anchor_click, 1)
elif enhanced_anchor_click not in js:
    raise SystemExit("Could not find expected primary tab click handling")

enhanced_primary_keyboard = """        i.addEventListener('keydown', (e) => {
            const items = Array.from(tabItems);
            const current = items.indexOf(i);
            let next;
            if (e.key === 'ArrowRight') next = (current + 1) % items.length;
            else if (e.key === 'ArrowLeft') next = (current - 1 + items.length) % items.length;
            else if (e.key === 'Home') next = 0;
            else if (e.key === 'End') next = items.length - 1;
            else return;
            e.preventDefault();
            items[next].focus();
            switchTab(items[next].getAttribute('data-tab'), true);
        });
"""
if enhanced_primary_keyboard not in js:
    raise SystemExit("Could not find expected primary tab keyboard handling")

new_section_state = """    tabs.forEach((tab, index) => {
        const active = index === activeIndex;
        tab.classList.toggle('active', active);
        if (active) tab.setAttribute('aria-current', 'true');
        else tab.removeAttribute('aria-current');
    });"""
if new_section_state not in js:
    old_section_state = "    tabs.forEach((tab, index) => tab.classList.toggle('active', index === activeIndex));"
    if old_section_state not in js:
        raise SystemExit("Could not find expected section tab state update")
    js = js.replace(old_section_state, new_section_state, 1)

focus_trapped_modal = """function initModals() {
    const modal = document.getElementById('app-modal');
    if (!modal) return;
    const dialog = modal.querySelector('.modal-container');
    const img = document.getElementById('modal-img'), title = document.getElementById('modal-title'), desc = document.getElementById('modal-desc'), links = document.getElementById('modal-links');
    let opener = null;

    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'modal-title');

    const close = () => {
        if (!modal.classList.contains('open')) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        opener?.focus();
        opener = null;
    };

    document.querySelectorAll('.app-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('a')) return;
            const thumb = card.querySelector('.app-thumb');
            const cardTitle = card.querySelector('.app-title');
            if (!thumb || !cardTitle) return;
            opener = card;
            img.src = thumb.src;
            title.textContent = cardTitle.textContent;
            desc.textContent = card.querySelector('.app-desc')?.textContent || '';
            links.innerHTML = card.querySelector('.app-links')?.innerHTML || '';
            modal.classList.add('open');
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
            dialog?.focus();
        });
    });
    modal.querySelector('.modal-close')?.addEventListener('click', close);
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
    document.addEventListener('keydown', (e) => {
        if (!modal.classList.contains('open')) return;
        if (e.key === 'Escape') {
            close();
            return;
        }
        if (e.key !== 'Tab') return;

        const focusable = Array.from(modal.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )).filter(el => !el.hasAttribute('hidden') && el.offsetParent !== null);
        if (!focusable.length) {
            e.preventDefault();
            dialog?.focus();
            return;
        }

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;
        if (e.shiftKey && (active === first || active === dialog || !modal.contains(active))) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && (active === last || !modal.contains(active))) {
            e.preventDefault();
            first.focus();
        }
    });
}
"""

keyboard_modal = """function initModals() {
    const modal = document.getElementById('app-modal');
    if (!modal) return;
    const dialog = modal.querySelector('.modal-container');
    const img = document.getElementById('modal-img'), title = document.getElementById('modal-title'), desc = document.getElementById('modal-desc'), links = document.getElementById('modal-links');
    let opener = null;

    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'modal-title');

    const close = () => {
        if (!modal.classList.contains('open')) return;
        modal.classList.remove('open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        opener?.focus();
        opener = null;
    };

    const openModal = (card, trigger) => {
        const thumb = card.querySelector('.app-thumb');
        const cardTitle = card.querySelector('.app-title');
        if (!thumb || !cardTitle) return;
        opener = trigger;
        img.src = thumb.src;
        title.textContent = cardTitle.textContent;
        desc.textContent = card.querySelector('.app-desc')?.textContent || '';
        links.innerHTML = card.querySelector('.app-links')?.innerHTML || '';
        modal.classList.add('open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        dialog?.focus();
    };

    document.querySelectorAll('.app-card').forEach(card => {
        const appLinks = card.querySelector('.app-links');
        if (!appLinks) return;

        let trigger = appLinks.querySelector('.app-detail-trigger');
        if (!trigger) {
            trigger = document.createElement('button');
            trigger.type = 'button';
            trigger.className = 'app-detail-trigger';
            trigger.innerHTML = '<span lang="ja">詳細</span><span lang="en">Details</span>';
            appLinks.appendChild(trigger);
        }
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            openModal(card, trigger);
        });
        card.addEventListener('click', (e) => {
            if (e.target.closest('a, button')) return;
            openModal(card, trigger);
        });
    });
    modal.querySelector('.modal-close')?.addEventListener('click', close);
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
    document.addEventListener('keydown', (e) => {
        if (!modal.classList.contains('open')) return;
        if (e.key === 'Escape') {
            close();
            return;
        }
        if (e.key !== 'Tab') return;

        const focusable = Array.from(modal.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )).filter(el => !el.hasAttribute('hidden') && el.offsetParent !== null);
        if (!focusable.length) {
            e.preventDefault();
            dialog?.focus();
            return;
        }

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const active = document.activeElement;
        if (e.shiftKey && (active === first || active === dialog || !modal.contains(active))) {
            e.preventDefault();
            last.focus();
        } else if (!e.shiftKey && (active === last || !modal.contains(active))) {
            e.preventDefault();
            first.focus();
        }
    });
}
"""

resource_only_modal = keyboard_modal.replace(
    "        links.innerHTML = card.querySelector('.app-links')?.innerHTML || '';",
    """        const linkSource = card.querySelector('.app-links')?.cloneNode(true);
        linkSource?.querySelector('.app-detail-trigger')?.remove();
        links.replaceChildren(...(linkSource ? Array.from(linkSource.childNodes) : []));""",
)

if focus_trapped_modal in js:
    js = js.replace(focus_trapped_modal, resource_only_modal, 1)
elif keyboard_modal in js:
    js = js.replace(keyboard_modal, resource_only_modal, 1)
elif resource_only_modal not in js:
    raise SystemExit("Could not find expected app modal behavior")

if "linkSource?.querySelector('.app-detail-trigger')?.remove();" not in js:
    raise SystemExit("App modal must exclude the Details trigger from copied resources")

accessible_toc = """function initTOC() {
    const fab = document.getElementById('toc-fab'), menu = document.getElementById('toc-menu');
    if (fab && menu) {
        const setOpen = (open) => {
            menu.classList.toggle('show', open);
            fab.setAttribute('aria-expanded', String(open));
        };
        fab.setAttribute('aria-controls', 'toc-menu');
        setOpen(menu.classList.contains('show'));
        fab.addEventListener('click', () => setOpen(!menu.classList.contains('show')));
        document.addEventListener('click', (e) => {
            if (!menu.contains(e.target) && !fab.contains(e.target)) setOpen(false);
        });
        updateTOC();
        updateSectionTabs();
    }
}
"""

escape_dismissible_toc = """function initTOC() {
    const fab = document.getElementById('toc-fab'), menu = document.getElementById('toc-menu');
    if (fab && menu) {
        const setOpen = (open) => {
            menu.classList.toggle('show', open);
            fab.setAttribute('aria-expanded', String(open));
        };
        fab.setAttribute('aria-controls', 'toc-menu');
        setOpen(menu.classList.contains('show'));
        fab.addEventListener('click', () => setOpen(!menu.classList.contains('show')));
        document.addEventListener('click', (e) => {
            if (!menu.contains(e.target) && !fab.contains(e.target)) setOpen(false);
        });
        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape' || !menu.classList.contains('show')) return;
            setOpen(false);
            fab.focus();
        });
        updateTOC();
        updateSectionTabs();
    }
}
"""
if accessible_toc in js:
    js = js.replace(accessible_toc, escape_dismissible_toc, 1)
elif escape_dismissible_toc not in js:
    raise SystemExit("Could not find expected TOC disclosure behavior")

old_toc_link_close = "            document.getElementById('toc-menu').classList.remove('show');"
new_toc_link_close = """            document.getElementById('toc-menu').classList.remove('show');
            document.getElementById('toc-fab')?.setAttribute('aria-expanded', 'false');"""
if new_toc_link_close not in js:
    if old_toc_link_close not in js:
        raise SystemExit("Could not find expected TOC link close behavior")
    js = js.replace(old_toc_link_close, new_toc_link_close, 1)

toc_data_title = "        a.setAttribute('data-title', text);"
toc_accessible_name = """        a.setAttribute('data-title', text);
        a.setAttribute('aria-label', text);"""
if toc_accessible_name not in js:
    if toc_data_title not in js:
        raise SystemExit("Could not find expected TOC link label setup")
    js = js.replace(toc_data_title, toc_accessible_name, 1)

js_path.write_text(js, encoding="utf-8")

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")
html = re.sub(
    r'(<nav class="tab-nav header-tab-nav" aria-label="Primary sections") role="tablist"(>)',
    r'\1\2',
    html,
    count=1,
)
for tab_id in ("research", "engineer"):
    pattern = re.compile(rf'<(?:button|a)\s+([^>]*\bid="{tab_id}-tab"[^>]*)>([\s\S]*?)</(?:button|a)>')
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find expected {tab_id} primary navigation control")
    attrs, body = match.group(1), match.group(2)
    for attr_pattern in (
        r'\s+role="tab"', r'\s+aria-controls="[^"]+"', r'\s+aria-selected="(?:true|false)"',
        r'\s+tabindex="-?\d+"', r'\s+type="button"', r'\s+href="[^"]+"',
    ):
        attrs = re.sub(attr_pattern, '', attrs)
    replacement = f'<a {attrs} href="#{tab_id}-content">{body}</a>'
    html = html[:match.start()] + replacement + html[match.end():]

for tab_id in ("research", "engineer"):
    pattern = re.compile(rf'<div\s+([^>]*\bid="{tab_id}-content"[^>]*)>')
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find expected {tab_id} content panel")
    attrs = re.sub(r'\s+role="tabpanel"', '', match.group(1))
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

old_toc_tooltip = ".toc-link:hover::after { opacity: 1; visibility: visible; transform: translateY(-50%) translateX(0); }"
new_toc_tooltip = """.toc-link:hover::after,
.toc-link:focus-visible::after { opacity: 1; visibility: visible; transform: translateY(-50%) translateX(0); }"""
if old_toc_tooltip in css:
    css = css.replace(old_toc_tooltip, new_toc_tooltip, 1)
elif new_toc_tooltip not in css:
    raise SystemExit("Could not find expected TOC tooltip styling")

if '.app-detail-trigger {' not in css:
    css += """

.app-detail-trigger {
  border: 0;
  padding: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
}

.app-detail-trigger:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 3px;
}
"""

css_path.write_text(css, encoding="utf-8")
