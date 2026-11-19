from pathlib import Path


path = Path('main.js')
text = path.read_text(encoding='utf-8')

# The header counts are plain numbers written once at load; there is no count-up
# animation left to keep reduced-motion aware. Require that static form.
static_stats_marker = """function initStats() {
    const researchSections"""
static_stats_assignment = 'if (el) el.textContent = s.v;'
if static_stats_marker not in text or static_stats_assignment not in text or 'animate(el, s.v)' in text:
    raise SystemExit('Could not find the expected static stats implementation')

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

sticky_aware_toc_scroll = """            const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            window.scrollTo({
                top: s.getBoundingClientRect().top + window.scrollY - getStickyOffset(),
                behavior: reduceMotion ? 'auto' : 'smooth'
            });"""

if legacy_toc_scroll in text:
    text = text.replace(legacy_toc_scroll, sticky_aware_toc_scroll, 1)
elif reduced_motion_toc_scroll in text:
    text = text.replace(reduced_motion_toc_scroll, sticky_aware_toc_scroll, 1)
elif sticky_aware_toc_scroll not in text:
    raise SystemExit('Could not find the expected table-of-contents navigation implementation')

required = [
    "window.matchMedia('(prefers-reduced-motion: reduce)').matches",
    "behavior: reduceMotion ? 'auto' : 'smooth'",
    'top: target.getBoundingClientRect().top + window.scrollY - getStickyOffset()',
    'top: s.getBoundingClientRect().top + window.scrollY - getStickyOffset()',
    'top: section.getBoundingClientRect().top + window.scrollY - getStickyOffset()',
]
missing = [snippet for snippet in required if snippet not in text]
if missing:
    raise SystemExit(f'Reduced-motion or sticky-offset policy is incomplete: {missing}')
if text.count("behavior: reduceMotion ? 'auto' : 'smooth'") < 2:
    raise SystemExit('Reduced-motion policy must cover both TOC and sticky section navigation')

path.write_text(text, encoding='utf-8')
