/**
 * Taigo Sakai Portfolio - Restrained visual details
 */

function init3DEffects() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.querySelectorAll('.app-card').forEach(card => {
        card.addEventListener('mousemove', (event) => {
            const rect = card.getBoundingClientRect();
            const xRatio = (event.clientX - rect.left) / rect.width - 0.5;
            const yRatio = (event.clientY - rect.top) / rect.height - 0.5;
            const rotateX = Math.max(-1.5, Math.min(1.5, yRatio * -3));
            const rotateY = Math.max(-1.5, Math.min(1.5, xRatio * 3));
            card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
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
