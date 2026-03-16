"""
Auto-Labeling with MediaPipe Pose
Generates initial keypoint labels using MediaPipe.
Sport-aware: uses correct bodypart names and mappings per sport.

Usage:
    python dlc-config/auto_label.py --sport snowboard   # Label snowboard
    python dlc-config/auto_label.py --sport skiing       # Label skiing
    python dlc-config/auto_label.py --sport all          # Label all sports
    python dlc-config/auto_label.py FOLDER_NAME          # Label one folder (legacy)
"""

import csv
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

LABELED_DATA_DIR = Path(__file__).parent.parent / "labeled-data"

# MediaPipe Pose landmark indices
# https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
MP_LANDMARK = mp.solutions.pose.PoseLandmark

# Minimum confidence to accept a landmark
MIN_CONFIDENCE = 0.5

# ── Per-sport configurations ──────────────────────────────────────────

SPORT_CONFIGS = {
    "snowboard": {
        "bodyparts": [
            "head", "nose_shoulder", "tail_shoulder", "center_hips",
            "front_knee", "back_knee", "front_ankle", "back_ankle",
            "board_nose", "board_tail",
        ],
        "mp_mapping": {
            "head": [MP_LANDMARK.NOSE],
            "nose_shoulder": [MP_LANDMARK.LEFT_SHOULDER],
            "tail_shoulder": [MP_LANDMARK.RIGHT_SHOULDER],
            "center_hips": [MP_LANDMARK.LEFT_HIP, MP_LANDMARK.RIGHT_HIP],
            "front_knee": [MP_LANDMARK.LEFT_KNEE],
            "back_knee": [MP_LANDMARK.RIGHT_KNEE],
            "front_ankle": [MP_LANDMARK.LEFT_ANKLE],
            "back_ankle": [MP_LANDMARK.RIGHT_ANKLE],
        },
        # board_nose, board_tail handled by auto_label_board.py
    },
    "skiing": {
        "bodyparts": [
            "head", "left_shoulder", "right_shoulder", "center_hips",
            "left_knee", "right_knee", "left_ankle", "right_ankle",
            "left_ski_tip", "left_ski_tail", "right_ski_tip", "right_ski_tail",
            "left_pole_tip", "right_pole_tip",
        ],
        "mp_mapping": {
            "head": [MP_LANDMARK.NOSE],
            "left_shoulder": [MP_LANDMARK.LEFT_SHOULDER],
            "right_shoulder": [MP_LANDMARK.RIGHT_SHOULDER],
            "center_hips": [MP_LANDMARK.LEFT_HIP, MP_LANDMARK.RIGHT_HIP],
            "left_knee": [MP_LANDMARK.LEFT_KNEE],
            "right_knee": [MP_LANDMARK.RIGHT_KNEE],
            "left_ankle": [MP_LANDMARK.LEFT_ANKLE],
            "right_ankle": [MP_LANDMARK.RIGHT_ANKLE],
            "left_pole_tip": [MP_LANDMARK.LEFT_WRIST],
            "right_pole_tip": [MP_LANDMARK.RIGHT_WRIST],
        },
        # ski tips/tails handled by auto_label_board.py
    },
}

# Default to snowboard for legacy usage
DEFAULT_SPORT = "snowboard"


def get_sport_config(sport: str | None) -> dict:
    """Get sport config, defaulting to snowboard."""
    s = sport or DEFAULT_SPORT
    if s not in SPORT_CONFIGS:
        print(f"WARNING: No config for sport '{s}', using snowboard defaults")
        s = DEFAULT_SPORT
    return SPORT_CONFIGS[s]


