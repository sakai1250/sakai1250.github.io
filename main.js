/**
 * Taigo Sakai Portfolio - Core Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    // Basic Loader
    initLoader();

    // Core Modules
    const safeInit = (fn, name) => {
        if (typeof fn !== 'function') {
            console.warn(`Function ${name} is not defined. Skipping.`);
            return;
        }
        try { fn(); } catch (e) { console.error(`Error in ${name}:`, e); }
    };

    safeInit(initTabs, 'Tabs');
    safeInit(initTheme, 'Theme');
    safeInit(initModals, 'Modals');
    safeInit(initStats, 'Stats');
    safeInit(initSearchAndFilters, 'SearchAndFilters');
    safeInit(initCopyButtons, 'CopyButtons');
    safeInit(initTOC, 'TOC');
    safeInit(initSectionTabs, 'SectionTabs');
    safeInit(initQiitaArticles, 'QiitaArticles');
    safeInit(initContactForm, 'ContactForm');
    safeInit(initStickyHeader, 'StickyHeader');
    safeInit(initScrollReveal, 'ScrollReveal');
    safeInit(initReadingProgress, 'ReadingProgress');
    safeInit(initCommandPalette, 'CommandPalette');
    safeInit(initLanguage, 'Language');

    // Visual Effects (From effects.js)
    safeInit(window.init3DEffects || init3DEffects, '3DEffects');
    safeInit(window.initBackgroundParticles || initBackgroundParticles, 'BackgroundParticles');
    safeInit(window.initTypingEffect || initTypingEffect, 'TypingEffect');
});

// === Core Functions ===

function initLoader() {
    const loader = document.getElementById('loading-screen');
    if (!loader) return;
    const hide = () => {
        if (loader.classList.contains('hidden')) return;
        loader.classList.add('hidden');
        document.body.style.overflow = '';
        // After transition, remove from layout and block interaction
        const onEnd = (e) => {
            if (e && e.target !== loader) return;
            loader.style.display = 'none';
            loader.setAttribute('aria-hidden', 'true');
            loader.removeEventListener('transitionend', onEnd);
        };
        loader.addEventListener('transitionend', onEnd);
        // Fallback if transitionend doesn't fire
        setTimeout(() => {
            if (loader.style.display !== 'none') {
                loader.style.display = 'none';
                loader.setAttribute('aria-hidden', 'true');
            }
        }, 700);
    };

    if (document.readyState === 'complete') {
        setTimeout(hide, 200);
    } else {
        window.addEventListener('load', () => setTimeout(hide, 500));
    }

    // Safety timeout in case load never fires
    setTimeout(hide, 3000);
}

function initTabs() {
    const tabItems = document.querySelectorAll('.tab-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const switchTab = (id) => {
        tabItems.forEach(i => i.classList.toggle('active', i.getAttribute('data-tab') === id));
        tabContents.forEach(c => {
            const active = c.id === `${id}-content`;
            c.classList.toggle('active', active);
            c.style.display = active ? 'block' : 'none';
        });
        if (typeof updateTOC === 'function') updateTOC();
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };
    tabItems.forEach(i => {
        const activate = () => switchTab(i.getAttribute('data-tab'));
        i.addEventListener('click', activate);
        i.addEventListener('keydown', (e) => {
            if (e.key !== 'Enter' && e.key !== ' ') return;
            e.preventDefault();
            activate();
        });
    });
}

function initTheme() {
    const btn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const set = (t) => {
        document.documentElement.setAttribute('data-theme', t);
        localStorage.setItem('theme', t);
        if (icon) icon.textContent = t === 'dark' ? '☾' : '☀︎';
        document.querySelectorAll('#stats-langs, #stats-general').forEach(img => {
            img.src = img.src.replace(/theme=[^&]+/, `theme=${t === 'dark' ? 'dracula' : 'default'}`);
        });
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) metaThemeColor.setAttribute('content', t === 'dark' ? '#09131F' : '#F7F3EA');
    };
    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'));
    set(localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'));
}

function initSearchAndFilters() {
    const input = document.getElementById('search');
    const chips = document.querySelectorAll('.chip');
    let activeTag = 'all', activeYear = 'all';

    const apply = () => {
        const q = input ? input.value.toLowerCase().trim() : '';
        const activeContent = document.querySelector('.tab-content.active') || document;
        let count = 0;

        activeContent.querySelectorAll('.section-card').forEach(section => {
            section.style.display = '';
        });

        activeContent.querySelectorAll('.repo-list li, .app-card').forEach(item => {
            const text = item.textContent.toLowerCase();
            const tags = (item.getAttribute('data-tags') || '').split(' ');
            const year = item.getAttribute('data-year') || '';
            const tagMatch = !item.classList.contains('app-card') || activeTag === 'all' || tags.includes(activeTag);
            const yearMatch = !year || activeYear === 'all' || year === activeYear;
            const match = (!q || text.includes(q)) && tagMatch && yearMatch;
            item.style.display = match ? '' : 'none';
            if (match) count++;
        });

        activeContent.querySelectorAll('.section-card').forEach(section => {
            const filterableItems = section.querySelectorAll('.repo-list li[data-year], .app-card[data-tags]');
            if (!filterableItems.length) return;
            const visibleItems = Array.from(filterableItems).some(item => item.style.display !== 'none');
            section.style.display = visibleItems ? '' : 'none';
        });

        const countEl = document.getElementById('search-count');
        if (countEl) countEl.textContent = count;
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };

    if (input) input.addEventListener('input', apply);
    chips.forEach(c => c.addEventListener('click', () => {
        const t = c.getAttribute('data-filter'), y = c.getAttribute('data-year');
        if (t) { activeTag = t; document.querySelectorAll('.chip[data-filter]').forEach(x => x.classList.toggle('active', x === c)); }
        if (y) { activeYear = y; document.querySelectorAll('.chip[data-year]').forEach(x => x.classList.toggle('active', x === c)); }
        apply();
    }));
}

function initModals() {
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

function initStats() {
    const animate = (obj, end) => {
        let start = null;
        const step = (ts) => {
            if (!start) start = ts;
            const progress = Math.min((ts - start) / 1500, 1);
            obj.innerHTML = Math.floor(progress * end);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };
    [{ id: 'stat-papers', v: 14 }, { id: 'stat-awards', v: 18 }, { id: 'stat-apps', v: 12 }].forEach(s => {
        const el = document.getElementById(s.id);
        if (el) animate(el, s.v);
    });
}

function initTOC() {
    const fab = document.getElementById('toc-fab'), menu = document.getElementById('toc-menu');
    if (fab && menu) {
        fab.addEventListener('click', () => menu.classList.toggle('show'));
        document.addEventListener('click', (e) => { if (!menu.contains(e.target) && !fab.contains(e.target)) menu.classList.remove('show'); });
        updateTOC();
        updateSectionTabs();
    }
}

function updateTOC() {
    const nav = document.getElementById('toc-nav');
    const content = document.querySelector('.tab-content.active');
    if (!nav || !content) return;
    nav.innerHTML = '';
    const lang = document.documentElement.getAttribute('data-lang') || 'ja';
    content.querySelectorAll('.section-card').forEach((s, i) => {
        const title = s.querySelector('.section-title');
        if (!title) return;
        const text = (title.querySelector(`[lang="${lang}"]`) || title).textContent.trim();
        s.id = `section-${i}`;
        const a = document.createElement('a');
        a.className = 'toc-link';
        a.setAttribute('data-title', text);
        a.textContent = [...text.replace(/[^\w\s]/g, '').trim() || text][0];
        a.href = `#${s.id}`;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            const h = document.querySelector('.header-bar').offsetHeight;
            window.scrollTo({ top: s.getBoundingClientRect().top + window.scrollY - h - 20, behavior: 'smooth' });
            document.getElementById('toc-menu').classList.remove('show');
        });
        nav.appendChild(a);
    });
}

function getActiveSections() {
    const content = document.querySelector('.tab-content.active');
    if (!content) return [];
    return Array.from(content.querySelectorAll('.section-card')).filter(section => section.offsetParent !== null);
}

function getSectionTitle(section) {
    const title = section.querySelector('.section-title');
    if (!title) return '';
    const lang = document.documentElement.getAttribute('data-lang') || 'ja';
    return (title.querySelector(`[lang="${lang}"]`) || title).textContent.trim();
}

function getStickyOffset() {
    const header = document.querySelector('.header-bar');
    const sectionTabs = document.getElementById('section-tab-nav');
    return (header?.offsetHeight || 0) + (sectionTabs?.offsetHeight || 0) + 16;
}

function scrollToSection(section) {
    window.scrollTo({
        top: section.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
        behavior: 'smooth'
    });
}

function updateActiveSectionTab() {
    const sections = getActiveSections();
    const tabs = document.querySelectorAll('.section-tab-item');
    if (!sections.length || !tabs.length) return;

    const targetLine = getStickyOffset() + 48;
    let activeIndex = 0;
    let nearest = Infinity;
    sections.forEach((section, index) => {
        const distance = Math.abs(section.getBoundingClientRect().top - targetLine);
        if (distance < nearest) {
            nearest = distance;
            activeIndex = index;
        }
    });
    tabs.forEach((tab, index) => tab.classList.toggle('active', index === activeIndex));
}

function updateSectionTabs() {
    const nav = document.getElementById('section-tab-nav');
    if (!nav) return;
    const sections = getActiveSections();
    nav.innerHTML = '';

    sections.forEach((section, index) => {
        if (!section.id) section.id = `section-${index}`;
        const button = document.createElement('button');
        button.className = 'section-tab-item';
        button.type = 'button';
        button.textContent = getSectionTitle(section);
        button.addEventListener('click', () => scrollToSection(section));
        nav.appendChild(button);
    });

    updateActiveSectionTab();
}

function initSectionTabs() {
    let ticking = false;
    const requestActiveUpdate = () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
            updateActiveSectionTab();
            ticking = false;
        });
    };

    window.addEventListener('scroll', requestActiveUpdate, { passive: true });
    window.addEventListener('resize', () => {
        updateSectionTabs();
        requestActiveUpdate();
    });
    updateSectionTabs();
}

function initCopyButtons() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            navigator.clipboard.writeText(btn.getAttribute('data-copy')).then(() => {
                const lang = document.documentElement.getAttribute('data-lang') || 'ja';
                const success = btn.getAttribute(`data-${lang}-success`);
                const spans = btn.querySelectorAll('span');
                const originals = Array.from(spans).map(s => s.textContent);
                spans.forEach(s => s.textContent = success);
                btn.classList.add('success');
                setTimeout(() => {
                    spans.forEach((s, i) => s.textContent = originals[i]);
                    btn.classList.remove('success');
                }, 2000);
            });
        });
    });
}

function initStickyHeader() {
    const header = document.querySelector('.header-bar');
    if (!header) return;
    const update = () => {
        header.classList.toggle('scrolled', window.scrollY > 20);
        document.documentElement.style.setProperty('--header-height', `${header.offsetHeight}px`);
    };
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
}

function initScrollReveal() {
    const obs = new IntersectionObserver((es) => {
        es.forEach(e => { if (e.isIntersecting) e.target.classList.add('reveal-active'); });
    }, { threshold: 0.1 });
    document.querySelectorAll('.section-card, .app-card').forEach(el => {
        el.classList.add('reveal-item'); obs.observe(el);
    });
}

function resolveCssColor(element, property) {
    const value = getComputedStyle(element).getPropertyValue(property).trim();
    const match = value.match(/^var\((--[^),\s]+)/);
    if (!match) return value;
    return getComputedStyle(document.documentElement).getPropertyValue(match[1]).trim() || value;
}

function updateSectionBackgroundTone() {
    const cards = Array.from(document.querySelectorAll('.tab-content.active .section-card'))
        .filter(card => card.offsetParent !== null);
    if (!cards.length) return;

    const viewportCenter = window.innerHeight / 2;
    let activeCard = cards[0];
    let nearest = Infinity;

    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        if (rect.bottom < 0 || rect.top > window.innerHeight) return;
        const cardCenter = rect.top + rect.height / 2;
        const distance = Math.abs(cardCenter - viewportCenter);
        if (distance < nearest) {
            nearest = distance;
            activeCard = card;
        }
    });

    document.documentElement.style.setProperty('--page-bg-accent', resolveCssColor(activeCard, '--section-accent'));
}

function initSectionBackgroundTone() {
    let ticking = false;
    const requestUpdate = () => {
        if (ticking) return;
        ticking = true;
        requestAnimationFrame(() => {
            updateSectionBackgroundTone();
            ticking = false;
        });
    };

    window.addEventListener('scroll', requestUpdate, { passive: true });
    window.addEventListener('resize', requestUpdate);
    document.querySelectorAll('.tab-item').forEach(item => {
        item.addEventListener('click', () => setTimeout(updateSectionBackgroundTone, 0));
    });
    updateSectionBackgroundTone();
}

function initReadingProgress() {
    const fab = document.getElementById('toc-fab');
    if (!fab) return;
    fab.insertAdjacentHTML('beforeend', `
        <svg class="progress-ring" width="56" height="56">
            <circle class="progress-ring__circle" stroke="var(--accent)" stroke-width="3" fill="transparent" r="26" cx="28" cy="28"/>
        </svg>
    `);
    const circle = fab.querySelector('.progress-ring__circle');
    if (!circle) return;
    const r = 26, c = r * 2 * Math.PI;
    circle.style.strokeDasharray = `${c} ${c}`;
    circle.style.strokeDashoffset = c;
    window.addEventListener('scroll', () => {
        const h = document.documentElement, b = document.body;
        const p = (h.scrollTop || b.scrollTop) / (h.scrollHeight - h.clientHeight);
        circle.style.strokeDashoffset = c - (p * c);
    }, { passive: true });
}

function initCommandPalette() {
    const p = document.getElementById('command-palette');
    const input = document.getElementById('palette-input'), res = document.getElementById('palette-results');
    if (!p || !input) return;
    const toggle = (s) => { p.classList.toggle('active', s); if (s) { input.value = ''; update(''); input.focus(); } };
    const update = (q) => {
        res.innerHTML = '';
        document.querySelectorAll('.section-title').forEach(t => {
            if (t.textContent.toLowerCase().includes(q.toLowerCase())) {
                const d = document.createElement('div');
                d.className = 'palette-item'; d.textContent = t.textContent;
                d.addEventListener('click', () => { t.scrollIntoView({ behavior: 'smooth' }); toggle(false); });
                res.appendChild(d);
            }
        });
    };
    input.addEventListener('input', (e) => update(e.target.value));
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); toggle(!p.classList.contains('active')); }
        if (e.key === 'Escape') toggle(false);
    });
}

function initLanguage() {
    const btn = document.getElementById('lang-toggle');
    const set = (l) => {
        document.documentElement.setAttribute('data-lang', l);
        localStorage.setItem('lang', l);
        const s = document.getElementById('search');
        if (s) s.placeholder = s.getAttribute(`data-${l}-placeholder`);
        
        // Ensure the active tab content is visible
        const activeTabItem = document.querySelector('.tab-item.active');
        if (activeTabItem) {
            const tabId = activeTabItem.getAttribute('data-tab');
            const targetId = `${tabId}-content`;
            document.querySelectorAll('.tab-content').forEach(tc => {
                tc.style.display = tc.id === targetId ? 'block' : 'none';
            });
        }
        updateTOC();
        updateSectionTabs();
    };
    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-lang') === 'ja' ? 'en' : 'ja'));
    set(localStorage.getItem('lang') || 'ja');
}

function initContactForm() {
    const f = document.getElementById('contact-form');
    if (!f) return;
    f.addEventListener('submit', async (e) => {
        e.preventDefault();
        const s = document.getElementById('form-status'), b = f.querySelector('button');
        b.disabled = true; b.textContent = '...';
        try {
            const r = await fetch(f.action, { method: f.method, body: new FormData(f), headers: { 'Accept': 'application/json' } });
            s.textContent = r.ok ? 'Success!' : 'Error';
            if (r.ok) f.reset();
        } catch { s.textContent = 'Error'; }
        b.disabled = false; b.textContent = 'Send';
    });
}

async function initQiitaArticles() {
    const c = document.getElementById('qiita-list');
    if (!c) return;
    try {
        const r = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent('https://qiita.com/sakai1250/feed')}`);
        const d = await r.json();
        if (d.status === 'ok') {
            c.innerHTML = '';
            d.items.slice(0, 5).forEach(i => {
                const l = document.createElement('li');
                l.innerHTML = `<a href="${i.link}" target="_blank">${i.title}</a>`;
                c.appendChild(l);
            });
        }
    } catch { c.innerHTML = 'Error'; }
}
