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
    "robots.txt",
    "sitemap.xml",
    "assets/cv.txt",
    "assets/data.json",
)
HTML_FILES = ("index.html", "404.html")
DEPLOYMENT_HOST = "sakai1250.github.io"
SOCIAL_IMAGE_META_KEYS = {"og:image", "twitter:image"}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
        self.non_get_form_actions = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        url = ""
        if tag == "a":
            url = attrs.get("href", "")
        elif tag == "img":
            url = attrs.get("src", "")
        elif tag == "link" and "stylesheet" in attrs.get("rel", "").split():
            url = attrs.get("href", "")
        elif tag == "meta":
            meta_key = (attrs.get("property") or attrs.get("name") or "").lower()
            if meta_key in SOCIAL_IMAGE_META_KEYS:
                url = attrs.get("content", "")
        elif tag == "form":
            url = attrs.get("action", "")
            if (
                url.startswith(("http://", "https://"))
                and attrs.get("method", "get").lower() != "get"
            ):
                self.non_get_form_actions.add(url)
        if url.startswith(("http://", "https://")):
            self.links.add(url)


def hostname(url):
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def is_insecure_external_http(url):
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return (
        parsed.scheme.lower() == "http"
        and (parsed.hostname or "").lower() not in {"localhost", "127.0.0.1", "::1"}
    )


def collect_links():
    parser = LinkParser()
    for path in HTML_FILES:
        parser.feed(Path(path).read_text(encoding="utf-8"))

    links = set(parser.links)
    url_pattern = re.compile(r"https?://[^\s<>\"'`)\]]+")
    for path in SOURCE_FILES:
        links.update(url_pattern.findall(Path(path).read_text(encoding="utf-8")))
    return links, parser.non_get_form_actions


def should_check(url, event_name):
    host = hostname(url)
    if host in {"localhost", "127.0.0.1", "::1"}:
        return False
    # A PR or push can reference content that Pages has not deployed yet.
    # Scheduled/manual runs verify the live site once deployment has settled.
    if host == DEPLOYMENT_HOST and event_name in {"push", "pull_request"}:
        return False
    return True


def check_url(url, allow_method_not_allowed=False):
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
                    final_url = response.geturl()
                if urlsplit(url).scheme.lower() == "https" and is_insecure_external_http(final_url):
                    return (
                        False,
                        status,
                        f"HTTPS redirects to insecure HTTP URL: {final_url}",
                    )
                error = None
                success = 200 <= status < 400
                break
            except HTTPError as exc:
                status = exc.code
                error = str(exc)

                # A HEAD request can be challenged even when GET is public; verify with GET.
                if status == 401 and method == "HEAD":
                    break

                # These responses usually mean the page exists but rejects automation.
                if status in (403, 429) or (
                    status == 999
                    and (host == "linkedin.com" or host.endswith(".linkedin.com"))
                ):
                    error = None
                    success = True
                    break

                # A non-GET form action can legitimately reject link-style requests.
                # 405 still confirms that the action endpoint exists; do not submit it.
                if status == 405 and allow_method_not_allowed:
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
    collected_links, non_get_form_actions = collect_links()
    insecure_links = sorted(url for url in collected_links if is_insecure_external_http(url))
    links = {
        url
        for url in collected_links
        if not is_insecure_external_http(url) and should_check(url, event_name)
    }

    failures = []
    print(f"Checking {len(links)} external links, stylesheets, form actions, and images")

    for url in insecure_links:
        failures.append((url, None, "insecure HTTP URL; use HTTPS"))
        print(f"FAIL HTTP: {url} use HTTPS")

    for url in sorted(links):
        success, status, error = check_url(
            url, allow_method_not_allowed=url in non_get_form_actions
        )
        if not success:
            failures.append((url, status, error))
            print(f'FAIL {status or "ERR"}: {url} {error or ""}')
        else:
            print(f"OK   {status}: {url}")

    if failures:
        raise SystemExit(
            f"{len(failures)} external link(s), stylesheet(s), form action(s), or image(s) are broken, insecure, or unreachable"
        )


if __name__ == "__main__":
    main()
