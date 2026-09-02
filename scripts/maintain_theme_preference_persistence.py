#!/usr/bin/env python3
"""Persist a site theme only after an explicit user choice."""

from pathlib import Path
import re


path = Path("main.js")
text = path.read_text(encoding="utf-8")

legacy_signature = "    const set = (t, animate) => {"
current_signature = "    const set = (t, animate, persist = false) => {"
if legacy_signature in text:
    text = text.replace(legacy_signature, current_signature, 1)
elif current_signature not in text:
    raise SystemExit("Could not find theme setter signature")

legacy_storage = "        safeStorageSet('theme', t);"
current_storage = "        if (persist) safeStorageSet('theme', t);"
if legacy_storage in text:
    text = text.replace(legacy_storage, current_storage, 1)
elif current_storage not in text:
    raise SystemExit("Could not find theme storage update")

legacy_click = "    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true));"
current_click = "    if (btn) btn.addEventListener('click', () => set(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true, true));"
if legacy_click in text:
    text = text.replace(legacy_click, current_click, 1)
elif current_click not in text:
    raise SystemExit("Could not find explicit theme choice handler")

initial_set = "    set(safeStorageGet('theme') || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'), false);"
if initial_set not in text:
    raise SystemExit("Theme initialization must keep using the saved value or current system preference")

if re.search(r"^\s*safeStorageSet\('theme', t\);\s*$", text, re.MULTILINE):
    raise SystemExit("Theme initialization still persists the resolved system preference unconditionally")
if text.count(current_storage) != 1 or text.count(current_click) != 1:
    raise SystemExit("Theme preference persistence must have exactly one explicit write path")

path.write_text(text, encoding="utf-8")
