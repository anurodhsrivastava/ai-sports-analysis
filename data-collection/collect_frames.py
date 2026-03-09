"""
Data Collection Pipeline
Downloads sport videos and extracts the most dynamic frames for labeling.
Supports multiple sports via --sport flag.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np


URLS_DIR = Path(__file__).parent / "urls"
VIDEOS_DIR = Path(__file__).parent.parent / "videos"
LABELED_DIR = Path(__file__).parent.parent / "labeled-data"
NUM_FRAMES = 20

# Snow normalization is mainly useful for snow sports
SNOW_SPORTS = {"snowboard", "skiing"}


def download_video(url: str, output_dir: Path) -> Path | None:
    """Download a video at 1080p using yt-dlp."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "--merge-output-format", "mp4",
        "--recode-video", "mp4",
        "-o", output_template,
        url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if "Merging formats into" in line or "has already been downloaded" in line:
                path_str = line.split('"')[1] if '"' in line else None
                if path_str:
                    return Path(path_str)

        mp4s = sorted(output_dir.glob("*.mp4"), key=os.path.getmtime, reverse=True)
        return mp4s[0] if mp4s else None

    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url}: {e.stderr}")
        return None


def compute_frame_dynamics(video_path: Path) -> list[tuple[int, float]]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    scores: list[tuple[int, float]] = []
    prev_gray = None
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            score = float(np.mean(diff))
            scores.append((frame_idx, score))

        prev_gray = gray
        frame_idx += 1

    cap.release()
    return scores


def normalize_snow_brightness(frame: np.ndarray) -> np.ndarray:
    """Apply CLAHE on L-channel of LAB color space for snow normalization."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_normalized = clahe.apply(l_channel)
    lab_normalized = cv2.merge([l_normalized, a_channel, b_channel])
    return cv2.cvtColor(lab_normalized, cv2.COLOR_LAB2BGR)


def extract_top_frames(
    video_path: Path,
    output_dir: Path,
    sport: str,
    num_frames: int = NUM_FRAMES,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Computing frame dynamics for {video_path.name}...")
    scores = compute_frame_dynamics(video_path)

    if not scores:
        print("No frames found in video.")
        return []

    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = sorted([s[0] for s in scores[:num_frames]])

    print(f"Extracting {len(top_indices)} frames with highest motion...")

    cap = cv2.VideoCapture(str(video_path))
    saved_paths: list[Path] = []
    frame_idx = 0
    target_set = set(top_indices)
    use_snow_norm = sport in SNOW_SPORTS

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx in target_set:
            if use_snow_norm:
                frame = normalize_snow_brightness(frame)
            filename = f"frame_{frame_idx:06d}.png"
            save_path = output_dir / filename
            cv2.imwrite(str(save_path), frame)
            saved_paths.append(save_path)

        frame_idx += 1

    cap.release()
    return saved_paths


def process_urls(sport: str) -> None:
    urls_file = URLS_DIR / f"{sport}.txt"
    if not urls_file.exists():
        print(f"URLs file not found: {urls_file}")
        print(f"Create {urls_file} with one video URL per line.")
        sys.exit(1)

    urls = [
        line.strip()
        for line in urls_file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        print(f"No URLs found in {urls_file}. Add video URLs (one per line).")
        sys.exit(1)

    print(f"Processing {len(urls)} {sport} video(s)...")

    videos_dir = VIDEOS_DIR / sport

    for i, url in enumerate(urls, 1):
        print(f"\n{'=' * 60}")
        print(f"Video {i}/{len(urls)}: {url}")
        print(f"{'=' * 60}")

        video_path = download_video(url, videos_dir)
        if video_path is None:
            print(f"Skipping {url} - download failed")
            continue

        video_name = video_path.stem.replace(" ", "_")
        output_dir = LABELED_DIR / sport / video_name
        frames = extract_top_frames(video_path, output_dir, sport)
        print(f"Extracted {len(frames)} frames to {output_dir}")

    print("\nData collection complete!")


def main():
    parser = argparse.ArgumentParser(description="Collect frames for sport pose labeling")
    parser.add_argument("--sport", type=str, required=True, help="Sport name")
    args = parser.parse_args()
    process_urls(args.sport)


if __name__ == "__main__":
    main()
