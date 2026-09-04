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
