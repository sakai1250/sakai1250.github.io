/**
 * Taigo Sakai Portfolio - Core Logic
 */

document.addEventListener('DOMContentLoaded', () => {
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
    safeInit(initLanguage, 'Language');
    safeInit(initModals, 'Modals');
    safeInit(initStats, 'Stats');
    safeInit(initSearchAndFilters, 'SearchAndFilters');
    safeInit(initCopyButtons, 'CopyButtons');
    safeInit(initResearchPriority, 'ResearchPriority');
    safeInit(initTOC, 'TOC');
    safeInit(initSectionTabs, 'SectionTabs');
    safeInit(initQiitaArticles, 'QiitaArticles');
    safeInit(initContactForm, 'ContactForm');
    safeInit(initStickyHeader, 'StickyHeader');
    safeInit(initReadingProgress, 'ReadingProgress');

    // Visual Effects (From effects.js)
    safeInit(window.initBackgroundParticles, 'BackgroundParticles');
    safeInit(window.initTypingEffect, 'TypingEffect');
});

// === Core Functions ===

function safeStorageGet(key) {
    try { return localStorage.getItem(key); } catch { return null; }
}

function safeStorageSet(key, value) {
    try { localStorage.setItem(key, value); } catch {}
}

function initTabs() {
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
        window.dispatchEvent(new Event('portfolio:tabchange'));
    };
    tabItems.forEach(i => {
        const id = i.getAttribute('data-tab');
        i.id = `${id}-tab`;
        i.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(id, true);
        });
        i.addEventListener('keydown', (e) => {
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
    });
    const initialTab = tabFromHash() || Array.from(tabItems).find(i => i.classList.contains('active'))?.getAttribute('data-tab');
    if (initialTab) switchTab(initialTab);
    window.addEventListener('hashchange', () => {
        const tab = tabFromHash();
        if (tab) switchTab(tab);
    });
}

function initTheme() {
    const btn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const set = (t, animate) => {
        if (animate) {
            document.documentElement.classList.add('theme-transitioning');
            window.setTimeout(() => document.documentElement.classList.remove('theme-transitioning'), 340);
            if (icon) {
                icon.classList.remove('theme-icon-swapping');
                void icon.offsetWidth;
                icon.classList.add('theme-icon-swapping');
            }
        }
        document.documentElement.setAttribute('data-theme', t);
        safeStorageSet('theme', t);
        if (icon) icon.textContent = t === 'dark' ? '☾' : '☀︎';
        if (btn) btn.setAttribute('aria-pressed', String(t === 'dark'));
        document.querySelectorAll('#stats-langs, #stats-general').forEach(img => {
            img.src = img.src.replace(/theme=[^&]+/, `theme=${t === 'dark' ? 'dracula' : 'default'}`);
        });
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) metaThemeColor.setAttribute('content', t === 'dark' ? '#09131F' : '#F7F3EA');
    };
    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true));
    set(safeStorageGet('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'), false);
}

