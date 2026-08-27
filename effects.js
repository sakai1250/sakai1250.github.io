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

function initModalAccessibility() {
    const modal = document.getElementById('app-modal');
    const container = modal?.querySelector('.modal-container');
    const closeButton = modal?.querySelector('.modal-close');
    if (!modal || !container || !closeButton) return;

    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'modal-title');
    modal.setAttribute('aria-hidden', modal.classList.contains('open') ? 'false' : 'true');

    let lastTrigger = null;
    document.querySelectorAll('.app-card').forEach(card => {
        card.addEventListener('click', event => {
            if (event.target.closest('a')) return;
            lastTrigger = card.querySelector('.app-title');
        });
    });

    const sync = () => {
        const open = modal.classList.contains('open');
        modal.setAttribute('aria-hidden', String(!open));
        if (open) {
            closeButton.focus();
        } else if (lastTrigger instanceof HTMLElement) {
            lastTrigger.focus();
            lastTrigger = null;
        }
    };

    const observer = new MutationObserver(sync);
    observer.observe(modal, { attributes: true, attributeFilter: ['class'] });

    modal.addEventListener('keydown', event => {
        if (event.key === 'Escape' && modal.classList.contains('open')) {
            event.preventDefault();
            closeButton.click();
            return;
        }
        if (event.key !== 'Tab' || !modal.classList.contains('open')) return;

        const focusable = Array.from(modal.querySelectorAll(
            'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )).filter(element => element.offsetParent !== null);
        if (focusable.length < 2) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    });

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

    initModalAccessibility();
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