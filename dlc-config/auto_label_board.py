"""
Auto-Label Board/Ski Endpoints
Sport-aware: detects snowboard (board_nose/board_tail) or
skis (left_ski_tip/tail, right_ski_tip/tail) using ankle positions + CV.

Usage:
    python dlc-config/auto_label_board.py --sport snowboard
    python dlc-config/auto_label_board.py --sport skiing
    python dlc-config/auto_label_board.py FOLDER_NAME
"""

import csv
import sys
from pathlib import Path

import cv2
import numpy as np

LABELED_DATA_DIR = Path(__file__).parent.parent / "labeled-data"

# ── Per-sport configurations ──────────────────────────────────────────

SPORT_CONFIGS = {
    "snowboard": {
        "bodyparts": [
            "head", "nose_shoulder", "tail_shoulder", "center_hips",
            "front_knee", "back_knee", "front_ankle", "back_ankle",
            "board_nose", "board_tail",
        ],
        # ankle keys -> endpoint keys
        "equipment_mappings": [
            {
                "ankle_keys": ("front_ankle", "back_ankle"),
                "endpoint_keys": ("board_nose", "board_tail"),
            },
        ],
    },
    "skiing": {
        "bodyparts": [
            "head", "left_shoulder", "right_shoulder", "center_hips",
            "left_knee", "right_knee", "left_ankle", "right_ankle",
            "left_ski_tip", "left_ski_tail", "right_ski_tip", "right_ski_tail",
            "left_pole_tip", "right_pole_tip",
        ],
        # Each ski is detected independently from its corresponding ankle
        "equipment_mappings": [
            {
                "ankle_keys": ("left_ankle",),
                "endpoint_keys": ("left_ski_tip", "left_ski_tail"),
            },
            {
                "ankle_keys": ("right_ankle",),
                "endpoint_keys": ("right_ski_tip", "right_ski_tail"),
            },
        ],
    },
}

DEFAULT_SPORT = "snowboard"

# How far beyond ankles to search for board/ski endpoints (pixels)
SEARCH_EXTENSION = 200
# For skis, search further since they extend more from the foot
SKI_SEARCH_EXTENSION = 300
# Minimum contour area to consider as board/ski
MIN_BOARD_AREA = 500
MIN_SKI_AREA = 200


def load_labels(folder_path: Path) -> tuple[list[str], dict]:
    """Load existing labels from CSV."""
    csv_path = folder_path / "labels.csv"
    if not csv_path.exists():
        return [], {}

    with open(csv_path) as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) < 4:
        return [], {}

    bp_row = rows[1][1:]
    labels = {}
    frame_names = []

    for data_row in rows[3:]:
        fname = data_row[0]
        frame_names.append(fname)
        labels[fname] = {}
        for j in range(0, len(bp_row), 2):
            bp = bp_row[j]
            x_val = data_row[j + 1] if j + 1 < len(data_row) else ""
            y_val = data_row[j + 2] if j + 2 < len(data_row) else ""
            if x_val and y_val:
                labels[fname][bp] = (float(x_val), float(y_val))

    return frame_names, labels


def save_labels_sport(folder_path: Path, frame_names: list[str], all_labels: dict, bodyparts: list[str]):
    """Save labels in DLC-compatible CSV format with sport-specific bodyparts."""
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


