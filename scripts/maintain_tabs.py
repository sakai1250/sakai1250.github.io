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

# Without JavaScript these controls are ordinary page links. Once JavaScript
# upgrades them into tabs, prevent the anchor's default jump so switching tabs
# does not unexpectedly move the viewport, especially on mobile.
legacy_keyboard = """        const activate = () => switchTab(id, true);
        i.addEventListener('click', activate);
        i.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                activate();
                return;
            }
"""
plain_anchor_click = """        i.addEventListener('click', () => switchTab(id, true));
        i.addEventListener('keydown', (e) => {
"""
enhanced_anchor_click = """        i.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(id, true);
        });
        i.addEventListener('keydown', (e) => {
"""
if legacy_keyboard in js:
    js = js.replace(legacy_keyboard, enhanced_anchor_click, 1)
elif plain_anchor_click in js:
    js = js.replace(plain_anchor_click, enhanced_anchor_click, 1)
elif enhanced_anchor_click not in js:
    raise SystemExit("Could not find expected primary tab click handling")

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

# The app detail overlay must behave like a dialog once JavaScript opens it.
# Keep its hidden state synchronized for assistive technology, allow Escape to
# close it, keep keyboard focus inside it, and return focus to the invoking card.
old_modal = """function initModals() {
    const modal = document.getElementById('app-modal');
    if (!modal) return;
    const img = document.getElementById('modal-img'), title = document.getElementById('modal-title'), desc = document.getElementById('modal-desc'), links = document.getElementById('modal-links');
    document.querySelectorAll('.app-card').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('a')) return;
            img.src = card.querySelector('.app-thumb').src;
            title.textContent = card.querySelector('.app-title').textContent;
            desc.textContent = card.querySelector('.app-desc').textContent;
            links.innerHTML = card.querySelector('.app-links')?.innerHTML || '';
            modal.classList.add('open');
            document.body.style.overflow = 'hidden';
        });
    });
    const close = () => { modal.classList.remove('open'); document.body.style.overflow = ''; };
    modal.querySelector('.modal-close')?.addEventListener('click', close);
    modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
}
"""
accessible_modal = """function initModals() {
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
        if (e.key === 'Escape' && modal.classList.contains('open')) close();
    });
}
"""
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
if old_modal in js:
    js = js.replace(old_modal, focus_trapped_modal, 1)
elif accessible_modal in js:
    js = js.replace(accessible_modal, focus_trapped_modal, 1)
elif focus_trapped_modal not in js:
    raise SystemExit("Could not find expected app modal behavior")

# The floating table of contents becomes an interactive disclosure only after
# JavaScript initializes it. Expose its controlled element and expanded state at
# that same point, then keep the state synchronized for every close path.
old_toc = """function initTOC() {
    const fab = document.getElementById('toc-fab'), menu = document.getElementById('toc-menu');
    if (fab && menu) {
        fab.addEventListener('click', () => menu.classList.toggle('show'));
        document.addEventListener('click', (e) => { if (!menu.contains(e.target) && !fab.contains(e.target)) menu.classList.remove('show'); });
        updateTOC();
        updateSectionTabs();
    }
}
"""
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
if old_toc in js:
    js = js.replace(old_toc, accessible_toc, 1)
elif accessible_toc not in js:
    raise SystemExit("Could not find expected TOC disclosure behavior")

old_toc_link_close = "            document.getElementById('toc-menu').classList.remove('show');"
new_toc_link_close = """            document.getElementById('toc-menu').classList.remove('show');
            document.getElementById('toc-fab')?.setAttribute('aria-expanded', 'false');"""
if new_toc_link_close not in js:
    if old_toc_link_close in js:
        js = js.replace(old_toc_link_close, new_toc_link_close, 1)
    else:
        raise SystemExit("Could not find expected TOC link close behavior")

js_path.write_text(js, encoding="utf-8")

html_path = Path("index.html")
html = html_path.read_text(encoding="utf-8")

# Without JavaScript both primary sections remain visible. Keep these controls as
# real page links so Research / Engineering navigation still works when scripts
# fail. Runtime JavaScript adds tab semantics only after it starts hiding inactive
# panels.
html = re.sub(
    r'(<nav class="tab-nav header-tab-nav" aria-label="Primary sections") role="tablist"(>)',
    r'\1\2',
    html,
    count=1,
)

for tab_id in ("research", "engineer"):
    pattern = re.compile(
        rf'<(?:button|a)\s+([^>]*\bid="{tab_id}-tab"[^>]*)>([\s\S]*?)</(?:button|a)>'
    )
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find expected {tab_id} primary navigation control")
    attrs = match.group(1)
    body = match.group(2)
    for attr_pattern in (
        r'\s+role="tab"',
        r'\s+aria-controls="[^"]+"',
        r'\s+aria-selected="(?:true|false)"',
        r'\s+tabindex="-?\d+"',
        r'\s+type="button"',
        r'\s+href="[^"]+"',
    ):
        attrs = re.sub(attr_pattern, '', attrs)
    replacement = f'<a {attrs} href="#{tab_id}-content">{body}</a>'
    html = html[:match.start()] + replacement + html[match.end():]

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

# The floating table-of-contents links expose their section names on pointer
# hover. Show the same label for keyboard focus so an icon-only control is not
# ambiguous to sighted keyboard users.
old_toc_tooltip = ".toc-link:hover::after { opacity: 1; visibility: visible; transform: translateY(-50%) translateX(0); }"
new_toc_tooltip = """.toc-link:hover::after,
.toc-link:focus-visible::after { opacity: 1; visibility: visible; transform: translateY(-50%) translateX(0); }"""
if old_toc_tooltip in css:
    css = css.replace(old_toc_tooltip, new_toc_tooltip, 1)
elif new_toc_tooltip not in css:
    raise SystemExit("Could not find expected TOC tooltip styling")

css_path.write_text(css, encoding="utf-8")