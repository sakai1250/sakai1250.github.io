#!/usr/bin/env python3
"""Verify the hero network figure: pure geometry (run in Node) and its static page contract."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

GEOMETRY_TEST = r"""
const assert = require('assert');
const h = require('./hero-network.js');

// network shape: fully connected feed-forward layers, laid out left to right
const net = h.createNetwork();
assert.deepStrictEqual(net.layers, [4, 6, 6, 3]);
assert.strictEqual(net.nodes.length, 19);
assert.strictEqual(net.edges.length, 4 * 6 + 6 * 6 + 6 * 3);
for (const n of net.nodes) assert(n.x >= 0 && n.x <= 1 && n.y >= 0 && n.y <= 1, 'node on canvas');
for (let l = 1; l < net.layers.length; l++) {
  const prev = net.nodes.find(n => n.layer === l - 1);
  const next = net.nodes.find(n => n.layer === l);
  assert(next.x > prev.x, 'layers advance left to right');
}
for (const [a, b] of net.edges) assert.strictEqual(net.nodes[b].layer - net.nodes[a].layer, 1, 'edges join adjacent layers');

// waveLevel: a periodic pulse that reaches the layers in order
const P = h.WAVE_PERIOD, D = h.LAYER_DELAY;
for (let layer = 0; layer < net.layers.length; layer++) {
  assert(h.waveLevel(layer, layer * D) > 0.99, 'peak when the wave arrives');
  assert(h.waveLevel(layer, layer * D + P / 2) < 0.1, 'quiet half a period later');
  assert(Math.abs(h.waveLevel(layer, 1.234) - h.waveLevel(layer, 1.234 + P)) < 1e-9, 'periodic');
}
for (let t = 0; t < 30; t += 0.1) {
  for (let layer = 0; layer < net.layers.length; layer += 0.5) {
    const v = h.waveLevel(layer, t);
    assert(v >= 0 && v <= 1, `level in range: ${v}`);
  }
}
assert(h.waveLevel(0, 0.1) > h.waveLevel(3, 0.1), 'input layer fires before the output layer');
assert(h.waveLevel(0.5, 0.5 * D) > 0.99, 'fractional layers address the edges between layers');

