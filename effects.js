/**
 * Taigo Sakai Portfolio - Restrained visual details
 */

function init3DEffects() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const maxTilt = 120;

    document.querySelectorAll('.app-card').forEach(card => {
        card.addEventListener('mousemove', (event) => {
            const rect = card.getBoundingClientRect();
            const xRatio = (event.clientX - rect.left) / rect.width - 0.5;
            const yRatio = (event.clientY - rect.top) / rect.height - 0.5;
            const rotateX = Math.max(-maxTilt, Math.min(maxTilt, yRatio * -12));
            const rotateY = Math.max(-maxTilt, Math.min(maxTilt, xRatio * 12));
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
}

function initCardDragRotation() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.querySelectorAll('.profile-card, .section-card').forEach(card => {
        if (card.dataset.dragRotationReady === 'true') return;
        card.dataset.dragRotationReady = 'true';

        let rotating = false;
        let previousX = 0;
        let previousY = 0;
        let rotateX = 0;
        let rotateY = 0;

        const reset = (event) => {
            if (!rotating) return;
            rotating = false;
            if (event?.pointerId !== undefined) {
                card.releasePointerCapture?.(event.pointerId);
            }
            card.classList.remove('card-rotating');
            card.style.transition = 'transform 0.55s var(--ease-out-expo), box-shadow 0.3s ease';
            card.style.transform = '';
            window.setTimeout(() => {
                if (!card.classList.contains('card-rotating')) {
                    card.style.transition = '';
                }
            }, 560);
        };

        card.addEventListener('pointerdown', (event) => {
            if (event.button !== 0 || event.pointerType === 'touch') return;
            if (event.target.closest('a, button, input, textarea, select, .repo-list li, .app-card')) return;

            rotating = true;
            previousX = event.clientX;
            previousY = event.clientY;
            rotateX = 0;
            rotateY = 0;
            card.classList.add('card-rotating');
            card.style.transition = 'none';
            card.setPointerCapture?.(event.pointerId);
        });

        card.addEventListener('pointermove', (event) => {
            if (!rotating) return;
            const deltaX = event.clientX - previousX;
            const deltaY = event.clientY - previousY;
            if (Math.hypot(deltaX, deltaY) < 4) return;

            event.preventDefault();
            previousX = event.clientX;
            previousY = event.clientY;
            rotateX += deltaY * -0.9;
            rotateY += deltaX * 0.9;
            const lift = Math.min(12, 5 + Math.hypot(deltaX, deltaY) / 12);
            card.style.transform = `perspective(850px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(${-lift}px) scale(1.015)`;
        });

        card.addEventListener('pointerup', reset);
        card.addEventListener('pointercancel', reset);
        card.addEventListener('lostpointercapture', reset);
        window.addEventListener('blur', () => reset());
    });
}

function initAvatarDragGuide() {
    const avatar = document.querySelector('.header-avatar');
    if (!avatar || avatar.dataset.dragGuideReady === 'true') return;
    avatar.dataset.dragGuideReady = 'true';

    const tooltip = document.createElement('div');
    tooltip.className = 'avatar-drag-tooltip';
    tooltip.setAttribute('role', 'status');
    tooltip.setAttribute('aria-live', 'polite');
    document.body.appendChild(tooltip);

    let dragging = false;
    let startX = 0;
    let startY = 0;

    const getGuideText = (clientX, clientY) => {
        avatar.style.visibility = 'hidden';
        const target = document.elementFromPoint(clientX, clientY);
        avatar.style.visibility = '';

        const lang = document.documentElement.getAttribute('data-lang') || 'ja';
        if (!target) return lang === 'ja' ? 'ページ外' : 'Outside the page';

        const appCard = target.closest('.app-card');
        if (appCard) {
            const title = appCard.querySelector('.app-title')?.textContent.trim() || '';
            return `${lang === 'ja' ? '開発作品' : 'Project'} · ${title}`;
        }

        const section = target.closest('.section-card');
        if (section) {
            const title = section.querySelector('.section-title');
            const localizedTitle = title?.querySelector(`[lang="${lang}"]`) || title;
            return `${lang === 'ja' ? 'セクション' : 'Section'} · ${localizedTitle?.textContent.trim() || ''}`;
        }

        if (target.closest('.profile-sidebar')) {
            return lang === 'ja' ? 'プロフィール・連絡先' : 'Profile and contact links';
        }
        if (target.closest('.section-tab-nav')) {
            return lang === 'ja' ? 'セクションナビゲーション' : 'Section navigation';
        }
        if (target.closest('.header-bar')) {
            return lang === 'ja' ? 'プロフィールと表示設定' : 'Profile and display controls';
        }
        if (target.closest('.main-content')) {
            return lang === 'ja' ? '研究・開発コンテンツ' : 'Research and engineering content';
        }
        return lang === 'ja' ? 'ページ背景' : 'Page background';
    };

    const updateTooltip = (clientX, clientY) => {
        tooltip.textContent = getGuideText(clientX, clientY);
        tooltip.style.left = `${clientX}px`;
        tooltip.style.top = `${Math.max(18, clientY - 20)}px`;
        tooltip.classList.add('visible');
    };

    const endDrag = (event) => {
        if (!dragging) return;
        dragging = false;
        avatar.releasePointerCapture?.(event.pointerId);
        avatar.classList.remove('avatar-dragging');
        avatar.style.transform = '';
        tooltip.classList.remove('visible');
    };

    avatar.addEventListener('pointerdown', (event) => {
        if (event.button !== 0) return;
        event.preventDefault();
        dragging = true;
        startX = event.clientX;
        startY = event.clientY;
        avatar.classList.add('avatar-dragging');
        avatar.setPointerCapture?.(event.pointerId);
        updateTooltip(event.clientX, event.clientY);
    });

    avatar.addEventListener('pointermove', (event) => {
        if (!dragging) return;
        event.preventDefault();
        const offsetX = event.clientX - startX;
        const offsetY = event.clientY - startY;
        avatar.style.transform = `translate3d(${offsetX}px, ${offsetY}px, 0) scale(1.06)`;
        updateTooltip(event.clientX, event.clientY);
    });

    avatar.addEventListener('pointerup', endDrag);
    avatar.addEventListener('pointercancel', endDrag);
    window.addEventListener('blur', () => {
        if (!dragging) return;
        dragging = false;
        avatar.classList.remove('avatar-dragging');
        avatar.style.transform = '';
        tooltip.classList.remove('visible');
    });
}

function initBackgroundParticles() {
    if (document.getElementById('neural-bg')) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const canvas = document.createElement('canvas');
    canvas.id = 'neural-bg';
    canvas.setAttribute('aria-hidden', 'true');
    Object.assign(canvas.style, {
        position: 'fixed',
        inset: '0',
        zIndex: '0',
        pointerEvents: 'none',
        opacity: '0.42',
    });
    document.body.prepend(canvas);

    const context = canvas.getContext('2d');
    if (!context) return;

    const particles = [];
    const particleCount = 22;
    const connectionDistance = 105;
    let animationFrame = 0;

    const themeColor = () => (
        getComputedStyle(document.documentElement).getPropertyValue('--particle-color').trim()
        || 'rgba(184, 138, 68, 0.24)'
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
            this.vx = (Math.random() - 0.5) * 0.12;
            this.vy = (Math.random() - 0.5) * 0.12;
            this.radius = 0.7 + Math.random() * 0.8;
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
                context.globalAlpha = (1 - distance / connectionDistance) * 0.34;
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
    if (!textElement) return;

    const phrases = [
        'Deep Learning Researcher',
        'iOS & Web Developer',
        'Ph.D. Student at Meijo University',
        'Building Intelligent Systems',
    ];

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        textElement.textContent = phrases[0];
        return;
    }

    let phraseIndex = 0;
    let characterIndex = 0;
    let deleting = false;

    const type = () => {
        const phrase = phrases[phraseIndex];
        characterIndex += deleting ? -1 : 1;
        textElement.textContent = phrase.substring(0, characterIndex);

        let delay = deleting ? 42 : 78;
        if (!deleting && characterIndex === phrase.length) {
            deleting = true;
            delay = 2100;
        } else if (deleting && characterIndex === 0) {
            deleting = false;
            phraseIndex = (phraseIndex + 1) % phrases.length;
            delay = 520;
        }
        window.setTimeout(type, delay);
    };

    type();
}

window.init3DEffects = init3DEffects;
window.initBackgroundParticles = initBackgroundParticles;
window.initTypingEffect = initTypingEffect;
window.initAvatarDragGuide = initAvatarDragGuide;
window.initCardDragRotation = initCardDragRotation;
