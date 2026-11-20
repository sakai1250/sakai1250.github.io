'use strict';

// Hero figure: a plain feed-forward neural network with a slow forward-pass pulse.
// Decorative only: the canvas is aria-hidden and carries no claims.

const TAU = Math.PI * 2;
const LAYERS = [4, 6, 6, 3];
const WAVE_PERIOD = 4.2;
const LAYER_DELAY = 0.6;
const WAVE_WIDTH = 0.35;
const STATIC_TIME = 0.9;

// Fully connected layers on the unit square, advancing left to right.
function createNetwork() {
    const nodes = [];
    const widest = Math.max(...LAYERS);
    LAYERS.forEach((count, layer) => {
        for (let i = 0; i < count; i++) {
            nodes.push({
                layer,
                x: 0.5 + 0.47 * (layer / (LAYERS.length - 1)),
                y: 0.5 + (i - (count - 1) / 2) * (0.7 / (widest - 1))
            });
        }
    });
    const edges = [];
    nodes.forEach((from, a) => {
        nodes.forEach((to, b) => { if (to.layer === from.layer + 1) edges.push([a, b]); });
    });
    return { layers: LAYERS.slice(), nodes, edges };
}

// 0..1 pulse that reaches layer `layer` (fractional = between layers) once per period.
function waveLevel(layer, t) {
    let phase = (((t % WAVE_PERIOD) + WAVE_PERIOD) % WAVE_PERIOD) - layer * LAYER_DELAY;
    phase = ((((phase + WAVE_PERIOD / 2) % WAVE_PERIOD) + WAVE_PERIOD) % WAVE_PERIOD) - WAVE_PERIOD / 2;
    return Math.exp(-(phase * phase) / (2 * WAVE_WIDTH * WAVE_WIDTH));
}

// Only a visible, foreground figure whose viewer allows motion should animate.
function shouldAnimate(state) {
    return !state.reduceMotion && !state.hidden && state.intersecting;
}

function startHeroNetwork() {
    const canvas = document.getElementById('hero-network');
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext('2d');
    const net = createNetwork();
    const reduceQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    let accent = '', ink = '', nodeFill = '';
    function readColors() {
        const style = getComputedStyle(canvas);
        accent = style.getPropertyValue('--hero-accent-rgb').trim() || '238, 75, 36';
        ink = style.getPropertyValue('--hero-ink-rgb').trim() || '255, 255, 255';
        nodeFill = style.getPropertyValue('--hero-node-rgb').trim() || '14, 14, 18';
    }
    readColors();
    const state = { reduceMotion: reduceQuery.matches, hidden: document.hidden, intersecting: true };
    const gaps = net.layers.slice(1).map((_, gap) => net.edges.filter(([a]) => net.nodes[a].layer === gap));
    let width = 0, height = 0, rafId = 0;

    function resize() {
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = canvas.clientWidth;
        height = canvas.clientHeight;
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function strokeEdges(edges, style) {
        ctx.strokeStyle = style;
        ctx.beginPath();
        edges.forEach(([a, b]) => {
            ctx.moveTo(net.nodes[a].x * width, net.nodes[a].y * height);
            ctx.lineTo(net.nodes[b].x * width, net.nodes[b].y * height);
        });
        ctx.stroke();
    }

    function draw(t) {
        ctx.clearRect(0, 0, width, height);
        ctx.lineWidth = 1;
        strokeEdges(net.edges, `rgba(${ink},.12)`);
        gaps.forEach((edges, gap) => strokeEdges(edges, `rgba(${accent},${waveLevel(gap + 0.5, t) * 0.5})`));
        net.nodes.forEach(node => {
            const level = waveLevel(node.layer, t);
            const x = node.x * width, y = node.y * height, r = 4 + level * 1.6;
            ctx.beginPath();
            ctx.arc(x, y, r, 0, TAU);
            ctx.fillStyle = `rgba(${nodeFill},.92)`;
            ctx.fill();
            ctx.strokeStyle = `rgba(${ink},${0.32 + level * 0.3})`;
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(x, y, r - 1.2, 0, TAU);
            ctx.fillStyle = level > 0.05 ? `rgba(${accent},${0.25 + level * 0.75})` : `rgba(${ink},.5)`;
            ctx.fill();
        });
    }

    function loop(ts) {
        draw(ts / 1000);
        rafId = requestAnimationFrame(loop);
    }

    function sync() {
        const run = shouldAnimate(state);
        if (run && !rafId) rafId = requestAnimationFrame(loop);
        if (!run && rafId) { cancelAnimationFrame(rafId); rafId = 0; }
    }

    resize();
    draw(STATIC_TIME);
    if (window.IntersectionObserver) {
        new IntersectionObserver(entries => {
            state.intersecting = entries[entries.length - 1].isIntersecting;
            sync();
        }).observe(canvas);
    }
    // Redraw with the new palette when the theme switches (the loop picks it up while animating).
    new MutationObserver(() => { readColors(); if (!rafId) draw(STATIC_TIME); })
        .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    document.addEventListener('visibilitychange', () => { state.hidden = document.hidden; sync(); });
    reduceQuery.addEventListener('change', () => { state.reduceMotion = reduceQuery.matches; sync(); });
    if (window.ResizeObserver) {
        new ResizeObserver(() => { resize(); if (!rafId) draw(STATIC_TIME); }).observe(canvas);
    }
    sync();
}

if (typeof document !== 'undefined') {
    if (document.readyState === 'complete') startHeroNetwork();
    else window.addEventListener('load', startHeroNetwork);
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { createNetwork, waveLevel, shouldAnimate, WAVE_PERIOD, LAYER_DELAY };
}
