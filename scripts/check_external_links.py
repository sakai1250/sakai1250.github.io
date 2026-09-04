#!/usr/bin/env python3

from html.parser import HTMLParser
from http.client import InvalidURL
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import os
import re
import time


SOURCE_FILES = (
    "README.md",
    "SECURITY.md",
    ".well-known/security.txt",
    "llms.txt",
    "assets/cv.txt",
)
HTML_FILES = ("index.html", "404.html")
DEPLOYMENT_HOST = "sakai1250.github.io"


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        url = ""
        if tag == "a":
            url = attrs.get("href", "")
        elif tag == "img":
            url = attrs.get("src", "")
        if url.startswith(("http://", "https://")):
            self.links.add(url)


def hostname(url):
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def collect_links():
    parser = LinkParser()
    for path in HTML_FILES:
        parser.feed(Path(path).read_text(encoding="utf-8"))

    links = set(parser.links)
    url_pattern = re.compile(r"https?://[^\s<>\"'`)\]]+")
    for path in SOURCE_FILES:
        links.update(url_pattern.findall(Path(path).read_text(encoding="utf-8")))
    return links


def should_check(url, event_name):
    host = hostname(url)
    if host in {"localhost", "127.0.0.1", "::1"}:
        return False
    # A PR or push can reference content that Pages has not deployed yet.
    # Scheduled/manual runs verify the live site once deployment has settled.
    if host == DEPLOYMENT_HOST and event_name in {"push", "pull_request"}:
        return False
    return True


def check_url(url):
    status = None
    error = None
    success = False
    host = hostname(url)

    for method in ("HEAD", "GET"):
        for attempt in range(2):
            try:
                request = Request(
                    url,
                    method=method,
                    headers={"User-Agent": "Mozilla/5.0 portfolio-link-check/1.0"},
                )
                with urlopen(request, timeout=15) as response:
                    status = response.status
                error = None
                success = 200 <= status < 400
                break
            except HTTPError as exc:
                status = exc.code
                error = str(exc)

                # These responses usually mean the page exists but rejects automation.
                if status in (401, 403, 429) or (
                    status == 999
                    and (host == "linkedin.com" or host.endswith(".linkedin.com"))
                ):
                    error = None
                    success = True
                    break

                # A server may reject HEAD while still serving GET normally.
                if method == "HEAD" and status in (400, 405, 501):
                    break

                # These are deterministic broken-link responses.
                if status in (404, 410):
                    break
            except (URLError, TimeoutError, InvalidURL, ValueError) as exc:
                status = None
                error = str(exc)

            if attempt == 0:
                time.sleep(0.75)

        if success or status in (404, 410):
            break
        if method == "HEAD":
            status = None
            error = None

    return success, status, error


def main():
    event_name = os.environ.get("GITHUB_EVENT_NAME", "")
    links = {
        url for url in collect_links() if should_check(url, event_name)
    }

    failures = []
    print(f"Checking {len(links)} external links and images")

    for url in sorted(links):
        success, status, error = check_url(url)
        if not success:
            failures.append((url, status, error))
            print(f'FAIL {status or "ERR"}: {url} {error or ""}')
        else:
            print(f"OK   {status}: {url}")

    if failures:
        raise SystemExit(f"{len(failures)} external link(s) or image(s) are broken or unreachable")


if __name__ == "__main__":
    main()
