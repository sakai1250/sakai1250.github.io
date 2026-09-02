from pathlib import Path


path = Path("main.js")
js = path.read_text(encoding="utf-8")

position_based = """function getSectionId(content, section, index) {
    const currentId = section?.id || '';
    const generatedId = /^(?:(?:research|engineer|portfolio)-)?section-\\d+$/;
    if (currentId && !generatedId.test(currentId)) return currentId;

    const prefix = content?.id?.replace(/-content$/, '') || 'portfolio';
    return `${prefix}-section-${index}`;
}
"""

semantic = """function getSectionId(content, section, index) {
    const currentId = section?.id || '';
    const generatedId = /^(?:(?:research|engineer|portfolio)-)?section-\\d+$/;
    if (currentId && !generatedId.test(currentId)) return currentId;

    const prefix = content?.id?.replace(/-content$/, '') || 'portfolio';
    const englishTitle = section?.querySelector('.section-title [lang=\"en\"]')?.textContent.trim() || '';
    const slug = englishTitle
        .toLowerCase()
        .replace(/&/g, ' and ')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
    return slug ? `${prefix}-${slug}` : `${prefix}-section-${index}`;
}
"""

if position_based in js:
    js = js.replace(position_based, semantic, 1)
elif semantic not in js:
    raise SystemExit("Could not find expected section ID generation")

required_markers = (
    "const englishTitle = section?.querySelector('.section-title [lang=\"en\"]')?.textContent.trim() || '';",
    "return slug ? `${prefix}-${slug}` : `${prefix}-section-${index}`;",
)
for marker in required_markers:
    if marker not in js:
        raise SystemExit(f"Missing stable section ID marker: {marker}")

path.write_text(js, encoding="utf-8")
