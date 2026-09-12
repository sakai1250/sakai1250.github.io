#!/usr/bin/env python3
"""Synchronize portfolio badge/app metadata and app thumbnails from the profile README."""

from __future__ import annotations

import json
import os
import re
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
README_URL = "https://raw.githubusercontent.com/sakai1250/sakai1250/main/Readme.md"
ASSETS_DIR = ROOT / "assets"
THUMB_DIR = ASSETS_DIR / "thumbnails"
DATA_FILE = ASSETS_DIR / "data.json"
INDEX_FILE = ROOT / "index.html"

ORGANIZATION_ALT_BY_SRC = {
    "https://github.com/user-attachments/assets/06029876-4a7b-44fe-8df6-cac6bbbf8391": "RM-NAGOYASHACHIHOKO",
    "https://github.com/user-attachments/assets/3df7dbab-02ff-494d-b468-3bf755043a2c": "JPHacks",
    "https://github.com/user-attachments/assets/7109b8d7-da71-4b8d-8858-773980b358d5": "Jogiken",
}
GENERIC_ORGANIZATION_ALTS = {"GitHub画像"}


def extract_images(content: str, header_pattern: str) -> list[dict[str, str]]:
    pattern = re.compile(
        rf"^#+\s*(?:{header_pattern})\s*$([\s\S]*?)(?=^#+\s|\Z)",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        return []

    block = match.group(1)
    img_pattern = re.compile(
        r"!\[(.*?)\]\((.*?)\)|<img\s+[^>]*src=[\"'](.*?)[\"'][^>]*>",
        re.IGNORECASE,
    )
    images: list[dict[str, str]] = []
    for match in img_pattern.finditer(block):
        if match.group(1) is not None:
            images.append({"alt": match.group(1), "src": match.group(2)})
        else:
            tag = match.group(0)
            alt_match = re.search(r"alt=[\"'](.*?)[\"']", tag, re.IGNORECASE)
            images.append(
                {
                    "alt": alt_match.group(1) if alt_match else "",
                    "src": match.group(3),
                }
            )
    return images


def normalize_organization_alts(items: list[dict[str, str]]) -> list[dict[str, str]]:
    """Replace generic source README labels with stable organization names."""
    for item in items:
        alt = item.get("alt", "").strip()
        src = item.get("src", "").strip()
        if alt and alt not in GENERIC_ORGANIZATION_ALTS:
            continue

        replacement = ORGANIZATION_ALT_BY_SRC.get(src)
        if not replacement:
            raise SystemExit(
                "Organization badge has generic alt text with an unknown image source: "
                f"{src!r}"
            )
        item["alt"] = replacement
    return items


def sync_app_thumbnail(full_repo: str, img_src: str) -> str:
    filename = f"{full_repo.replace('/', '_')}.webp"
    local_path = THUMB_DIR / filename
    local_web_path = f"assets/thumbnails/{filename}"

    try:
        image_res = requests.get(img_src, timeout=20)
        image_res.raise_for_status()
        img = Image.open(BytesIO(image_res.content))
        if img.mode == "P":
            img = img.convert("RGBA")
        elif img.mode == "CMYK":
            img = img.convert("RGB")
        img.thumbnail((400, 400))
        img.save(local_path, "WEBP", quality=85)
        return local_web_path
    except Exception as exc:
        print(f"Error processing image for {full_repo}: {exc}")
        if local_path.is_file():
            print(f"Using cached thumbnail for {full_repo}: {local_web_path}")
            return local_web_path
        return img_src


def sync_index_app_thumbnails(apps: dict[str, dict]) -> None:
    """Use cached app thumbnails in static cards when an exact repo match exists."""
    text = INDEX_FILE.read_text(encoding="utf-8")
    original = text
    apps_section_start = text.find('id="engineer-my-apps-and-services"')
    search_start = apps_section_start if apps_section_start >= 0 else 0

    for full_repo, app in apps.items():
        local_img = str(app.get("img", "")).strip()
        if not local_img.startswith("assets/thumbnails/"):
            continue

        repo_url = f"https://github.com/{full_repo}"
        repo_pos = text.find(repo_url, search_start)
        if repo_pos < 0:
            continue

        card_start = text.rfind('<div class="app-card"', search_start, repo_pos)
        img_start = text.find("<img", card_start, repo_pos) if card_start >= 0 else -1
        img_end = text.find(">", img_start, repo_pos) if img_start >= 0 else -1
        if img_start < 0 or img_end < 0:
            continue

        img_tag = text[img_start : img_end + 1]
        if 'class="app-thumb"' not in img_tag:
            continue

        updated_tag, count = re.subn(
            r'\bsrc=(["\']).*?\1',
            f'src="{local_img}"',
            img_tag,
            count=1,
            flags=re.IGNORECASE,
        )
        if count:
            text = text[:img_start] + updated_tag + text[img_end + 1 :]

    if text != original:
        INDEX_FILE.write_text(text, encoding="utf-8")


def main() -> None:
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    expected_files: set[str] = set()

    response = requests.get(README_URL, timeout=20)
    response.raise_for_status()
    content = response.text

    data: dict[str, dict] = {"badges": {}, "apps": {}}
    data["badges"]["badges-languages"] = extract_images(
        content, r"Programming\s+languages|Languages|言語"
    )
    data["badges"]["badges-frameworks"] = extract_images(
        content, r"Frameworks|Tools|ツール|技術"
    )
    data["badges"]["badges-orgs"] = normalize_organization_alts(
        extract_images(content, r"Organizations|所属")
    )

    apps_match = re.search(
        r"^##\s+My Apps\s*$([\s\S]*?)(?=^##\s|\Z)",
        content,
        re.IGNORECASE | re.MULTILINE,
    )
    apps_content = apps_match.group(1) if apps_match else ""
    app_blocks = re.findall(
        r"<td\b[^>]*>([\s\S]*?)</td>",
        apps_content,
        re.IGNORECASE,
    )

    for block in app_blocks:
        repo_match = re.search(
            r"<a\b[^>]*href=[\"']https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?[\"'][^>]*>",
            block,
            re.IGNORECASE,
        )
        if not repo_match:
            continue

        full_repo = repo_match.group(1)
        paragraph_match = re.search(r"<p\b[^>]*>([\s\S]*?)</p>", block, re.IGNORECASE)
        desc = ""
        if paragraph_match:
            desc = re.sub(r"<[^>]+>", " ", paragraph_match.group(1))
            desc = re.sub(r"\s+", " ", desc).strip()

        img_match = re.search(
            r"<img\s+[^>]*src=[\"'](.*?)[\"']", block, re.IGNORECASE
        )
        img_src = img_match.group(1) if img_match else None

        app_data = {"desc": desc}
        if img_src and img_src.startswith("http"):
            filename = f"{full_repo.replace('/', '_')}.webp"
            expected_files.add(filename)
            app_data["img"] = sync_app_thumbnail(full_repo, img_src)

        data["apps"][full_repo] = app_data

    for filename in os.listdir(THUMB_DIR):
        if filename not in expected_files:
            (THUMB_DIR / filename).unlink()

    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    sync_index_app_thumbnails(data["apps"])


if __name__ == "__main__":
    main()
