#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path


class ControlNameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_control = None
        self.unnamed_controls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        is_control = tag == 'button' or (tag == 'a' and attrs.get('href'))
        if not is_control:
            return
        self.current_control = {
            'tag': tag,
            'id': attrs.get('id', ''),
            'href': attrs.get('href', ''),
            'aria_label': attrs.get('aria-label', '').strip(),
            'aria_labelledby': attrs.get('aria-labelledby', '').strip(),
            'text': [],
        }

    def handle_data(self, data):
        if self.current_control is not None:
            self.current_control['text'].append(data)

    def handle_endtag(self, tag):
        if self.current_control is None or tag != self.current_control['tag']:
            return
        control = self.current_control
        visible_text = ''.join(control['text']).strip()
        if not (visible_text or control['aria_label'] or control['aria_labelledby']):
            if control['id']:
                identifier = f"#{control['id']}"
            elif control['tag'] == 'a':
                identifier = f"<a href={control['href']!r}>"
            else:
                identifier = '<button>'
            self.unnamed_controls.append(identifier)
        self.current_control = None


problems = []
for html_path in (Path('index.html'), Path('404.html')):
    parser = ControlNameParser()
    parser.feed(html_path.read_text(encoding='utf-8'))
    if parser.unnamed_controls:
        problems.append(
            f"{html_path}: interactive controls missing an accessible name "
            f"{parser.unnamed_controls}"
        )

if problems:
    raise SystemExit('\n'.join(problems))

print('OK: links and buttons expose visible text or an ARIA accessible name')
