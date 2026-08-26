from pathlib import Path


path = Path("index.html")
text = path.read_text(encoding="utf-8")

old = 'class="app-thumb" alt="icon"'
new = 'class="app-thumb" alt=""'

count = text.count(old)
if count:
    text = text.replace(old, new)
elif 'class="app-thumb" alt=""' not in text:
    raise SystemExit("Could not find app thumbnail accessibility markers")

path.write_text(text, encoding="utf-8")
