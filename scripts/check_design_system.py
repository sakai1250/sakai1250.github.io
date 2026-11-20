#!/usr/bin/env python3
"""Keep the portfolio on its ruled Index design: no legacy fonts, gold, pills, or soft shadows."""

from __future__ import annotations

import re
from pathlib import Path

INDEX = Path("index.html")
STYLE = Path("style.css")
MAIN = Path("main.js")

REQUIRED_FONT_FAMILIES = ("family=Geist:", "family=Geist+Mono:", "Noto+Sans+JP")
FORBIDDEN_FONTS_HTML = ("Cormorant", "DM+Sans")
FORBIDDEN_FONTS_CSS = ("Cormorant", "DM Sans")
FORBIDDEN_GOLD = ("#C6A15B", "#8A611E", "#EEE2CA", "--accent-2", "--accent-soft")
FORBIDDEN_CSS_STRINGS = (
    ".reveal-item",
    ".reveal-active",
    "#loading-screen",
    ".spinner",
    "quietPulse",
    ".cursor {",
    "@keyframes blink",
)
LAYER_ORDER = "@layer reset, tokens, base, layout, components;"
SCROLL_SUPPORTS = "@supports (animation-timeline: scroll())"
HIDE_EN = '[lang="en"] { display: none !important; }'
KEEP_HTML_VISIBLE = "html[lang] { display: block !important; }"
PILL_RADIUS = re.compile(r"border-radius\s*:\s*(?:999|9999|50|100)px")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")


def problems_in_index(html: str) -> list[str]:
    problems: list[str] = []
    link = re.search(r'<link\s+href="(https://fonts\.googleapis\.com/css2\?[^"]+)"', html)
    if not link:
        return ["index.html: Google Fonts stylesheet link is missing"]
    href = link.group(1)
    for needle in REQUIRED_FONT_FAMILIES:
        if needle not in href:
            problems.append(f"index.html: font link is missing {needle}")
    for needle in FORBIDDEN_FONTS_HTML:
        if needle in href:
            problems.append(f"index.html: legacy font {needle} is still loaded")
    # Focus order must follow the visual order: brand, tabs + filters, then actions.
    positions = [html.find(f'class="{name}"') for name in ("header-brand", "header-tab-row", "header-actions")]
    if -1 in positions or positions != sorted(positions):
        problems.append("index.html: header DOM order must be brand, tab row, actions (it sets keyboard focus order)")
    return problems


