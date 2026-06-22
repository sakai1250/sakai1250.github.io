import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const [html, css, main, effects] = await Promise.all([
  readFile(new URL('../index.html', import.meta.url), 'utf8'),
  readFile(new URL('../style.css', import.meta.url), 'utf8'),
  readFile(new URL('../main.js', import.meta.url), 'utf8'),
  readFile(new URL('../effects.js', import.meta.url), 'utf8'),
]);

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

test('keeps the existing interaction hooks', () => {
  for (const hook of [
    'id="lang-toggle"',
    'id="theme-toggle"',
    'data-tab="research"',
    'data-tab="engineer"',
    'id="section-tab-nav"',
    'id="app-modal"',
  ]) {
    assert.match(html, new RegExp(escapeRegExp(hook)));
  }
});

test('defines ivory editorial tokens and removes neon token usage', () => {
  for (const value of ['#F7F3EA', '#FAF8F3', '#071A2F', '#B88A44', '#C6A15B']) {
    assert.match(css.toUpperCase(), new RegExp(escapeRegExp(value)));
  }
  assert.doesNotMatch(css, /--neon-glow|--grad-sunset|--grad-neon|#00e5ff/i);
});

test('removes card reordering but keeps the avatar drag guide', () => {
  assert.match(main, /initAvatarDragGuide/);
  assert.match(effects, /function initAvatarDragGuide/);
  assert.match(effects, /window\.initAvatarDragGuide = initAvatarDragGuide/);
  assert.doesNotMatch(effects, /initPlayfulCardDrag|playful-draggable|playful-placeholder/);
  assert.doesNotMatch(css, /\.playful-/);
  assert.match(css, /\.header-avatar[\s\S]*cursor:\s*grab/i);
});

test('keeps a visible but restrained application card tilt', () => {
  assert.match(effects, /const maxTilt = 4/);
  assert.match(effects, /translateY\(-4px\)/);
});

test('uses editorial fonts instead of cyber display fonts', () => {
  assert.match(html, /Cormorant\+Garamond/);
  assert.doesNotMatch(html, /Orbitron|Chakra\+Petch/);
});

test('keeps OS theme detection and uses editorial browser colors', () => {
  assert.match(html, /prefers-color-scheme:\s*light/);
  assert.match(main, /#09131F/i);
  assert.match(main, /#F7F3EA/i);
});
