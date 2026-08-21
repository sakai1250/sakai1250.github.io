/**
 * Taigo Sakai Portfolio - Restrained visual details
 */

// Kept as no-ops for compatibility with older cached main.js versions.
function init3DEffects() {}
function initAvatarDragGuide() {}
function initCardDragRotation() {}

function initBackgroundParticles() {
    if (document.getElementById('neural-bg')) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (window.matchMedia('(max-width: 768px)').matches) return;

    const canvas = document.createElement('canvas');
    canvas.id = 'neural-bg';
    canvas.setAttribute('aria-hidden', 'true');
    Object.assign(canvas.style, {
        position: 'fixed',
        inset: '0',
        zIndex: '0',
        pointerEvents: 'none',
        opacity: '0.28',
    });
    document.body.prepend(canvas);

    const context = canvas.getContext('2d');
    if (!context) return;

    const particles = [];
    const particleCount = 18;
    const connectionDistance = 105;
    let animationFrame = 0;

    const themeColor = () => (
        getComputedStyle(document.documentElement).getPropertyValue('--particle-color').trim()
        || 'rgba(138, 97, 30, 0.18)'
    );

    const resize = () => {
        const ratio = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.floor(window.innerWidth * ratio);
        canvas.height = Math.floor(window.innerHeight * ratio);
        canvas.style.width = `${window.innerWidth}px`;
        canvas.style.height = `${window.innerHeight}px`;
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
    };

    class Particle {
        constructor() {
            this.x = Math.random() * window.innerWidth;
            this.y = Math.random() * window.innerHeight;
            this.vx = (Math.random() - 0.5) * 0.10;
            this.vy = (Math.random() - 0.5) * 0.10;
            this.radius = 0.7 + Math.random() * 0.7;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > window.innerWidth) this.vx *= -1;
            if (this.y < 0 || this.y > window.innerHeight) this.vy *= -1;
        }

        draw(color) {
            context.beginPath();
            context.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            context.fillStyle = color;
            context.fill();
        }
    }

    for (let index = 0; index < particleCount; index += 1) {
        particles.push(new Particle());
    }

    const animate = () => {
        context.clearRect(0, 0, window.innerWidth, window.innerHeight);
        const color = themeColor();

        particles.forEach((particle, index) => {
            particle.update();
            particle.draw(color);

            for (let nextIndex = index + 1; nextIndex < particles.length; nextIndex += 1) {
                const next = particles[nextIndex];
                const distance = Math.hypot(particle.x - next.x, particle.y - next.y);
                if (distance >= connectionDistance) continue;

                context.beginPath();
                context.strokeStyle = color;
                context.globalAlpha = (1 - distance / connectionDistance) * 0.24;
                context.lineWidth = 0.45;
                context.moveTo(particle.x, particle.y);
                context.lineTo(next.x, next.y);
                context.stroke();
                context.globalAlpha = 1;
            }
        });

        animationFrame = requestAnimationFrame(animate);
    };

    window.addEventListener('resize', resize, { passive: true });
    window.addEventListener('pagehide', () => cancelAnimationFrame(animationFrame), { once: true });
    resize();
    animate();
}

function initTypingEffect() {
    const textElement = document.getElementById('typing-text');
    const cursor = document.querySelector('.typing-container .cursor');
    if (!textElement) return;

    textElement.textContent = 'Computer Vision · Continual Learning · Multi-View Tracking';
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

        @media (max-width: 768px) {
            .main-content { order: 1 !important; }
            .profile-sidebar { order: 2 !important; }
            .header-actions a[href*="github.com/sakai1250"] { display: none !important; }
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