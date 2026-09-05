#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path


class ControlNameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current_control = None
        self.unnamed_controls = []
        self.document_ids = set()
        self.labelledby_references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get('id', '').strip()
        if element_id:
            self.document_ids.add(element_id)

        if self.current_control is not None and tag == 'img':
            alt = attrs.get('alt', '').strip()
            if alt:
                self.current_control['text'].append(alt)
            return

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
        accessible_text = ''.join(control['text']).strip()
        if control['id']:
            identifier = f"#{control['id']}"
        elif control['tag'] == 'a':
            identifier = f"<a href={control['href']!r}>"
        else:
            identifier = '<button>'

        if control['aria_labelledby']:
            self.labelledby_references.append(
                (identifier, control['aria_labelledby'].split())
            )

        if not (accessible_text or control['aria_label'] or control['aria_labelledby']):
            self.unnamed_controls.append(identifier)
        self.current_control = None

    def missing_labelledby_references(self):
        missing = []
        for identifier, references in self.labelledby_references:
            unknown = [reference for reference in references if reference not in self.document_ids]
            if unknown:
                missing.append(f"{identifier} -> {unknown}")
        return missing


problems = []
for html_path in (Path('index.html'), Path('404.html')):
    parser = ControlNameParser()
    parser.feed(html_path.read_text(encoding='utf-8'))
    if parser.unnamed_controls:
        problems.append(
            f"{html_path}: interactive controls missing an accessible name "
            f"{parser.unnamed_controls}"
        )
    missing_references = parser.missing_labelledby_references()
    if missing_references:
        problems.append(
            f"{html_path}: aria-labelledby references missing element IDs "
            f"{missing_references}"
        )

if problems:
    raise SystemExit('\n'.join(problems))

print('OK: links and buttons expose valid text, image alt text, or an ARIA accessible name')
