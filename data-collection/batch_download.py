"""
Parallel batch downloader for remaining videos.
Downloads in small batches with delays between batches to avoid YouTube rate limits.

Usage:
    python data-collection/batch_download.py --sport snowboard --workers 3 --batch-pause 60
"""

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np

URLS_DIR = Path(__file__).parent / "urls"
VIDEOS_DIR = Path(__file__).parent.parent / "videos"
LABELED_DIR = Path(__file__).parent.parent / "labeled-data"
NUM_FRAMES = 20
SNOW_SPORTS = {"snowboard", "skiing"}


def _get_existing_video_ids(videos_dir: Path) -> set[str]:
    """Get YouTube video IDs already downloaded by checking filenames + yt-dlp archive."""
    ids = set()
    archive = videos_dir / ".downloaded_ids.txt"
    if archive.exists():
        for line in archive.read_text().splitlines():
            line = line.strip()
            if line:
                ids.add(line)
    return ids


def _record_downloaded(videos_dir: Path, video_id: str):
    archive = videos_dir / ".downloaded_ids.txt"
    with open(archive, "a") as f:
        f.write(video_id + "\n")


def _extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    if "v=" in url:
        vid = url.split("v=")[1].split("&")[0]
        return vid
    return url.rsplit("/", 1)[-1]


def download_one(url: str, output_dir: Path) -> tuple[str, Path | None, str]:
    """Download a single video. Returns (url, path_or_none, status)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "--recode-video", "mp4",
        "--cookies-from-browser", "chrome",
        "--js-runtimes", "node",
        "-o", template,
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
        for line in result.stdout.splitlines():
            if "Merging formats into" in line or "has already been downloaded" in line:
                path_str = line.split('"')[1] if '"' in line else None
                if path_str:
                    return url, Path(path_str), "ok"

        mp4s = sorted(output_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True)
        if mp4s:
            return url, mp4s[0], "ok"
        return url, None, "no_output"

    except subprocess.CalledProcessError as e:
        if "Sign in to confirm" in (e.stderr or ""):
            return url, None, "bot_blocked"
        return url, None, f"error: {(e.stderr or '')[:100]}"
    except subprocess.TimeoutExpired:
        return url, None, "timeout"


def normalize_snow_brightness(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_norm = clahe.apply(l_ch)
    return cv2.cvtColor(cv2.merge([l_norm, a_ch, b_ch]), cv2.COLOR_LAB2BGR)


def extract_frames(video_path: Path, output_dir: Path, sport: str):
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return 0

    prev_gray = None
    scores = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (5, 5), 0)
        if prev_gray is not None:
            scores.append((idx, float(np.mean(cv2.absdiff(prev_gray, gray)))))
        prev_gray = gray
        idx += 1

    if not scores:
        cap.release()
        return 0

    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = set(s[0] for s in scores[:NUM_FRAMES])

    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    use_snow = sport in SNOW_SPORTS
    saved = 0
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx in top_indices:
            if use_snow:
                frame = normalize_snow_brightness(frame)
            cv2.imwrite(str(output_dir / f"frame_{idx:06d}.png"), frame)
            saved += 1
        idx += 1

    cap.release()
    return saved


def main():
    parser = argparse.ArgumentParser(description="Parallel batch video downloader")
    parser.add_argument("--sport", required=True)
    parser.add_argument("--workers", type=int, default=3, help="Parallel downloads per batch")
    parser.add_argument("--batch-size", type=int, default=5, help="Videos per batch")
    parser.add_argument("--batch-pause", type=int, default=45, help="Seconds between batches")
    parser.add_argument("--max-consecutive-blocks", type=int, default=10,
                        help="Stop after N consecutive bot blocks")
    args = parser.parse_args()

    urls_file = URLS_DIR / f"{args.sport}.txt"
    urls = [l.strip() for l in urls_file.read_text().splitlines()
            if l.strip() and not l.strip().startswith("#")]

    videos_dir = VIDEOS_DIR / args.sport
    videos_dir.mkdir(parents=True, exist_ok=True)

    # Load already-downloaded IDs
    done_ids = _get_existing_video_ids(videos_dir)
    # Also check labeled dirs
    existing_labels = set()
    label_dir = LABELED_DIR / args.sport
    if label_dir.exists():
        existing_labels = {d.name for d in label_dir.iterdir() if d.is_dir() and list(d.glob("*.png"))}

    # Filter to remaining URLs
    remaining = []
    for url in urls:
        vid = _extract_video_id(url)
        if vid not in done_ids:
            remaining.append(url)

    print(f"Total URLs: {len(urls)}, Already done: {len(done_ids)}, Remaining: {len(remaining)}")
    print(f"Workers: {args.workers}, Batch: {args.batch_size}, Pause: {args.batch_pause}s")
    print(f"Will stop after {args.max_consecutive_blocks} consecutive bot blocks\n")

    total_new = 0
    total_failed = 0
    consecutive_blocks = 0

    for batch_start in range(0, len(remaining), args.batch_size):
        batch = remaining[batch_start:batch_start + args.batch_size]
        batch_num = batch_start // args.batch_size + 1
        total_batches = (len(remaining) + args.batch_size - 1) // args.batch_size

        print(f"\n{'='*60}")
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} videos)")
        print(f"Progress: {total_new} downloaded, {total_failed} failed")
        print(f"{'='*60}")

        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(download_one, url, videos_dir): url for url in batch}

            for future in as_completed(futures):
                url, video_path, status = future.result()
                vid = _extract_video_id(url)

                if status == "ok" and video_path:
                    _record_downloaded(videos_dir, vid)
                    consecutive_blocks = 0

                    # Extract frames
                    video_name = video_path.stem.replace(" ", "_")
                    if video_name not in existing_labels:
                        out_dir = LABELED_DIR / args.sport / video_name
                        n = extract_frames(video_path, out_dir, args.sport)
                        print(f"  OK: {video_path.name} -> {n} frames")
                    else:
                        print(f"  OK: {video_path.name} (already labeled)")
                    total_new += 1

                elif status == "bot_blocked":
                    _record_downloaded(videos_dir, vid)  # don't retry blocked ones
                    consecutive_blocks += 1
                    total_failed += 1
                    print(f"  BLOCKED: {vid}")
                else:
                    _record_downloaded(videos_dir, vid)
                    total_failed += 1
                    print(f"  FAILED: {vid} ({status})")

        if consecutive_blocks >= args.max_consecutive_blocks:
            print(f"\n{args.max_consecutive_blocks} consecutive blocks - pausing 5 min...")
            consecutive_blocks = 0
            time.sleep(300)

        if batch_start + args.batch_size < len(remaining):
            print(f"Pausing {args.batch_pause}s before next batch...")
            time.sleep(args.batch_pause)

    print(f"\n{'='*60}")
    print(f"Done! Downloaded: {total_new}, Failed: {total_failed}")
    total_videos = len(list(videos_dir.glob("*.mp4")))
    total_labels = len(list((LABELED_DIR / args.sport).iterdir())) if (LABELED_DIR / args.sport).exists() else 0
    print(f"Total videos: {total_videos}, Total labeled: {total_labels}")


if __name__ == "__main__":
    main()
