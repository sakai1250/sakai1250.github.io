#!/usr/bin/env python3
"""Require meaningful accessible names for non-hidden form controls."""

from html.parser import HTMLParser
from pathlib import Path


HTML_FILES = (Path("index.html"), Path("404.html"))


def normalized_text(parts):
    return " ".join("".join(parts).split())


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.labels = []
        self.label_stack = []
        self.controls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id", "").strip()
        if element_id:
            self.ids.add(element_id)

        if tag == "label":
            label = {"for": attrs.get("for", "").strip(), "text": []}
            self.labels.append(label)
            self.label_stack.append(label)
            return

        if tag not in ("input", "textarea", "select"):
            return

        input_type = attrs.get("type", "").lower()
        if tag == "input" and input_type == "hidden":
            return

        implicit_label = self.label_stack[-1] if self.label_stack else None
        self.controls.append((tag, attrs, implicit_label))

    def handle_data(self, data):
        if self.label_stack:
            self.label_stack[-1]["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "label" and self.label_stack:
            self.label_stack.pop()

    def label_text_for(self, control_id):
        for label in self.labels:
            if label["for"] == control_id and normalized_text(label["text"]):
                return True
        return False


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
    if implicit_label and normalized_text(implicit_label["text"]):
        return True
    if control_id and parser.label_text_for(control_id):
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

        dangling_labels = sorted(
            label["for"]
            for label in parser.labels
            if label["for"] and label["for"] not in parser.ids
        )
        if dangling_labels:
            problems.append(
                f"{path}: labels reference missing ids: {dangling_labels}"
            )

        for tag, attrs, implicit_label in parser.controls:
            checked += 1
            if not control_has_name(tag, attrs, implicit_label, parser):
                problems.append(
                    f"{path}: form control has no meaningful accessible name: "
                    f"{describe_control(tag, attrs)}"
                )

    if problems:
        raise SystemExit("\n".join(problems))

    print(f"OK: {checked} non-hidden form controls have meaningful accessible names")


if __name__ == "__main__":
    main()
