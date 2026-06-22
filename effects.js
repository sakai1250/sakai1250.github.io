/**
 * Taigo Sakai Portfolio - Visual Effects & Advanced Interactions
 */

// === 3D Tilt & Parallax ===
function init3DEffects() {
    // 3D Tilt for App Cards
    const cards = document.querySelectorAll('.app-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left, y = e.clientY - rect.top;
            const centerX = rect.width / 2, centerY = rect.height / 2;
            const rotateX = (y - centerY) / 20, rotateY = (centerX - x) / 20;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)`;
        });
    });

    // Parallax Header
    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY;
        const header = document.querySelector('.header-bar');
        if (header) header.style.backgroundPositionY = `${scrolled * 0.5}px`;
    }, { passive: true });
}

// === Neural Background Particles ===
function initBackgroundParticles() {
    if (document.getElementById('neural-bg')) return;
    const canvas = document.createElement('canvas');
    canvas.id = 'neural-bg';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.zIndex = '-1';
    canvas.style.pointerEvents = 'none';
    canvas.style.opacity = '0.3';
    document.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let particles = [];

    function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 2;
        }
        update() {
            this.x += this.vx; this.y += this.vy;
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#2f81f7';
            ctx.fill();
        }
    }

    for (let i = 0; i < 60; i++) particles.push(new Particle());

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach((p, i) => {
            p.update(); p.draw();
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j], dx = p.x - p2.x, dy = p.y - p2.y, dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#2f81f7';
                    ctx.globalAlpha = 1 - (dist / 150);
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                    ctx.globalAlpha = 1;
                }
            }
        });
        requestAnimationFrame(animate);
    }
    animate();
}

// === Typing Effect ===
function initTypingEffect() {
    const textEl = document.getElementById('typing-text');
    if (!textEl) return;
    const phrases = ["Deep Learning Researcher", "iOS & Web Developer", "Ph.D. Student at Meijo University", "Building Intelligent Systems"];
    let phraseIndex = 0, charIndex = 0, isDeleting = false, typeSpeed = 100;

    const type = () => {
        const current = phrases[phraseIndex];
        charIndex += isDeleting ? -1 : 1;
        textEl.textContent = current.substring(0, charIndex);
        typeSpeed = isDeleting ? 50 : 100;

        if (!isDeleting && charIndex === current.length) {
            isDeleting = true;
            typeSpeed = 2000;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            phraseIndex = (phraseIndex + 1) % phrases.length;
            typeSpeed = 500;
        }
        setTimeout(type, typeSpeed);
    };
    type();
}

// === Drag & Drop Interactions ===
function initDraggableInteractions() {
    initPlayfulCardDrag();

    // Draggable Avatar Tooltip
    const avatar = document.querySelector('.header-profile img');
    if (avatar) {
        avatar.style.cursor = 'grab';
        let isDragging = false, startX, startY, tooltip = null;

        const updateTooltip = (x, y) => {
            if (!tooltip) { tooltip = document.createElement('div'); tooltip.className = 'drag-tooltip'; document.body.appendChild(tooltip); }
            avatar.style.display = 'none';
            const elBelow = document.elementFromPoint(x, y);
            avatar.style.display = 'block';

            const lang = document.documentElement.getAttribute('data-lang') || 'ja';
            let text = lang === 'ja' ? '未知の領域' : 'Unknown Area';

            if (elBelow) {
                const app = elBelow.closest('.app-card');
                const section = elBelow.closest('.section-card');
                const header = elBelow.closest('.header-bar');
                const sidebar = elBelow.closest('.profile-sidebar');

                if (app) {
                    const title = app.querySelector('.app-title')?.textContent || '';
                    text = (lang === 'ja' ? '開発：' : 'Dev: ') + title;
                } else if (section) {
                    const titleEl = section.querySelector('.section-title');
                    const titleText = (titleEl?.querySelector(`[lang="${lang}"]`) || titleEl)?.textContent.trim() || '';
                    text = (lang === 'ja' ? '研究：' : 'Res: ') + titleText;
                } else if (header) {
                    text = lang === 'ja' ? 'ナビゲーション' : 'Navigation';
                } else if (sidebar) {
                    text = lang === 'ja' ? '自己紹介' : 'Biography';
                } else {
                    text = lang === 'ja' ? '背景' : 'Background';
                }
            }
            tooltip.textContent = text;
            tooltip.style.left = `${x}px`;
            tooltip.style.top = `${y - 40}px`;
            tooltip.classList.add('visible');
        };

        const onStart = (e) => {
            e.preventDefault(); isDragging = true;
            avatar.style.cursor = 'grabbing';
            startX = e.pageX || e.touches[0].pageX;
            startY = e.pageY || e.touches[0].pageY;
        };

        const onMove = (e) => {
            if (!isDragging) return;
            const pageX = e.pageX || e.touches[0].pageX, pageY = e.pageY || e.touches[0].pageY;
            avatar.style.transform = `translate(${pageX - startX}px, ${pageY - startY}px) scale(1.1)`;
            updateTooltip(e.clientX || e.touches[0].clientX, e.clientY || e.touches[0].clientY);
        };

        const onEnd = () => {
            isDragging = false; avatar.style.cursor = 'grab';
            avatar.style.transition = 'transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            avatar.style.transform = 'translate(0, 0) scale(1)';
            if (tooltip) tooltip.classList.remove('visible');
        };

        avatar.addEventListener('mousedown', onStart);
        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onEnd);
    }
}

function initPlayfulCardDrag() {
    const dragSelector = '.profile-card, .section-card, .app-card, .repo-list li';
    const edgeOnlySelector = '.repo-list li, .app-card';

    document.querySelectorAll(dragSelector).forEach((card) => {
        if (card.dataset.playDragReady === 'true') return;
        card.dataset.playDragReady = 'true';
        card.classList.add('playful-draggable');

        let startX = 0, startY = 0, pointerActive = false, didReorder = false, suppressClick = false;
        let activeConfig = null, placeholder = null, grabOffsetX = 0, grabOffsetY = 0;

        const endDrag = (e = {}) => {
            if (!pointerActive) return;
            pointerActive = false;
            card.releasePointerCapture?.(e.pointerId);
            window.removeEventListener('pointerup', endDrag);
            window.removeEventListener('pointercancel', endDrag);
            window.removeEventListener('blur', endDrag);
            if (placeholder) {
                placeholder.parentElement?.insertBefore(card, placeholder);
                placeholder.remove();
                placeholder = null;
            }
            clearPlayfulDragState(card);
            activeConfig = null;

            if (didReorder) {
                suppressClick = true;
                setTimeout(() => { suppressClick = false; }, 0);
                if (typeof updateSectionTabs === 'function') updateSectionTabs();
                if (typeof updateTOC === 'function') updateTOC();
            }
        };

        card.addEventListener('pointerdown', (e) => {
            if (e.button === 2) {
                clearPlayfulDragState(card);
                return;
            }
            if (e.button !== 0 || e.target.closest('button, input, textarea, select, .section-tab-item, .chip')) return;
            if (card.matches('.section-card') && e.target.closest('.repo-list li, .app-card')) return;
            if (card.matches(edgeOnlySelector) && !isInItemDragHandle(card, e.clientX)) return;
            activeConfig = getReorderConfig(card);
            pointerActive = true;
            didReorder = false;
            startX = e.clientX;
            startY = e.clientY;
            const rect = card.getBoundingClientRect();
            grabOffsetX = e.clientX - rect.left;
            grabOffsetY = e.clientY - rect.top;
            card.classList.add('playful-grabbed');
            card.style.transition = 'none';
            card.setPointerCapture?.(e.pointerId);
            window.addEventListener('pointerup', endDrag);
            window.addEventListener('pointercancel', endDrag);
            window.addEventListener('blur', endDrag);
        });

        card.addEventListener('pointermove', (e) => {
            if (!pointerActive) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            const isItem = card.matches(edgeOnlySelector);
            const config = activeConfig;

            if (!isItem) {
                const rect = card.getBoundingClientRect();
                const pointerX = (e.clientX - rect.left) / rect.width - 0.5;
                const pointerY = (e.clientY - rect.top) / rect.height - 0.5;
                const dragBoostX = Math.max(-1, Math.min(1, dx / 160));
                const dragBoostY = Math.max(-1, Math.min(1, dy / 160));
                const rotateX = Math.max(-190, Math.min(190, (-pointerY * 90) - (dragBoostY * 160)));
                const rotateY = Math.max(-190, Math.min(190, (pointerX * 90) + (dragBoostX * 160)));
                const lift = Math.min(18, Math.hypot(dx, dy) / 8);
                card.style.transform = `perspective(620px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(${-lift}px) scale(1.035)`;
            }

            if (Math.hypot(dx, dy) < 8) return;
            if (!config) return;

            e.preventDefault();
            didReorder = true;
            card.classList.add('playful-dragging');
            config.container.classList.add('playful-drop-target');
            if (!placeholder) {
                const rect = card.getBoundingClientRect();
                placeholder = createDragPlaceholder(card, rect);
                card.parentElement.insertBefore(placeholder, card);
                setFixedDragPosition(card, rect, e.clientX, e.clientY, grabOffsetX, grabOffsetY);
                document.body.appendChild(card);
            }

            updateFixedDragPosition(card, e.clientX, e.clientY, grabOffsetX, grabOffsetY);

            const afterElement = getDragAfterElement(config.container, config.item, e.clientY, e.clientX, placeholder);
            if (!afterElement) {
                config.container.appendChild(placeholder);
            } else if (afterElement !== placeholder.nextElementSibling) {
                config.container.insertBefore(placeholder, afterElement);
            }
            markSortNeighbors(config.container, placeholder);
        });

        card.addEventListener('pointerup', endDrag);
        card.addEventListener('pointercancel', endDrag);
        card.addEventListener('contextmenu', () => {
            if (placeholder) {
                placeholder.parentElement?.insertBefore(card, placeholder);
                placeholder.remove();
                placeholder = null;
            }
            clearPlayfulDragState(card);
            activeConfig = null;
            pointerActive = false;
            window.removeEventListener('pointerup', endDrag);
            window.removeEventListener('pointercancel', endDrag);
            window.removeEventListener('blur', endDrag);
        });
        card.addEventListener('click', (e) => {
            if (!suppressClick) return;
            e.preventDefault();
            e.stopPropagation();
            suppressClick = false;
        });
    });

    if (document.body.dataset.playDragObserver !== 'true') {
        document.body.dataset.playDragObserver = 'true';
        let observerTicking = false;
        new MutationObserver(() => {
            if (observerTicking) return;
            observerTicking = true;
            requestAnimationFrame(() => {
                initPlayfulCardDrag();
                observerTicking = false;
            });
        }).observe(document.body, { childList: true, subtree: true });
    }
}

function isInItemDragHandle(card, clientX) {
    const rect = card.getBoundingClientRect();
    if (card.matches('.repo-list li') && card.querySelector(':scope > .link-arrow')) {
        return clientX >= rect.right - 92 && clientX <= rect.right - 38;
    }
    return clientX >= rect.right - 56;
}

function clearPlayfulDragState(card) {
    card.classList.remove('playful-grabbed', 'playful-dragging', 'playful-floating-list-item');
    card.style.transition = 'transform 0.45s var(--ease-out-expo)';
    card.style.transform = '';
    card.style.position = '';
    card.style.left = '';
    card.style.top = '';
    card.style.width = '';
    card.style.height = '';
    card.style.margin = '';
    card.style.pointerEvents = '';
    card.style.zIndex = '';
    document.querySelectorAll('.playful-drop-target').forEach(el => el.classList.remove('playful-drop-target'));
    document.querySelectorAll('.playful-sort-before, .playful-sort-after').forEach(el => {
        el.classList.remove('playful-sort-before', 'playful-sort-after');
    });
}

function createDragPlaceholder(card, rect) {
    const placeholder = document.createElement(card.tagName.toLowerCase());
    placeholder.className = card.className;
    placeholder.classList.remove('playful-grabbed', 'playful-dragging');
    placeholder.classList.add('playful-placeholder-source');
    placeholder.style.width = `${rect.width}px`;
    placeholder.style.height = `${rect.height}px`;
    placeholder.style.margin = getComputedStyle(card).margin;
    placeholder.setAttribute('aria-hidden', 'true');
    return placeholder;
}

function setFixedDragPosition(card, rect, clientX, clientY, offsetX, offsetY) {
    if (card.matches('li')) {
        card.classList.add('playful-floating-list-item');
    }
    card.style.position = 'fixed';
    card.style.width = `${rect.width}px`;
    card.style.height = `${rect.height}px`;
    card.style.margin = '0';
    card.style.pointerEvents = 'none';
    card.style.zIndex = '2400';
    card.style.transform = 'none';
    updateFixedDragPosition(card, clientX, clientY, offsetX, offsetY);
}

function updateFixedDragPosition(card, clientX, clientY, offsetX, offsetY) {
    card.style.left = `${clientX - offsetX}px`;
    card.style.top = `${clientY - offsetY}px`;
}

function markSortNeighbors(container, dragging) {
    container.querySelectorAll('.playful-sort-before, .playful-sort-after').forEach(el => {
        el.classList.remove('playful-sort-before', 'playful-sort-after');
    });
    const prev = getSortableSibling(dragging, 'previousElementSibling');
    const next = getSortableSibling(dragging, 'nextElementSibling');
    if (prev) prev.classList.add('playful-sort-before');
    if (next) next.classList.add('playful-sort-after');
}

function getSortableSibling(element, direction) {
    let sibling = element[direction];
    while (sibling && (
        sibling.classList.contains('playful-dragging')
        || sibling.classList.contains('playful-placeholder-source')
    )) {
        sibling = sibling[direction];
    }
    return sibling;
}

function getReorderConfig(card) {
    if (card.matches('.section-card') && card.parentElement?.matches('.tab-content')) {
        return { container: card.parentElement, item: '.section-card' };
    }
    if (card.matches('li') && card.parentElement?.matches('.repo-list')) {
        return { container: card.parentElement, item: 'li' };
    }
    if (card.matches('.app-card') && card.parentElement?.matches('.grid-dense')) {
        return { container: card.parentElement, item: '.app-card' };
    }
    return null;
}

function getDragAfterElement(container, selector, y, x, dragging) {
    const items = [...container.querySelectorAll(selector)].filter(item => {
        return item !== dragging
            && !item.classList.contains('playful-dragging')
            && !item.classList.contains('playful-placeholder-source');
    });
    const isGrid = getComputedStyle(container).display === 'grid';

    return items.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = isGrid
            ? Math.hypot(x - (box.left + box.width / 2), y - (box.top + box.height / 2))
            : y - box.top - box.height / 2;

        if (isGrid) {
            return offset < closest.offset ? { offset, element: child } : closest;
        }
        return offset < 0 && offset > closest.offset ? { offset, element: child } : closest;
    }, { offset: isGrid ? Number.POSITIVE_INFINITY : Number.NEGATIVE_INFINITY }).element;
}

// 互換性のためにwindowに公開
window.init3DEffects = init3DEffects;
window.initBackgroundParticles = initBackgroundParticles;
window.initTypingEffect = initTypingEffect;
window.initDraggableInteractions = initDraggableInteractions;
