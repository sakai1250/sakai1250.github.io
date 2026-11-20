#!/usr/bin/env python3
"""Guard text, link, and hero colour contrast declared as CSS custom properties."""

from __future__ import annotations

import math
import re
from pathlib import Path

STYLE = Path("style.css")

TEXT_MIN = 4.5
TEXT_TOKENS = ("--text-main", "--text-sub", "--muted", "--accent")
MARK_MIN = 3.0
RGB_TOLERANCE = 3 / 255


def _encode(linear: float) -> float:
    linear = min(1.0, max(0.0, linear))
    if linear <= 0.0031308:
        return 12.92 * linear
    return 1.055 * linear ** (1 / 2.4) - 0.055


def _decode(encoded: float) -> float:
    if encoded <= 0.04045:
        return encoded / 12.92
    return ((encoded + 0.055) / 1.055) ** 2.4


def _oklch_to_srgb(lightness: float, chroma: float, hue: float) -> tuple[float, float, float]:
    a = chroma * math.cos(math.radians(hue))
    b = chroma * math.sin(math.radians(hue))
    l_ = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    red = 4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
    green = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
    blue = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_
    return _encode(red), _encode(green), _encode(blue)


def parse_color(value: str) -> tuple[float, float, float]:
    """Return gamma-encoded sRGB (0-1) for `#rgb`, `#rrggbb`, or `oklch(L C H)`."""
    text = value.strip()
    if text.startswith("#"):
        digits = text[1:]
        if len(digits) == 3:
            digits = "".join(ch * 2 for ch in digits)
        if len(digits) != 6:
            raise ValueError(f"unsupported hex colour: {value!r}")
        return tuple(int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    match = re.fullmatch(r"oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*(?:/\s*[\d.]+%?)?\s*\)", text)
    if not match:
        raise ValueError(f"unsupported colour: {value!r}")
    lightness_raw, chroma, hue = match.groups()
    lightness = float(lightness_raw[:-1]) / 100 if lightness_raw.endswith("%") else float(lightness_raw)
    return _oklch_to_srgb(lightness, float(chroma), float(hue))


def _luminance(rgb: tuple[float, float, float]) -> float:
    red, green, blue = (_decode(channel) for channel in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(fg: str, bg: str) -> float:
    lighter, darker = sorted((_luminance(parse_color(fg)), _luminance(parse_color(bg))), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _declarations(block: str) -> dict[str, str]:
    return {
        name: value.strip()
        for name, value in re.findall(r"(--[a-zA-Z0-9-]+)\s*:\s*([^;]+);", block)
    }


def theme_tokens(css: str) -> dict[str, dict[str, str]]:
    """Custom properties of the light (`:root`) and dark (`[data-theme="dark"]`) blocks."""
    light = re.search(r":root\s*\{([^}]*)\}", css)
    dark = re.search(r'\[data-theme="dark"\]\s*\{([^}]*)\}', css)
    if not light or not dark:
        raise SystemExit("style.css: could not find the :root and [data-theme=\"dark\"] token blocks")
    return {"light": _declarations(light.group(1)), "dark": _declarations(dark.group(1))}


def _resolve(tokens: dict[str, str], name: str) -> str | None:
    value = tokens.get(name)
    if value is None:
        return None
    reference = re.fullmatch(r"var\((--[a-zA-Z0-9-]+)\)", value)
    return tokens.get(reference.group(1)) if reference else value


def problems_in_css(css: str) -> list[str]:
    themes = theme_tokens(css)
    problems: list[str] = []
    for theme in ("light", "dark"):
        tokens = {**themes["light"], **themes[theme]} if theme == "dark" else themes["light"]
        background = _resolve(tokens, "--bg")
        if background is None:
            problems.append(f"{theme}: --bg is not defined")
            continue
        for name in TEXT_TOKENS:
            colour = _resolve(tokens, name)
            if colour is None:
                problems.append(f"{theme}: {name} is not defined")
            elif (ratio := contrast_ratio(colour, background)) < TEXT_MIN:
                problems.append(f"{theme}: {name} on --bg is {ratio:.2f}:1 (needs {TEXT_MIN}:1)")
        # Backgrounds other than --bg that carry text: the mobile header uses --bg-2 and the
        # footer share button uses --surface-2.
        for bg_name, text_names in (("--bg-2", TEXT_TOKENS), ("--surface-2", ("--text-main", "--text-sub"))):
            alt = _resolve(tokens, bg_name)
            if alt is None:
                continue
            for name in text_names:
                colour = _resolve(tokens, name)
                if colour is not None and (ratio := contrast_ratio(colour, alt)) < TEXT_MIN:
                    problems.append(f"{theme}: {name} on {bg_name} is {ratio:.2f}:1 (needs {TEXT_MIN}:1)")
        mark = _resolve(tokens, "--accent-mark")
        if mark is not None and (ratio := contrast_ratio(mark, background)) < MARK_MIN:
            problems.append(f"{theme}: --accent-mark on --bg is {ratio:.2f}:1 (needs {MARK_MIN}:1)")
        hero_fg, hero_bg = _resolve(tokens, "--hero-fg"), _resolve(tokens, "--hero-bg")
        if hero_fg and hero_bg and (ratio := contrast_ratio(hero_fg, hero_bg)) < TEXT_MIN:
            problems.append(f"{theme}: --hero-fg on --hero-bg is {ratio:.2f}:1 (needs {TEXT_MIN}:1)")
        rgb = tokens.get("--hero-accent-rgb")
        if rgb and mark:
            declared = tuple(int(part) / 255 for part in rgb.split(","))
            actual = parse_color(mark)
            if any(abs(a - b) > RGB_TOLERANCE for a, b in zip(declared, actual)):
                problems.append(f"{theme}: --hero-accent-rgb ({rgb}) does not match --accent-mark")
    return problems


def self_test() -> None:
    assert round(contrast_ratio("#000000", "#ffffff"), 2) == 21.0
    assert contrast_ratio("oklch(0.178 0 90)", "oklch(0.991 0.001 106)") >= 18.0
    vivid = parse_color("oklch(0.639 0.206 34)")
    hexed = parse_color("#EE4B24")
    assert all(abs(a - b) <= 0.02 for a, b in zip(vivid, hexed)), (vivid, hexed)

    good = ':root { --bg: #ffffff; --text-main: #000000; --text-sub: #333333; --muted: #555555; --accent: #aa2200; }\n' \
           '[data-theme="dark"] { --bg: #000000; --text-main: #ffffff; --text-sub: #dddddd; --muted: #aaaaaa; --accent: #ff7755; }'
    assert problems_in_css(good) == [], problems_in_css(good)
    weak = good.replace("--muted: #555555", "--muted: #bbbbbb")
    assert any("--muted" in problem for problem in problems_in_css(weak))
    weak_alt = good.replace("--accent: #aa2200; }", "--accent: #aa2200; --bg-2: #e0e0e0; }", 1)
    assert any("--muted on --bg-2" in problem for problem in problems_in_css(weak_alt)), problems_in_css(weak_alt)
    mismatched = good.replace("--accent: #aa2200;", "--accent: #aa2200; --accent-mark: #ee4b24; --hero-accent-rgb: 0, 0, 0;", 1)
    assert any("--hero-accent-rgb" in problem for problem in problems_in_css(mismatched))


def main() -> None:
    self_test()
    problems = problems_in_css(STYLE.read_text(encoding="utf-8"))
    if problems:
        raise SystemExit("Colour contrast problems:\n  - " + "\n  - ".join(problems))
    print("OK: declared text, link, and hero colours meet the contrast thresholds in both themes")


if __name__ == "__main__":
    main()
