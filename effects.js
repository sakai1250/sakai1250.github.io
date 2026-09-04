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

    // Keep only the desktop adjustment that is not already represented in static CSS.
    const style = document.createElement('style');
    style.id = 'portfolio-polish-style';
    style.textContent = `
        @media (min-width: 769px) {
            .header-stats {
                transform: translate(-50%, -8px) !important;
            }
        }
    `;
    document.head.appendChild(style);

    // Keep the current call-to-action priority until it is moved into static HTML.
    const cvButton = document.querySelector('.header-actions a[href="assets/cv.pdf"]');
    const githubButton = document.querySelector('.header-actions a[href*="github.com/sakai1250"]');
    cvButton?.classList.add('primary');
    githubButton?.classList.remove('primary');
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
