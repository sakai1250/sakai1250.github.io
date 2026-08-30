from pathlib import Path


path = Path('main.js')
text = path.read_text(encoding='utf-8')

legacy = """function initStats() {
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

reduced_motion = """function initStats() {
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

if legacy in text:
    text = text.replace(legacy, reduced_motion, 1)
elif reduced_motion not in text:
    raise SystemExit('Could not find the expected stats animation implementation')

required = [
    "window.matchMedia('(prefers-reduced-motion: reduce)').matches",
    'if (reduceMotion) {',
    'obj.textContent = end;',
    'requestAnimationFrame(step);',
]
missing = [snippet for snippet in required if snippet not in text]
if missing:
    raise SystemExit(f'Reduced-motion stats policy is incomplete: {missing}')

path.write_text(text, encoding='utf-8')
