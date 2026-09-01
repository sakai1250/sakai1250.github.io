#!/usr/bin/env python3
"""Require accessible names for non-hidden form controls."""

from html.parser import HTMLParser
from pathlib import Path


HTML_FILES = (Path("index.html"), Path("404.html"))


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.label_fors = set()
        self.controls = []
        self.label_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id", "").strip()
        if element_id:
            self.ids.add(element_id)

        if tag == "label":
            label_for = attrs.get("for", "").strip()
            if label_for:
                self.label_fors.add(label_for)
            self.label_depth += 1
            return

        if tag not in ("input", "textarea", "select"):
            return

        input_type = attrs.get("type", "").lower()
        if tag == "input" and input_type == "hidden":
            return

        self.controls.append((tag, attrs, self.label_depth > 0))

    def handle_endtag(self, tag):
        if tag == "label" and self.label_depth:
            self.label_depth -= 1


def native_input_name(attrs):
    input_type = attrs.get("type", "").lower()
    if input_type in ("submit", "reset"):
        return True
    if input_type == "button":
        return bool(attrs.get("value", "").strip())
    if input_type == "image":
        return bool(attrs.get("alt", "").strip())
    return False


def control_has_name(tag, attrs, implicit_label, parser):
    control_id = attrs.get("id", "").strip()
    if implicit_label or (control_id and control_id in parser.label_fors):
        return True

    if attrs.get("aria-label", "").strip():
        return True

    labelledby = attrs.get("aria-labelledby", "").split()
    if labelledby and all(ref in parser.ids for ref in labelledby):
        return True

    return tag == "input" and native_input_name(attrs)


def describe_control(tag, attrs):
    details = [tag]
    for key in ("type", "id", "name"):
        value = attrs.get(key, "").strip()
        if value:
            details.append(f"{key}={value!r}")
    return " ".join(details)


def main():
    problems = []
    checked = 0

    for path in HTML_FILES:
        parser = Parser()
        parser.feed(path.read_text(encoding="utf-8"))

        for tag, attrs, implicit_label in parser.controls:
            checked += 1
            if not control_has_name(tag, attrs, implicit_label, parser):
                problems.append(
                    f"{path}: form control has no accessible name: "
                    f"{describe_control(tag, attrs)}"
                )

    if problems:
        raise SystemExit("\n".join(problems))

    print(f"OK: {checked} non-hidden form controls have accessible names")


if __name__ == "__main__":
    main()
