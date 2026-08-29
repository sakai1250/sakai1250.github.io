/**
 * Taigo Sakai Portfolio - Restrained visual details
 */

// Kept as no-ops for compatibility with older cached main.js versions.
function init3DEffects() {}
function initAvatarDragGuide() {}
function initCardDragRotation() {}
function initBackgroundParticles() {}

function initTypingEffect() {
    const textElement = document.getElementById('typing-text');
    const cursor = document.querySelector('.typing-container .cursor');
    if (!textElement) return;

    textElement.textContent = 'Ph.D. Student · Special Assistant · Computer Vision Researcher';
    if (cursor) cursor.style.display = 'none';
}

function getSectionByEnglishTitle(title) {
    return Array.from(document.querySelectorAll('.section-card')).find(section => {
        const heading = section.querySelector('.section-title [lang="en"]');
        return heading?.textContent.trim() === title;
    });
}

function syncPortfolioStats() {
    const researchSection = getSectionByEnglishTitle('Research Achievements');
    const awardsSection = getSectionByEnglishTitle('Awards');
    const appsSection = getSectionByEnglishTitle('My Apps & Services');

    const values = {
        'stat-papers': researchSection?.querySelectorAll('.repo-list > li').length,
        'stat-awards': awardsSection?.querySelectorAll('.repo-list > li').length,
        'stat-apps': appsSection?.querySelectorAll('.app-card').length,
    };

    Object.entries(values).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && Number.isInteger(value)) element.textContent = String(value);
    });
}

