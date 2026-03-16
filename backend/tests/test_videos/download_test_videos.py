"""
Download and cache short test videos for sport detection e2e tests.

Downloads ~10-15 second clips from YouTube for each sport category
and several unrelated activities. Videos are cached in tests/test_videos/cache/
and only re-downloaded if missing.

Usage:
    python tests/test_videos/download_test_videos.py
"""

import json
import subprocess
import sys
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
MANIFEST_PATH = Path(__file__).parent / "manifest.json"

# Short, reliable YouTube clips for each category.
# Using ytsearchN: prefix to find videos by query when direct URLs become unavailable.
TEST_VIDEOS = {
    # === POSITIVE FLOWS: correct sport ===
    "snowboarding_01": {
        "url": "ytsearch1:snowboarding gopro short run",
        "sport": "snowboarding",
        "expected_env": "snow",
        "category": "positive",
    },
    "skiing_01": {
        "url": "ytsearch1:skiing gopro short run pov",
        "sport": "skiing",
        "expected_env": "snow",
        "category": "positive",
    },
    "skateboarding_01": {
        "url": "ytsearch1:skateboarding street trick short clip",
        "sport": "skateboarding",
        "expected_env": "urban",
        "category": "positive",
    },
    "surfing_01": {
        "url": "ytsearch1:surfing gopro wave short clip",
        "sport": "surfing",
        "expected_env": "water",
        "category": "positive",
    },
    # === NEGATIVE FLOWS: wrong sport selected ===
    # (These reuse positive videos but test with wrong sport selection)

    # === UNRELATED VIDEOS: no supported sport ===
    "cooking_01": {
        "url": "ytsearch1:cooking recipe kitchen short clip",
        "sport": None,
        "expected_env": "unknown",
        "category": "unrelated",
    },
    "dancing_01": {
        "url": "ytsearch1:dance performance indoor short clip",
        "sport": None,
        "expected_env": "unknown",
        "category": "unrelated",
    },
    "driving_01": {
        "url": "ytsearch1:driving dashcam road short clip",
        "sport": None,
        "expected_env": "unknown",
        "category": "unrelated",
    },
    "teaching_01": {
        "url": "ytsearch1:classroom teaching lecture short clip",
        "sport": None,
        "expected_env": "unknown",
        "category": "unrelated",
    },
    "tennis_01": {
        "url": "ytsearch1:tennis rally court short clip",
        "sport": None,
        "expected_env": "unknown",
        "category": "unrelated",
    },
    "climbing_01": {
        "url": "ytsearch1:rock climbing wall short clip",
        "sport": None,
        "expected_env": "unknown",
        "category": "unrelated",
    },
}


def download_video(key: str, config: dict) -> Path | None:
    """Download a single video, return cached path."""
    cache_path = CACHE_DIR / f"{key}.mp4"

    if cache_path.exists() and cache_path.stat().st_size > 1000:
        print(f"  [cached] {key}")
        return cache_path

    url = config["url"]
    print(f"  [downloading] {key}: {url}")

    cmd = [
        "yt-dlp",
        url,
        "-f", "bestvideo[height<=480][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=480]+bestaudio/best[height<=480]",
        "--merge-output-format", "mp4",
        "--recode-video", "mp4",
        # Limit to ~15 seconds
        "--download-sections", "*0:00-0:15",
        "-o", str(cache_path),
        "--no-playlist",
        "--quiet",
        "--no-warnings",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
        if cache_path.exists() and cache_path.stat().st_size > 1000:
            print(f"  [ok] {key} ({cache_path.stat().st_size // 1024} KB)")
            return cache_path
        else:
            print(f"  [failed] {key}: file too small or missing")
            return None
    except subprocess.CalledProcessError as e:
        print(f"  [failed] {key}: {e.stderr[:200] if e.stderr else 'unknown error'}")
        return None
    except subprocess.TimeoutExpired:
        print(f"  [failed] {key}: download timed out")
        return None


def download_all() -> dict:
    """Download all test videos and return manifest."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    manifest = {}
    success = 0
    failed = 0

    print(f"Downloading {len(TEST_VIDEOS)} test videos to {CACHE_DIR}/\n")

    for key, config in TEST_VIDEOS.items():
        path = download_video(key, config)
        if path:
            manifest[key] = {
                **config,
                "path": str(path),
            }
            success += 1
        else:
            failed += 1

    # Save manifest
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone: {success} downloaded, {failed} failed")
    print(f"Manifest: {MANIFEST_PATH}")

    return manifest


if __name__ == "__main__":
    manifest = download_all()
    if not manifest:
        print("ERROR: No videos downloaded. Check yt-dlp installation.")
        sys.exit(1)