def detect_board_endpoints(
    image: np.ndarray,
    front_ankle: tuple[float, float],
    back_ankle: tuple[float, float],
) -> tuple[tuple[float, float] | None, tuple[float, float] | None]:
    """
    Detect board nose and tail using ankle positions and CV.

    Strategy:
    1. Compute board axis direction from ankle positions
    2. Create a search region along and beyond the ankle line
    3. Threshold for dark pixels (board is darker than snow)
    4. Find board contour near ankles
    5. Project contour points onto board axis to find extremes
    """
    h, w = image.shape[:2]
    fa = np.array(front_ankle)
    ba = np.array(back_ankle)

    # Board axis direction (front ankle → back ankle)
    board_vec = ba - fa
    board_len = np.linalg.norm(board_vec)
    if board_len < 10:
        return None, None

    board_dir = board_vec / board_len
    board_perp = np.array([-board_dir[1], board_dir[0]])

    # Midpoint of ankles
    mid = (fa + ba) / 2

    # Define search region: a rotated rectangle around the ankle line, extended
    half_length = board_len / 2 + SEARCH_EXTENSION
    half_width = 80  # pixels perpendicular to board

    # Create mask for the search region
    corners = np.array([
        mid - board_dir * half_length - board_perp * half_width,
        mid + board_dir * half_length - board_perp * half_width,
        mid + board_dir * half_length + board_perp * half_width,
        mid - board_dir * half_length + board_perp * half_width,
    ], dtype=np.int32)

    region_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(region_mask, [corners], 255)

    # Convert to grayscale and threshold for dark objects (board)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adaptive approach: the board is darker than surrounding snow
    # Use local mean in the search region
    masked_gray = cv2.bitwise_and(gray, gray, mask=region_mask)
    region_pixels = gray[region_mask > 0]

    if len(region_pixels) == 0:
        return None, None

    # Board is typically in the darker portion of the region
    threshold = np.percentile(region_pixels, 35)
    board_mask = cv2.inRange(gray, 0, int(threshold))
    board_mask = cv2.bitwise_and(board_mask, region_mask)

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    board_mask = cv2.morphologyEx(board_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    board_mask = cv2.morphologyEx(board_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(board_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, None

    # Find the contour closest to the ankle midpoint and large enough
    best_contour = None
    best_score = float("inf")

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_BOARD_AREA:
            continue

        # Score: distance from contour centroid to ankle midpoint
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        dist = np.linalg.norm(np.array([cx, cy]) - mid)

        # Prefer larger contours closer to ankles
        score = dist - area * 0.01
        if score < best_score:
            best_score = score
            best_contour = cnt

    if best_contour is None:
        # Fallback: extrapolate from ankles
        nose = fa - board_dir * board_len * 0.4
        tail = ba + board_dir * board_len * 0.4
        nose = np.clip(nose, [0, 0], [w - 1, h - 1])
        tail = np.clip(tail, [0, 0], [w - 1, h - 1])
        return tuple(nose.round(1)), tuple(tail.round(1))

    # Project all contour points onto the board axis
    pts = best_contour.reshape(-1, 2).astype(float)
    projections = np.dot(pts - mid, board_dir)

    min_idx = np.argmin(projections)
    max_idx = np.argmax(projections)

    # The endpoint closer to front_ankle is board_nose
    pt_min = pts[min_idx]
    pt_max = pts[max_idx]

    # Determine which end is nose vs tail based on proximity to ankles
    dist_min_to_front = np.linalg.norm(pt_min - fa)
    dist_max_to_front = np.linalg.norm(pt_max - fa)

    if dist_min_to_front < dist_max_to_front:
        board_nose = tuple(pt_min.round(1))
        board_tail = tuple(pt_max.round(1))
    else:
        board_nose = tuple(pt_max.round(1))
        board_tail = tuple(pt_min.round(1))

    return board_nose, board_tail


def detect_ski_endpoints(
    image: np.ndarray,
    ankle: tuple[float, float],
    center_hips: tuple[float, float] | None = None,
) -> tuple[tuple[float, float] | None, tuple[float, float] | None]:
    """
    Detect ski tip and tail from a single ankle position.

    Strategy:
    1. Estimate ski direction from ankle position (skis point roughly downhill)
    2. Use hip-to-ankle vector if available, otherwise assume vertical
    3. Search along that axis for dark elongated objects
    4. Find the extreme points as ski tip (front) and tail (back)
    """
    h, w = image.shape[:2]
    ankle_pt = np.array(ankle)

    # Estimate ski direction: if we have hips, ski roughly extends
    # perpendicular to the leg in the plane, but mostly forward/backward.
    # Use a vertical-ish default direction (skis point downhill)
    if center_hips is not None:
        hip_pt = np.array(center_hips)
        leg_vec = ankle_pt - hip_pt
        leg_len = np.linalg.norm(leg_vec)
        if leg_len > 10:
            # Ski direction is roughly perpendicular to the leg in the image plane,
            # but we use a blend of leg direction and horizontal
            leg_dir = leg_vec / leg_len
            # Ski typically extends more horizontally than vertically
            ski_dir = np.array([1.0, leg_dir[1] * 0.3])
            ski_dir = ski_dir / np.linalg.norm(ski_dir)
        else:
            ski_dir = np.array([1.0, 0.0])
    else:
        ski_dir = np.array([1.0, 0.0])

    ski_perp = np.array([-ski_dir[1], ski_dir[0]])

    # Search region around the ankle
    half_length = SKI_SEARCH_EXTENSION
    half_width = 60

    corners = np.array([
        ankle_pt - ski_dir * half_length - ski_perp * half_width,
        ankle_pt + ski_dir * half_length - ski_perp * half_width,
        ankle_pt + ski_dir * half_length + ski_perp * half_width,
        ankle_pt - ski_dir * half_length + ski_perp * half_width,
    ], dtype=np.int32)

    region_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(region_mask, [corners], 255)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    region_pixels = gray[region_mask > 0]

    if len(region_pixels) == 0:
        return None, None

    # Skis are typically darker than snow
    threshold = np.percentile(region_pixels, 30)
    ski_mask = cv2.inRange(gray, 0, int(threshold))
    ski_mask = cv2.bitwise_and(ski_mask, region_mask)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    ski_mask = cv2.morphologyEx(ski_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    ski_mask = cv2.morphologyEx(ski_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(ski_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # Fallback: extrapolate from ankle
        tip = ankle_pt + ski_dir * 120
        tail = ankle_pt - ski_dir * 80
        tip = np.clip(tip, [0, 0], [w - 1, h - 1])
        tail = np.clip(tail, [0, 0], [w - 1, h - 1])
        return tuple(tip.round(1)), tuple(tail.round(1))

    # Find elongated contour closest to ankle
    best_contour = None
    best_score = float("inf")

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_SKI_AREA:
            continue

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        dist = np.linalg.norm(np.array([cx, cy]) - ankle_pt)

        # Prefer elongated contours (skis are long and thin)
        _, (mw, mh), _ = cv2.minAreaRect(cnt)
        aspect = max(mw, mh) / (min(mw, mh) + 1e-6)

        # Score: close to ankle, elongated, large
        score = dist - area * 0.005 - aspect * 10
        if score < best_score:
            best_score = score
            best_contour = cnt

    if best_contour is None:
        tip = ankle_pt + ski_dir * 120
        tail = ankle_pt - ski_dir * 80
        tip = np.clip(tip, [0, 0], [w - 1, h - 1])
        tail = np.clip(tail, [0, 0], [w - 1, h - 1])
        return tuple(tip.round(1)), tuple(tail.round(1))

    # Project contour points onto ski axis
    pts = best_contour.reshape(-1, 2).astype(float)
    projections = np.dot(pts - ankle_pt, ski_dir)

    min_idx = np.argmin(projections)
    max_idx = np.argmax(projections)

    # Tip is the forward end (positive projection), tail is behind
    ski_tip = tuple(pts[max_idx].round(1))
    ski_tail = tuple(pts[min_idx].round(1))

    return ski_tip, ski_tail


def process_folder(folder_path: Path, sport: str = DEFAULT_SPORT) -> dict:
    """Auto-label equipment endpoints for all frames in a folder."""
    config = SPORT_CONFIGS.get(sport, SPORT_CONFIGS[DEFAULT_SPORT])
    bodyparts = config["bodyparts"]
    mappings = config["equipment_mappings"]

    frame_names, labels = load_labels(folder_path)

    if not frame_names:
        return {"frames": 0, "labeled": 0, "skipped_no_ankles": 0}

    labeled_count = 0
    skipped_no_ankles = 0

    for fname in frame_names:
        frame_labels = labels.get(fname, {})
        frame_had_label = False

        for mapping in mappings:
            ankle_keys = mapping["ankle_keys"]
            endpoint_keys = mapping["endpoint_keys"]

            # Check if required ankles are present
            if not all(k in frame_labels for k in ankle_keys):
                skipped_no_ankles += 1
                continue

            img_path = folder_path / fname
            if not img_path.exists():
                continue

            img = cv2.imread(str(img_path))
            if img is None:
                continue

            if sport == "skiing":
                # Single ankle -> ski detection
                ankle = frame_labels[ankle_keys[0]]
                hips = frame_labels.get("center_hips")
                tip, tail = detect_ski_endpoints(img, ankle, hips)
            else:
                # Two ankles -> board detection
                front_ankle = frame_labels[ankle_keys[0]]
                back_ankle = frame_labels[ankle_keys[1]]
                tip, tail = detect_board_endpoints(img, front_ankle, back_ankle)

            if tip is not None:
                frame_labels[endpoint_keys[0]] = tip
            if tail is not None:
                frame_labels[endpoint_keys[1]] = tail

            if tip and tail:
                frame_had_label = True

        labels[fname] = frame_labels
        if frame_had_label:
            labeled_count += 1

    save_labels_sport(folder_path, frame_names, labels, bodyparts)

    return {
        "frames": len(frame_names),
        "labeled": labeled_count,
        "skipped_no_ankles": skipped_no_ankles,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Auto-label board endpoints")
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
    elif args.sport:
        sport_dir = LABELED_DATA_DIR / args.sport
        if not sport_dir.exists():
            print(f"Sport directory not found: {sport_dir}")
            sys.exit(1)
        folders = sorted(
            d for d in sport_dir.iterdir()
            if d.is_dir() and (d / "labels.csv").exists()
        )
    else:
        folders = sorted(d for d in LABELED_DATA_DIR.iterdir() if d.is_dir())

    sport = args.sport or DEFAULT_SPORT
    equip_name = "ski endpoints" if sport == "skiing" else "board endpoints"

    print(f"Auto-labeling {equip_name} for {len(folders)} folder(s) ({sport})...")
    print("Using ankle positions + dark-object detection\n")

    total_frames = 0
    total_labeled = 0
    total_skipped = 0

    for folder in folders:
        print(f"Processing: {folder.name}...")
        stats = process_folder(folder, sport=sport)
        total_frames += stats["frames"]
        total_labeled += stats["labeled"]
        total_skipped += stats["skipped_no_ankles"]
        print(
            f"  {stats['labeled']}/{stats['frames']} {equip_name} detected"
            f" ({stats['skipped_no_ankles']} skipped - no ankles)"
        )

    print(f"\nDone! {total_labeled}/{total_frames} frames have {equip_name}.")
    print(f"Skipped {total_skipped} frames (missing ankle keypoints).")
    print(f"\nNext: open in napari to review and correct:")
    print(f"  python3 dlc-config/label_frames.py <folder>")


if __name__ == "__main__":
    main()