function initPublicationLinkAccessibility() {
    const researchSection = getSectionByEnglishTitle('Research Achievements');
    if (!researchSection) return;

    researchSection.querySelectorAll('.repo-list > li').forEach(item => {
        const link = Array.from(item.querySelectorAll('a')).find(anchor => {
            const label = anchor.textContent.trim();
            return label === '[Paper]' || label === '[Program]';
        });
        if (!link) return;

        const rawText = item.textContent.replace(/\s+/g, ' ').trim();
        const titleMatch = rawText.match(/[“"]\s*([^”"]+?)\s*[,”"]/);
        if (!titleMatch) return;

        const resource = link.textContent.trim().slice(1, -1);
        link.setAttribute('aria-label', `${resource}: ${titleMatch[1].trim()}`);
    });
}

function initAppResourceLinkAccessibility() {
    document.querySelectorAll('.app-card').forEach(card => {
        const title = card.querySelector('.app-title')?.textContent.replace(/\s+/g, ' ').trim();
        if (!title) return;

        card.querySelectorAll('.app-links a').forEach(link => {
            const resource = link.textContent.replace(/\s+/g, ' ').trim();
            if (!resource) return;
            link.setAttribute('aria-label', `${resource}: ${title}`);
        });
    });
}

function initAppCardKeyboardAccess() {
    document.querySelectorAll('.app-card').forEach(card => {
        const trigger = card.querySelector('.app-thumb');
        const title = card.querySelector('.app-title')?.textContent.trim();
        if (!trigger || !title) return;

        trigger.tabIndex = 0;
        trigger.setAttribute('role', 'button');
        trigger.setAttribute('aria-haspopup', 'dialog');
        trigger.setAttribute('aria-controls', 'app-modal');
        trigger.setAttribute('aria-label', `詳細を開く: ${title} / Open details: ${title}`);
        trigger.addEventListener('keydown', event => {
            if (event.key !== 'Enter' && event.key !== ' ') return;
            event.preventDefault();
            card.click();
        });
    });
}

function initModalAccessibility() {
    const modal = document.getElementById('app-modal');
    const container = modal?.querySelector('.modal-container');
    const closeButton = modal?.querySelector('.modal-close');
    if (!modal || !container || !closeButton) return;

    // main.js owns dialog semantics, Escape, and the focus trap. This helper only
    // remembers the actual trigger so focus returns to the keyboard user's entry
    // point after the dialog closes.
    let lastTrigger = null;
    document.querySelectorAll('.app-card').forEach(card => {
        card.addEventListener('click', event => {
            if (event.target.closest('a')) return;
            const activeElement = document.activeElement;
            lastTrigger = activeElement instanceof HTMLElement && card.contains(activeElement)
                ? activeElement
                : card.querySelector('.app-title');
        });
    });

    const sync = () => {
        if (!modal.classList.contains('open') && lastTrigger instanceof HTMLElement) {
            lastTrigger.focus();
            lastTrigger = null;
        }
    };

    const observer = new MutationObserver(sync);
    observer.observe(modal, { attributes: true, attributeFilter: ['class'] });
    window.addEventListener('pagehide', () => observer.disconnect(), { once: true });
}

function initTocAccessibility() {
    const button = document.getElementById('toc-fab');
    const menu = document.getElementById('toc-menu');
    if (!button || !menu) return;

    button.setAttribute('aria-controls', 'toc-menu');
    const sync = () => {
        button.setAttribute('aria-expanded', String(menu.classList.contains('show')));
    };
    sync();

    const observer = new MutationObserver(sync);
    observer.observe(menu, { attributes: true, attributeFilter: ['class'] });
    window.addEventListener('pagehide', () => observer.disconnect(), { once: true });
}

function initPortfolioPolish() {
    if (document.getElementById('portfolio-polish-style')) return;

    const style = document.createElement('style');
    style.id = 'portfolio-polish-style';
    style.textContent = `
        .header-profile::before,
        .header-profile::after,
        .avatar-drag-tooltip {
            display: none !important;
        }

        .app-thumb[role="button"]:focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 2px;
        }

        @media (min-width: 769px) {
            .header-stats {
                transform: translate(-50%, -8px) !important;
            }
        }

        @media (max-width: 768px) {
            .header-actions a[href="assets/cv.pdf"] { display: inline-flex !important; }
            .header-tab-row .year-filter {
                flex-wrap: nowrap !important;
                overflow-x: auto;
                padding-bottom: 4px;
                scrollbar-width: none;
            }
            .header-tab-row .year-filter::-webkit-scrollbar { display: none; }
            .header-tab-row .year-filter .filter-label,
            .header-tab-row .year-filter .chip {
                flex: 0 0 auto;
            }
            .header-tab-row .year-filter .filter-label { width: auto !important; }
            .header-tab-row .year-filter .chip { min-height: 36px; }
        }
    `;
    document.head.appendChild(style);

    const paperStat = document.querySelector('#stat-papers')?.closest('.stat-item');
    const jaStatLabel = paperStat?.querySelector('.stat-label [lang="ja"]');
    const enStatLabel = paperStat?.querySelector('.stat-label [lang="en"]');
    if (jaStatLabel) jaStatLabel.textContent = '研究業績';
    if (enStatLabel) enStatLabel.textContent = 'Research outputs';

    const cvButton = document.querySelector('.header-actions a[href="assets/cv.pdf"]');
    const githubButton = document.querySelector('.header-actions a[href*="github.com/sakai1250"]');
    cvButton?.classList.add('primary');
    githubButton?.classList.remove('primary');

    if (githubButton) {
        const ja = githubButton.querySelector('[lang="ja"]');
        const en = githubButton.querySelector('[lang="en"]');
        if (ja) ja.textContent = 'GitHub';
        if (en) en.textContent = 'GitHub';
    }

    document.querySelectorAll('.tab-item').forEach(tab => {
        const ja = tab.querySelector('[lang="ja"]');
        if (!ja) return;
        if (tab.dataset.tab === 'research') ja.textContent = '研究';
        if (tab.dataset.tab === 'engineer') ja.textContent = '開発';
    });

    initPublicationLinkAccessibility();
    initAppResourceLinkAccessibility();
    initAppCardKeyboardAccess();
    initModalAccessibility();
    initTocAccessibility();
    syncPortfolioStats();
    window.setTimeout(syncPortfolioStats, 1700);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPortfolioPolish, { once: true });
} else {
    initPortfolioPolish();
}

window.init3DEffects = init3DEffects;
window.initBackgroundParticles = initBackgroundParticles;
window.initTypingEffect = initTypingEffect;
window.initAvatarDragGuide = initAvatarDragGuide;
window.initCardDragRotation = initCardDragRotation;