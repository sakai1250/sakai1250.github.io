#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path


class ControlNameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_button = None
        self.unnamed_buttons = []

    def handle_starttag(self, tag, attrs):
        if tag != 'button':
            return
        attrs = dict(attrs)
        self.current_button = {
            'id': attrs.get('id', ''),
            'aria_label': attrs.get('aria-label', '').strip(),
            'aria_labelledby': attrs.get('aria-labelledby', '').strip(),
            'text': [],
        }

    def handle_data(self, data):
        if self.current_button is not None:
            self.current_button['text'].append(data)

    def handle_endtag(self, tag):
        if tag != 'button' or self.current_button is None:
            return
        control = self.current_button
        visible_text = ''.join(control['text']).strip()
        if not (visible_text or control['aria_label'] or control['aria_labelledby']):
            identifier = f"#{control['id']}" if control['id'] else '<button>'
            self.unnamed_buttons.append(identifier)
        self.current_button = None


problems = []
for html_path in (Path('index.html'), Path('404.html')):
    parser = ControlNameParser()
    parser.feed(html_path.read_text(encoding='utf-8'))
    if parser.unnamed_buttons:
        problems.append(
            f"{html_path}: buttons missing an accessible name {parser.unnamed_buttons}"
        )

if problems:
    raise SystemExit('\n'.join(problems))

print('OK: interactive buttons expose visible text or an ARIA accessible name')