def detect_pose(image_path: Path, mp_mapping: dict) -> dict[str, tuple[float, float]] | None:
    """
    Run MediaPipe Pose on a single image.
    Returns dict of {bodypart: (x_pixel, y_pixel)} or None if no pose detected.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None

    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    with mp.solutions.pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        min_detection_confidence=0.5,
    ) as pose:
        results = pose.process(rgb)

    if not results.pose_landmarks:
        return None

    landmarks = results.pose_landmarks.landmark
    labels = {}

    for bodypart, mp_indices in mp_mapping.items():
        points = []
        all_visible = True

        for idx in mp_indices:
            lm = landmarks[idx]
            if lm.visibility < MIN_CONFIDENCE:
                all_visible = False
                break
            points.append((lm.x * w, lm.y * h))

        if all_visible and points:
            x = sum(p[0] for p in points) / len(points)
            y = sum(p[1] for p in points) / len(points)
            labels[bodypart] = (round(x, 1), round(y, 1))

    return labels if labels else None


def save_labels(folder_path: Path, frame_names: list[str], all_labels: dict, bodyparts: list[str]):
    """Save labels in DLC-compatible CSV format."""
    csv_path = folder_path / "labels.csv"

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)

        scorer_row = ["scorer"] + ["coach"] * (len(bodyparts) * 2)
        bodyparts_row = ["bodyparts"]
        coords_row = ["coords"]
        for bp in bodyparts:
            bodyparts_row.extend([bp, bp])
            coords_row.extend(["x", "y"])

        writer.writerow(scorer_row)
        writer.writerow(bodyparts_row)
        writer.writerow(coords_row)

        for frame_name in frame_names:
            row = [frame_name]
            frame_labels = all_labels.get(frame_name, {})
            for bp in bodyparts:
                if bp in frame_labels:
                    x, y = frame_labels[bp]
                    row.extend([f"{x:.1f}", f"{y:.1f}"])
                else:
                    row.extend(["", ""])
            writer.writerow(row)

    return csv_path


def auto_label_folder(folder_path: Path, sport_config: dict) -> dict:
    """Auto-label all frames in a folder. Returns stats."""
    frame_paths = sorted(folder_path.glob("*.png"))
    if not frame_paths:
        return {"frames": 0, "detected": 0, "bodyparts_total": 0}

    mp_mapping = sport_config["mp_mapping"]
    bodyparts = sport_config["bodyparts"]

    frame_names = [p.name for p in frame_paths]
    all_labels: dict[str, dict[str, tuple[float, float]]] = {}
    detected_count = 0
    total_bodyparts = 0

    for frame_path in frame_paths:
        labels = detect_pose(frame_path, mp_mapping)
        if labels:
            all_labels[frame_path.name] = labels
            detected_count += 1
            total_bodyparts += len(labels)

    csv_path = save_labels(folder_path, frame_names, all_labels, bodyparts)

    return {
        "frames": len(frame_paths),
        "detected": detected_count,
        "bodyparts_total": total_bodyparts,
        "avg_bodyparts": total_bodyparts / detected_count if detected_count else 0,
        "csv_path": csv_path,
    }


ALL_SPORTS = ["snowboard", "skiing"]


def _find_label_folders(sport: str | None = None) -> list[Path]:
    """Find all frame folders to label, respecting sport directory layout."""
    folders = []

    if sport and sport != "all":
        sport_dir = LABELED_DATA_DIR / sport
        if sport_dir.exists():
            folders = sorted(
                d for d in sport_dir.iterdir()
                if d.is_dir() and list(d.glob("*.png"))
            )
    elif sport == "all":
        for s in ALL_SPORTS:
            sport_dir = LABELED_DATA_DIR / s
            if sport_dir.exists():
                folders.extend(
                    sorted(d for d in sport_dir.iterdir()
                           if d.is_dir() and list(d.glob("*.png")))
                )
        for d in sorted(LABELED_DATA_DIR.iterdir()):
            if d.is_dir() and d.name not in ALL_SPORTS and list(d.glob("*.png")):
                folders.append(d)
    else:
        folders = sorted(
            d for d in LABELED_DATA_DIR.iterdir()
            if d.is_dir() and list(d.glob("*.png"))
        )

    return folders


def _detect_sport(folders: list[Path], explicit_sport: str | None) -> str:
    """Detect sport from folder path or explicit argument."""
    if explicit_sport and explicit_sport != "all":
        return explicit_sport
    if folders:
        for sport in ALL_SPORTS:
            if sport in str(folders[0]):
                return sport
    return DEFAULT_SPORT


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto-label frames with MediaPipe Pose")
    parser.add_argument("folder", nargs="?", default=None,
                        help="Specific folder name to label (legacy mode)")
    parser.add_argument("--sport", type=str, default=None,
                        help="Sport to label (searches labeled-data/{sport}/)")
    args = parser.parse_args()

    if args.folder:
        folders = [LABELED_DATA_DIR / args.folder]
        if not folders[0].exists():
            print(f"Folder not found: {folders[0]}")
            sys.exit(1)
    else:
        folders = _find_label_folders(args.sport)

    if not folders:
        print("No folders found with frames to label.")
        print("Run data collection first: python data-collection/collect_frames.py --sport <sport>")
        sys.exit(1)

    sport_label = args.sport or "all"

    # For "all" mode, process each sport separately with its own config
    if sport_label == "all":
        sports_to_process = ALL_SPORTS
    else:
        sports_to_process = [sport_label]

    total_frames = 0
    total_detected = 0

    for sport in sports_to_process:
        config = get_sport_config(sport)
        mp_mapping = config["mp_mapping"]
        sport_folders = [f for f in folders if sport in str(f)]

        if not sport_folders:
            continue

        auto_bps = list(mp_mapping.keys())
        print(f"Auto-labeling {len(sport_folders)} folder(s) for {sport} with MediaPipe Pose...")
        print(f"Bodyparts auto-detected: {', '.join(auto_bps)} ({len(auto_bps)}/{len(config['bodyparts'])})")
        remaining = [bp for bp in config["bodyparts"] if bp not in mp_mapping]
        if remaining:
            print(f"Deferred to board labeler: {', '.join(remaining)}\n")

        for folder in sport_folders:
            print(f"Processing: {folder.relative_to(LABELED_DATA_DIR)}...")
            stats = auto_label_folder(folder, config)
            total_frames += stats["frames"]
            total_detected += stats["detected"]
            print(
                f"  {stats['detected']}/{stats['frames']} frames detected, "
                f"avg {stats['avg_bodyparts']:.1f} bodyparts/frame"
            )

    print(f"\nDone! {total_detected}/{total_frames} frames auto-labeled.")
    print(f"\nNext steps:")
    print(f"  1. Auto-label board/skis: python dlc-config/auto_label_board.py --sport {sport_label}")
    print(f"  2. Manual refinement: python dlc-config/label_frames.py --sport {sport_label}")
    print(f"  3. Train model:       python training/train.py --sport {sport_label}")


if __name__ == "__main__":
    main()
