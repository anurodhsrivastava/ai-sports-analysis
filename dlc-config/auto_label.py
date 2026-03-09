"""
Sport-Aware Auto-Labeling with MediaPipe Pose
Generates initial labels using MediaPipe, per-sport keypoint mapping.

Usage:
    python dlc-config/auto_label.py --sport snowboard              # Label all folders for sport
    python dlc-config/auto_label.py --sport running FOLDER_NAME    # Label one folder
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

LABELED_DATA_DIR = Path(__file__).parent.parent / "labeled-data"
CONFIGS_DIR = Path(__file__).parent.parent / "training" / "configs"

MP_LANDMARK = mp.solutions.pose.PoseLandmark

# MediaPipe mappings per sport
# Running and home workout use pure body pose (all keypoints auto-detected)
SPORT_MP_MAPPING = {
    "snowboard": {
        "head": [MP_LANDMARK.NOSE],
        "nose_shoulder": [MP_LANDMARK.LEFT_SHOULDER],
        "tail_shoulder": [MP_LANDMARK.RIGHT_SHOULDER],
        "center_hips": [MP_LANDMARK.LEFT_HIP, MP_LANDMARK.RIGHT_HIP],
        "front_knee": [MP_LANDMARK.LEFT_KNEE],
        "back_knee": [MP_LANDMARK.RIGHT_KNEE],
        "front_ankle": [MP_LANDMARK.LEFT_ANKLE],
        "back_ankle": [MP_LANDMARK.RIGHT_ANKLE],
        # board_nose and board_tail require manual labeling
    },
    "skiing": {
        "head": [MP_LANDMARK.NOSE],
        "left_shoulder": [MP_LANDMARK.LEFT_SHOULDER],
        "right_shoulder": [MP_LANDMARK.RIGHT_SHOULDER],
        "center_hips": [MP_LANDMARK.LEFT_HIP, MP_LANDMARK.RIGHT_HIP],
        "left_knee": [MP_LANDMARK.LEFT_KNEE],
        "right_knee": [MP_LANDMARK.RIGHT_KNEE],
        "left_ankle": [MP_LANDMARK.LEFT_ANKLE],
        "right_ankle": [MP_LANDMARK.RIGHT_ANKLE],
        # ski tips/tails and pole tips require manual labeling
    },
    "running": {
        "head": [MP_LANDMARK.NOSE],
        "neck": [MP_LANDMARK.LEFT_SHOULDER, MP_LANDMARK.RIGHT_SHOULDER],
        "shoulder": [MP_LANDMARK.LEFT_SHOULDER],
        "elbow": [MP_LANDMARK.LEFT_ELBOW],
        "wrist": [MP_LANDMARK.LEFT_WRIST],
        "hip": [MP_LANDMARK.LEFT_HIP],
        "knee": [MP_LANDMARK.LEFT_KNEE],
        "ankle": [MP_LANDMARK.LEFT_ANKLE],
        "toe": [MP_LANDMARK.LEFT_FOOT_INDEX],
        "heel": [MP_LANDMARK.LEFT_HEEL],
        "mid_torso": [MP_LANDMARK.LEFT_SHOULDER, MP_LANDMARK.LEFT_HIP],
        "pelvis": [MP_LANDMARK.LEFT_HIP, MP_LANDMARK.RIGHT_HIP],
    },
    "home_workout": {
        "head": [MP_LANDMARK.NOSE],
        "left_shoulder": [MP_LANDMARK.LEFT_SHOULDER],
        "right_shoulder": [MP_LANDMARK.RIGHT_SHOULDER],
        "left_elbow": [MP_LANDMARK.LEFT_ELBOW],
        "right_elbow": [MP_LANDMARK.RIGHT_ELBOW],
        "left_wrist": [MP_LANDMARK.LEFT_WRIST],
        "right_wrist": [MP_LANDMARK.RIGHT_WRIST],
        "left_hip": [MP_LANDMARK.LEFT_HIP],
        "right_hip": [MP_LANDMARK.RIGHT_HIP],
        "left_knee": [MP_LANDMARK.LEFT_KNEE],
        "right_knee": [MP_LANDMARK.RIGHT_KNEE],
        "left_ankle": [MP_LANDMARK.LEFT_ANKLE],
        "right_ankle": [MP_LANDMARK.RIGHT_ANKLE],
    },
}

MIN_CONFIDENCE = 0.5


def detect_pose(image_path: Path, mp_mapping: dict) -> dict[str, tuple[float, float]] | None:
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


def auto_label_folder(folder_path: Path, mp_mapping: dict, bodyparts: list[str]) -> dict:
    frame_paths = sorted(folder_path.glob("*.png"))
    if not frame_paths:
        return {"frames": 0, "detected": 0, "bodyparts_total": 0}

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

    save_labels(folder_path, frame_names, all_labels, bodyparts)

    return {
        "frames": len(frame_paths),
        "detected": detected_count,
        "bodyparts_total": total_bodyparts,
        "avg_bodyparts": total_bodyparts / detected_count if detected_count else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Auto-label frames with MediaPipe")
    parser.add_argument("--sport", type=str, required=True, help="Sport name")
    parser.add_argument("folder", nargs="?", default=None, help="Optional specific folder name")
    args = parser.parse_args()

    if args.sport not in SPORT_MP_MAPPING:
        print(f"Unknown sport: {args.sport}. Available: {list(SPORT_MP_MAPPING.keys())}")
        sys.exit(1)

    mp_mapping = SPORT_MP_MAPPING[args.sport]

    # Load bodyparts from config
    config_path = CONFIGS_DIR / f"{args.sport}.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
        bodyparts = config["bodyparts"]
    else:
        bodyparts = list(mp_mapping.keys())

    sport_dir = LABELED_DATA_DIR / args.sport
    if not sport_dir.exists():
        sport_dir = LABELED_DATA_DIR

    if args.folder:
        folders = [sport_dir / args.folder]
        if not folders[0].exists():
            print(f"Folder not found: {folders[0]}")
            sys.exit(1)
    else:
        folders = sorted(d for d in sport_dir.iterdir() if d.is_dir())

    auto_detected = [bp for bp in bodyparts if bp in mp_mapping]
    manual_needed = [bp for bp in bodyparts if bp not in mp_mapping]

    print(f"Auto-labeling {len(folders)} folder(s) for {args.sport} with MediaPipe Pose...")
    print(f"Auto-detected: {', '.join(auto_detected)} ({len(auto_detected)}/{len(bodyparts)})")
    if manual_needed:
        print(f"Manual labeling needed: {', '.join(manual_needed)}\n")

    total_frames = 0
    total_detected = 0

    for folder in folders:
        print(f"Processing: {folder.name}...")
        stats = auto_label_folder(folder, mp_mapping, bodyparts)
        total_frames += stats["frames"]
        total_detected += stats["detected"]
        print(
            f"  {stats['detected']}/{stats['frames']} frames detected, "
            f"avg {stats['avg_bodyparts']:.1f} bodyparts/frame"
        )

    print(f"\nDone! {total_detected}/{total_frames} frames auto-labeled.")


if __name__ == "__main__":
    main()