// shouldAnimate: only a visible, foreground, motion-allowed figure animates
for (const reduceMotion of [false, true]) {
  for (const hidden of [false, true]) {
    for (const intersecting of [false, true]) {
      const expected = !reduceMotion && !hidden && intersecting;
      assert.strictEqual(h.shouldAnimate({ reduceMotion, hidden, intersecting }), expected);
    }
  }
}
console.log('geometry ok');
"""

MAX_JS_BYTES = 8192
REQUIRED_JS_TOKENS = (
    "prefers-reduced-motion",
    "IntersectionObserver",
    "visibilitychange",
    "devicePixelRatio",
    "requestAnimationFrame",
    "MutationObserver",
    "--hero-ink-rgb",
    "--hero-node-rgb",
)
FORBIDDEN_JS_TOKENS = ("fetch(", "XMLHttpRequest", "WebSocket", "import ")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def problems_in_page(html: str, js: str, css: str) -> list[str]:
    problems: list[str] = []
    hero = re.search(r'<section class="hero"[^>]*>(.*?)</section>', html, re.S)
    if not hero:
        return ["index.html: section.hero is missing"]
    body = hero.group(1)
    if not re.search(r'<canvas id="hero-network" class="hero-canvas" aria-hidden="true"></canvas>', body):
        problems.append("index.html: .hero must contain the aria-hidden canvas#hero-network.hero-canvas")
    # Removed on request: the figure carries no caption, disclosure, or counter.
    for leftover in ("hero-note", "hero-fused", "説明用シミュレーション", "Illustrative simulation", "hero-tracking"):
        if leftover in html:
            problems.append(f"index.html: `{leftover}` must not appear (the figure is a plain network without captions)")
    if not re.search(r'<script src="hero-network\.js\?v=[a-f0-9]+" defer></script>', html):
        problems.append("index.html: hero-network.js must load with a versioned src and defer")

    for token in REQUIRED_JS_TOKENS:
        if token not in js:
            problems.append(f"hero-network.js: missing {token}")
    for token in FORBIDDEN_JS_TOKENS:
        if token in js:
            problems.append(f"hero-network.js: must not use {token!r} (no network, no modules)")
    if len(js.encode("utf-8")) > MAX_JS_BYTES:
        problems.append(f"hero-network.js: larger than {MAX_JS_BYTES} bytes")

    for token in ("--hero-accent-rgb", "--hero-ink-rgb", "--hero-node-rgb"):
        if len(re.findall(rf"{token}\s*:", css)) < (2 if token != "--hero-accent-rgb" else 1):
            problems.append(f"style.css: {token} must be defined" + (" for both themes" if token != "--hero-accent-rgb" else ""))
    if re.search(r"--hero-bg\s*:\s*oklch", css):
        problems.append("style.css: --hero-bg must follow the theme (var(--bg)), not a fixed dark colour")
    if "hero-note" in css or "hero-pulse" in css:
        problems.append("style.css: leftover .hero-note / hero-pulse rules from the removed caption")
    canvas_rule = [body_ for selector, body_ in RULE.findall(css) if ".hero-canvas" in selector]
    if not canvas_rule:
        problems.append("style.css: .hero-canvas is not styled")
    if any("position: fixed" in rule for rule in canvas_rule):
        problems.append("style.css: .hero-canvas must not be position: fixed")
    for selector, rule in RULE.findall(css):
        if ".hero" in selector and "backdrop-filter" in rule:
            problems.append(f"style.css: no backdrop-filter in hero rules (`{selector.strip()}`)")
    return problems


def self_test() -> None:
    good_html = (
        '<link href="x"><script src="hero-network.js?v=abc123def456" defer></script>'
        '<section class="hero" id="top"><canvas id="hero-network" class="hero-canvas" aria-hidden="true"></canvas></section>'
    )
    good_js = ("prefers-reduced-motion IntersectionObserver visibilitychange devicePixelRatio requestAnimationFrame "
               "MutationObserver --hero-ink-rgb --hero-node-rgb")
    good_css = (":root { --hero-accent-rgb: 1, 2, 3; --hero-ink-rgb: 1, 1, 1; --hero-node-rgb: 2, 2, 2; --hero-bg: var(--bg); } "
                '[data-theme="dark"] { --hero-ink-rgb: 9, 9, 9; --hero-node-rgb: 8, 8, 8; } .hero-canvas { position: absolute; }')
    assert problems_in_page(good_html, good_js, good_css) == [], problems_in_page(good_html, good_js, good_css)
    assert any("aria-hidden" in p for p in problems_in_page(good_html.replace(' aria-hidden="true"', ""), good_js, good_css))
    assert any("hero-note" in p for p in problems_in_page(good_html + '<p class="hero-note"></p>', good_js, good_css))
    assert any("説明用シミュレーション" in p for p in problems_in_page(good_html + "説明用シミュレーション", good_js, good_css))
    assert any("hero-note" in p for p in problems_in_page(good_html, good_js, good_css + ".hero-note { }"))
    assert any("IntersectionObserver" in p for p in problems_in_page(good_html, good_js.replace("IntersectionObserver", ""), good_css))
    assert any("fetch(" in p for p in problems_in_page(good_html, good_js + " fetch(", good_css))
    assert any("fixed" in p for p in problems_in_page(good_html, good_js, good_css.replace("absolute", "fixed")))
    assert any("backdrop-filter" in p for p in problems_in_page(good_html, good_js, good_css + ".hero::after { backdrop-filter: blur(4px); }"))
    assert any("defer" in p for p in problems_in_page(good_html.replace(" defer", ""), good_js, good_css))
    assert any("both themes" in p for p in problems_in_page(good_html, good_js, good_css.replace("--hero-ink-rgb: 9, 9, 9;", "")))
    assert any("follow the theme" in p for p in problems_in_page(good_html, good_js, good_css.replace("--hero-bg: var(--bg)", "--hero-bg: oklch(0.1 0 0)")))
    assert any("MutationObserver" in p for p in problems_in_page(good_html, good_js.replace("MutationObserver", ""), good_css))


def check_geometry() -> None:
    result = subprocess.run(["node", "-e", GEOMETRY_TEST], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit("hero-network.js geometry test failed:\n" + (result.stderr or result.stdout).strip())


def main() -> None:
    if not Path("hero-network.js").exists():
        raise SystemExit("hero-network.js is missing")
    self_test()
    check_geometry()
    js = Path("hero-network.js").read_text(encoding="utf-8")
    problems = problems_in_page(
        Path("index.html").read_text(encoding="utf-8"), js, Path("style.css").read_text(encoding="utf-8")
    )
    if problems:
        raise SystemExit("Hero network problems:\n  - " + "\n  - ".join(problems))
    print("OK: hero network geometry, animation policy, and page contract behave as specified")


if __name__ == "__main__":
    main()
