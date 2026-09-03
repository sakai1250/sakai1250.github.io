from pathlib import Path


path = Path('main.js')
text = path.read_text(encoding='utf-8')

legacy_stats = """function initStats() {
    const animate = (obj, end) => {
        let start = null;
        const step = (ts) => {
            if (!start) start = ts;
            const progress = Math.min((ts - start) / 1500, 1);
            obj.innerHTML = Math.floor(progress * end);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };"""

reduced_motion_stats = """function initStats() {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const animate = (obj, end) => {
        if (reduceMotion) {
            obj.textContent = end;
            return;
        }
        let start = null;
        const step = (ts) => {
            if (!start) start = ts;
            const progress = Math.min((ts - start) / 1500, 1);
            obj.textContent = Math.floor(progress * end);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };"""

if legacy_stats in text:
    text = text.replace(legacy_stats, reduced_motion_stats, 1)
elif reduced_motion_stats not in text:
    raise SystemExit('Could not find the expected stats animation implementation')

legacy_scroll = """function scrollToSection(section) {
    window.scrollTo({
        top: section.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
        behavior: 'smooth'
    });
}"""

reduced_motion_scroll = """function scrollToSection(section) {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({
        top: section.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
        behavior: reduceMotion ? 'auto' : 'smooth'
    });
}"""

shareable_reduced_motion_scroll = """function scrollToSection(section) {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    history.replaceState(null, '', `#${section.id}`);
    window.scrollTo({
        top: section.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
        behavior: reduceMotion ? 'auto' : 'smooth'
    });
}"""

if legacy_scroll in text:
    text = text.replace(legacy_scroll, reduced_motion_scroll, 1)
elif reduced_motion_scroll not in text and shareable_reduced_motion_scroll not in text:
    raise SystemExit('Could not find the expected section navigation implementation')

legacy_toc_scroll = """            const h = document.querySelector('.header-bar').offsetHeight;
            window.scrollTo({ top: s.getBoundingClientRect().top + window.scrollY - h - 20, behavior: 'smooth' });"""

reduced_motion_toc_scroll = """            const h = document.querySelector('.header-bar').offsetHeight;
            const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            window.scrollTo({
                top: s.getBoundingClientRect().top + window.scrollY - h - 20,
                behavior: reduceMotion ? 'auto' : 'smooth'
            });"""

if legacy_toc_scroll in text:
    text = text.replace(legacy_toc_scroll, reduced_motion_toc_scroll, 1)
elif reduced_motion_toc_scroll not in text:
    raise SystemExit('Could not find the expected table-of-contents navigation implementation')

required = [
    "window.matchMedia('(prefers-reduced-motion: reduce)').matches",
    'if (reduceMotion) {',
    'obj.textContent = end;',
    'requestAnimationFrame(step);',
    "behavior: reduceMotion ? 'auto' : 'smooth'",
]
missing = [snippet for snippet in required if snippet not in text]
if missing:
    raise SystemExit(f'Reduced-motion policy is incomplete: {missing}')
if text.count("behavior: reduceMotion ? 'auto' : 'smooth'") < 2:
    raise SystemExit('Reduced-motion policy must cover both TOC and sticky section navigation')

path.write_text(text, encoding='utf-8')
