#!/usr/bin/env python3
"""Guard the thumbnail cache fallback policy used by asset maintenance."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = ROOT / "scripts" / "sync_readme_assets.py"


def main() -> None:
    text = SYNC_SCRIPT.read_text(encoding="utf-8")
    required = [
        "expected_files.add(filename)",
        "if local_path.is_file():",
        "return local_web_path",
        "if filename not in expected_files:",
        'local_img.startswith("assets/thumbnails/")',
        'sync_index_app_thumbnails(data["apps"])',
    ]
    missing = [snippet for snippet in required if snippet not in text]
    if missing:
        raise SystemExit(f"Thumbnail cache fallback policy is incomplete: {missing}")

    legacy_cleanup = "if filename not in " + "generated_files:"
    if legacy_cleanup in text:
        raise SystemExit(
            "Thumbnail cleanup still depends on current-run download success"
        )


if __name__ == "__main__":
    main()