def _split_top_level(value: str, separator: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    current = ""
    for char in value:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == separator and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    parts.append(current)
    return [part.strip() for part in parts if part.strip()]


def _blur_of(shadow: str) -> float:
    lengths = [
        token for token in _split_top_level(shadow, " ")
        if re.fullmatch(r"-?[\d.]+(?:px|rem|em)?", token)
    ]
    if len(lengths) < 3:
        return 0.0
    return float(re.match(r"-?[\d.]+", lengths[2]).group(0))  # type: ignore[union-attr]


def problems_in_css(css: str) -> list[str]:
    problems: list[str] = []
    for needle in FORBIDDEN_FONTS_CSS:
        if needle in css:
            problems.append(f"style.css: legacy font {needle} is still referenced")
    lowered = css.lower()
    for needle in FORBIDDEN_GOLD:
        if needle.lower() in lowered:
            problems.append(f"style.css: legacy gold token {needle} is still present")
    if LAYER_ORDER not in css:
        problems.append(f"style.css: missing `{LAYER_ORDER}`")
    if not re.search(r"--accent-mark\s*:", css):
        problems.append("style.css: --accent-mark is not defined")
    if PILL_RADIUS.search(css):
        problems.append("style.css: pill-shaped border-radius (999/9999/50/100px) is still used")
    for selector, body in RULE.findall(css):
        for declaration in re.findall(r"box-shadow\s*:\s*([^;]+);", body):
            for shadow in _split_top_level(declaration, ","):
                if _blur_of(shadow) > 0 and ".modal" not in selector:
                    problems.append(f"style.css: soft shadow outside .modal in `{selector.strip()}`")
    for needle in FORBIDDEN_CSS_STRINGS:
        if needle in css:
            problems.append(f"style.css: forbidden legacy string {needle!r} is present")
    supports_at = css.find(SCROLL_SUPPORTS)
    if supports_at < 0 or css.find("animation-timeline: scroll(", supports_at + len(SCROLL_SUPPORTS)) < 0:
        problems.append(f"style.css: scroll-driven progress must sit inside `{SCROLL_SUPPORTS}`")
    # <html lang="en"> matches [lang="en"]; without this the whole page is display:none in English.
    hide_at = css.find(HIDE_EN)
    if hide_at >= 0 and css.find(KEEP_HTML_VISIBLE, hide_at) < 0:
        problems.append(f"style.css: `{KEEP_HTML_VISIBLE}` must follow `{HIDE_EN}` or English mode renders a blank page")
    return problems


def _function_body(js: str, name: str) -> str | None:
    start = js.find(f"function {name}(")
    if start < 0:
        return None
    open_at = js.find("{", start)
    depth = 0
    for index in range(open_at, len(js)):
        if js[index] == "{":
            depth += 1
        elif js[index] == "}":
            depth -= 1
            if depth == 0:
                return js[open_at:index + 1]
    return None


def problems_in_main(js: str) -> list[str]:
    body = _function_body(js, "initViewTransitions")
    if body is None:
        return ["main.js: initViewTransitions() is missing"]
    problems: list[str] = []
    for needle in ("startViewTransition", "prefers-reduced-motion"):
        if needle not in body:
            problems.append(f"main.js: initViewTransitions() must use {needle}")
    if body is not None and ".catch(" not in body:
        problems.append("main.js: initViewTransitions() must swallow skipped-transition rejections with .catch(")
    if "safeInit(initViewTransitions" not in js:
        problems.append("main.js: initViewTransitions is not registered with safeInit")
    return problems


def self_test() -> None:
    good_html = '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400&family=Geist+Mono:wght@400&family=Noto+Sans+JP:wght@400&display=swap" rel="stylesheet">'
    header = '<a class="header-brand"></a><div class="header-tab-row"></div><div class="header-actions"></div>'
    good_html = good_html + header
    assert problems_in_index(good_html) == []
    assert any("DOM order" in p for p in problems_in_index(good_html.replace("header-actions", "x").replace("header-tab-row", "header-actions").replace("x", "header-tab-row")))
    old_html = good_html.replace("Geist+Mono", "DM+Sans")
    assert any("Geist+Mono" in p for p in problems_in_index(old_html))
    assert any("DM+Sans" in p for p in problems_in_index(old_html))

    good_css = f"{LAYER_ORDER}\n@layer tokens {{ :root {{ --accent-mark: #ee4b24; }} }}\n" \
               ".rule { box-shadow: 0 1px 0 #111, 0 0 0 3px #fff; border-radius: 4px; }\n" \
               ".modal-container { box-shadow: 0 20px 40px rgba(0,0,0,.3); }\n" \
               f"{SCROLL_SUPPORTS} {{ .ring {{ animation-timeline: scroll(root); }} }}\n" \
               f"{HIDE_EN}\n{KEEP_HTML_VISIBLE}\n"
    assert problems_in_css(good_css) == [], problems_in_css(good_css)
    assert any("scroll-driven" in p for p in problems_in_css(good_css.replace("animation-timeline: scroll(root);", "")))
    assert any("blank page" in p for p in problems_in_css(good_css.replace(KEEP_HTML_VISIBLE, "")))
    assert any("soft shadow" in p for p in problems_in_css(good_css + ".card { box-shadow: 0 4px 14px rgba(0,0,0,.1); }"))
    assert any("pill" in p for p in problems_in_css(good_css + ".chip { border-radius: 999px; }"))
    assert any("gold" in p for p in problems_in_css(good_css + ".x { color: #c6a15b; }"))
    assert any("Cormorant" in p for p in problems_in_css(good_css + ".x { font-family: 'Cormorant Garamond'; }"))
    assert any("@keyframes blink" in p for p in problems_in_css(good_css + "@keyframes blink { 50% { opacity: 0; } }"))
    assert any("@layer" in p for p in problems_in_css(good_css.replace(LAYER_ORDER, "")))

    good_js = "function initViewTransitions() { const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches; if (!reduce) document.startViewTransition(() => {}).finished.catch(() => {}); }\n" \
              "safeInit(initViewTransitions, 'ViewTransitions');"
    assert problems_in_main(good_js) == [], problems_in_main(good_js)
    assert any(".catch(" in p for p in problems_in_main(good_js.replace(".catch(", ".then(")))
    assert any("missing" in p for p in problems_in_main("function other() {}"))
    assert any("prefers-reduced-motion" in p for p in problems_in_main(good_js.replace("prefers-reduced-motion", "x")))
    assert any("safeInit" in p for p in problems_in_main(good_js.replace("safeInit(initViewTransitions", "nothing(")))


def main() -> None:
    self_test()
    problems = problems_in_index(INDEX.read_text(encoding="utf-8"))
    problems += problems_in_css(STYLE.read_text(encoding="utf-8"))
    problems += problems_in_main(MAIN.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Design system problems:\n  - " + "\n  - ".join(problems))
    print("OK: fonts, layers, accent tokens, shapes, and shadows follow the Index design system")


if __name__ == "__main__":
    main()