function initSearchAndFilters() {
    const input = document.getElementById('search');
    const chips = document.querySelectorAll('.chip');
    let activeTag = 'all', activeYear = 'all';

    chips.forEach(chip => {
        chip.setAttribute('aria-pressed', String(chip.classList.contains('active')));
    });

    const yearFilterRow = document.querySelector('.year-filter');
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







    const apply = () => {
        const q = input ? input.value.toLowerCase().trim() : '';
        const activeContent = document.querySelector('.tab-content.active') || document;
        syncYearFilterForTab(activeContent);
        let count = 0;

        activeContent.querySelectorAll('.section-card').forEach(section => {
            section.style.display = '';
        });

        activeContent.querySelectorAll('.repo-list li, .app-card').forEach(item => {
            const text = item.textContent.toLowerCase();
            const tags = (item.getAttribute('data-tags') || '').split(' ');
            const year = item.getAttribute('data-year') || '';
            const tagMatch = !item.classList.contains('app-card') || activeTag === 'all' || tags.includes(activeTag);
            const yearMatch = activeYear === 'all' || year === activeYear;
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
        if (countEl) {
            const ja = countEl.querySelector('[lang="ja"]');
            const en = countEl.querySelector('[lang="en"]');
            if (ja) ja.textContent = `${count}件`;
            if (en) en.textContent = `${count} items`;
        }
        if (typeof updateSectionTabs === 'function') updateSectionTabs();
    };

    if (input) input.addEventListener('input', apply);
    chips.forEach(c => c.addEventListener('click', () => {
        const t = c.getAttribute('data-filter'), y = c.getAttribute('data-year');
        if (t) {
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
        apply();
    }));
    window.addEventListener('portfolio:tabchange', apply);
    apply();
}

function initModals() {
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
    const researchSections = Array.from(document.querySelectorAll('#research-content .section-card'));
    const findResearchSection = (englishTitle) => researchSections.find(section =>
        section.querySelector('.section-title [lang="en"]')?.textContent.trim() === englishTitle
    );
    const publicationCount = findResearchSection('Research Achievements')?.querySelectorAll('.repo-list > li').length ?? 0;
    const awardCount = findResearchSection('Awards')?.querySelectorAll('.repo-list > li').length ?? 0;
    const appCount = document.querySelectorAll('#engineer-content .app-card').length;

    [
        { id: 'stat-papers', v: publicationCount },
        { id: 'stat-awards', v: awardCount },
        { id: 'stat-apps', v: appCount }
    ].forEach(s => {
        const el = document.getElementById(s.id);
        if (el) animate(el, s.v);
    });
}

function initResearchPriority() {
    const content = document.getElementById('research-content');
    if (!content) return;

    const sections = Array.from(content.querySelectorAll(':scope > .section-card'));
    const achievements = sections.find(section =>
        section.querySelector('.section-title')?.textContent.includes('Research Achievements')
    );
    const education = sections.find(section =>
        section.querySelector('.section-title')?.textContent.includes('Education')
    );

    if (achievements && education) content.insertBefore(achievements, education);
}

function initTOC() {
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
        a.setAttribute('aria-label', text);
        a.textContent = [...text.replace(/[^\w\s]/g, '').trim() || text][0];
        a.href = `#${s.id}`;
        a.addEventListener('click', (e) => {
            e.preventDefault();
            const h = document.querySelector('.header-bar').offsetHeight;
            window.scrollTo({ top: s.getBoundingClientRect().top + window.scrollY - h - 20, behavior: 'smooth' });
            document.getElementById('toc-menu').classList.remove('show');
            document.getElementById('toc-fab')?.setAttribute('aria-expanded', 'false');
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
    tabs.forEach((tab, index) => {
        const active = index === activeIndex;
        tab.classList.toggle('active', active);
        if (active) tab.setAttribute('aria-current', 'true');
        else tab.removeAttribute('aria-current');
    });
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
        btn.addEventListener('click', async () => {
            const value = btn.getAttribute('data-copy') || '';
            const lang = document.documentElement.getAttribute('data-lang') || 'ja';
            const success = btn.getAttribute(`data-${lang}-success`) || 'Copied!';
            const error = btn.getAttribute('data-error') || 'Error';
            const spans = btn.querySelectorAll('span');
            const originals = Array.from(spans).map(s => s.textContent);

            const fallbackCopy = () => {
                const textarea = document.createElement('textarea');
                textarea.value = value;
                textarea.setAttribute('readonly', '');
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                textarea.setSelectionRange(0, textarea.value.length);
                let copied = false;
                try { copied = document.execCommand('copy'); } catch {}
                textarea.remove();
                return copied;
            };

            let copied = false;
            try {
                if (navigator.clipboard?.writeText) {
                    await navigator.clipboard.writeText(value);
                    copied = true;
                } else {
                    copied = fallbackCopy();
                }
            } catch {
                copied = fallbackCopy();
            }

            spans.forEach(s => s.textContent = copied ? success : error);
            btn.classList.toggle('success', copied);
            setTimeout(() => {
                spans.forEach((s, i) => s.textContent = originals[i]);
                btn.classList.remove('success');
            }, 2000);
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

function initLanguage() {
    const btn = document.getElementById('lang-toggle');
    const set = (l) => {
        document.documentElement.setAttribute('data-lang', l);
        document.documentElement.lang = l;
        safeStorageSet('lang', l);
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
    set(safeStorageGet('lang') || 'ja');
}

function initContactForm() {
    const f = document.getElementById('contact-form');
    if (!f) return;

    const status = document.getElementById('form-status');
    if (status) {
        status.setAttribute('role', 'status');
        status.setAttribute('aria-live', 'polite');
    }

    f.addEventListener('submit', async (e) => {
        e.preventDefault();
        const button = f.querySelector('button[type="submit"]') || f.querySelector('button');
        if (!button) return;

        const lang = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ja';
        const labels = lang === 'en'
            ? { sending: 'Sending…', success: 'Message sent.', error: 'Could not send the message.' }
            : { sending: '送信中…', success: '送信しました。', error: '送信できませんでした。' };
        const originalButtonHTML = button.innerHTML;

        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
        button.textContent = labels.sending;

        const controller = new AbortController();
        const timeoutId = window.setTimeout(() => controller.abort(), 10000);

        if (status) status.textContent = '';

        try {
            const response = await fetch(f.action, {
                method: f.method,
                body: new FormData(f),
                headers: { 'Accept': 'application/json' },
                signal: controller.signal
            });
            if (status) status.textContent = response.ok ? labels.success : labels.error;
            if (response.ok) f.reset();
        } catch {
            if (status) status.textContent = labels.error;
        } finally {
            window.clearTimeout(timeoutId);
            button.disabled = false;
            button.removeAttribute('aria-busy');
            button.innerHTML = originalButtonHTML;
        }
    });
}

async function initQiitaArticles() {
    const c = document.getElementById('qiita-list');
    if (!c) return;

    const showError = () => {
        const lang = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ja';
        c.textContent = lang === 'en'
            ? 'Could not load Qiita articles.'
            : 'Qiita記事を読み込めませんでした。';
    };

    try {
        const r = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent('https://qiita.com/sakai1250/feed')}`);
        if (!r.ok) {
            showError();
            return;
        }

        const d = await r.json();
        if (d.status !== 'ok' || !Array.isArray(d.items)) {
            showError();
            return;
        }

        const articles = [];
        d.items.slice(0, 5).forEach(i => {
            let url;
            try {
                url = new URL(i.link);
            } catch {
                return;
            }
            if (url.protocol !== 'https:' || url.hostname !== 'qiita.com') return;
            articles.push({ url: url.href, title: String(i.title || 'Qiita article') });
        });

        if (!articles.length) {
            showError();
            return;
        }

        c.replaceChildren();
        articles.forEach(article => {
            const l = document.createElement('li');
            const a = document.createElement('a');
            a.href = article.url;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.textContent = article.title;
            l.appendChild(a);
            c.appendChild(l);
        });
    } catch {
        showError();
    }
}
