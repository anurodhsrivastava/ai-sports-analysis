"""
Napari-based Frame Labeling Tool for DLC
Labels 10 snowboard bodyparts on extracted frames and saves
annotations in DLC-compatible CSV format.

Usage:
    python dlc-config/label_frames.py [video_folder_name]

If no folder name is given, lists available folders to label.
"""

import csv
import sys
from pathlib import Path

import napari
import numpy as np
from skimage import io


PROJECT_DIR = Path(__file__).parent.parent / "dlc-project"
LABELED_DATA_DIR = Path(__file__).parent.parent / "labeled-data"

BODYPARTS = [
    "head",
    "nose_shoulder",
    "tail_shoulder",
    "center_hips",
    "front_knee",
    "back_knee",
    "front_ankle",
    "back_ankle",
    "board_nose",
    "board_tail",
]

COLORS = {
    "head": "yellow",
    "nose_shoulder": "cyan",
    "tail_shoulder": "cyan",
    "center_hips": "green",
    "front_knee": "orange",
    "back_knee": "magenta",
    "front_ankle": "orange",
    "back_ankle": "magenta",
    "board_nose": "blue",
    "board_tail": "blue",
}


def list_folders():
    """List available frame folders."""
    folders = sorted(d.name for d in LABELED_DATA_DIR.iterdir() if d.is_dir())
    print(f"\nAvailable folders ({len(folders)}):")
    for i, f in enumerate(folders, 1):
        csv_path = LABELED_DATA_DIR / f / "labels.csv"
        status = " [labeled]" if csv_path.exists() else ""
        print(f"  {i}. {f}{status}")
    return folders


def load_frames(folder_path: Path) -> tuple[list[np.ndarray], list[str]]:
    """Load all PNG frames from a folder."""
    frame_paths = sorted(folder_path.glob("*.png"))
    frames = [io.imread(str(p)) for p in frame_paths]
    names = [p.name for p in frame_paths]
    return frames, names


def save_labels(folder_path: Path, frame_names: list[str], labels: dict):
    """
    Save labels to DLC-compatible CSV format.
    labels: {frame_name: {bodypart: (x, y)}}
    """
    csv_path = folder_path / "labels.csv"

    # DLC format: scorer, bodyparts header rows, then data
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)

        # Header rows
        scorer_row = ["scorer"] + ["coach"] * (len(BODYPARTS) * 2)
        bodyparts_row = ["bodyparts"]
        coords_row = ["coords"]
        for bp in BODYPARTS:
            bodyparts_row.extend([bp, bp])
            coords_row.extend(["x", "y"])

        writer.writerow(scorer_row)
        writer.writerow(bodyparts_row)
        writer.writerow(coords_row)

        # Data rows
        for frame_name in frame_names:
            row = [frame_name]
            frame_labels = labels.get(frame_name, {})
            for bp in BODYPARTS:
                if bp in frame_labels:
                    x, y = frame_labels[bp]
                    row.extend([f"{x:.1f}", f"{y:.1f}"])
                else:
                    row.extend(["", ""])
            writer.writerow(row)

    print(f"Labels saved to {csv_path}")
    return csv_path


def label_folder(folder_name: str):
    """Open napari to label frames in a folder."""
    folder_path = LABELED_DATA_DIR / folder_name
    if not folder_path.exists():
        print(f"Folder not found: {folder_path}")
        sys.exit(1)

    frames, frame_names = load_frames(folder_path)
    if not frames:
        print(f"No PNG frames found in {folder_path}")
        sys.exit(1)

    print(f"\nLabeling: {folder_name}")
    print(f"Frames: {len(frames)}")
    print(f"Bodyparts: {', '.join(BODYPARTS)}")
    print("\nInstructions:")
    print("  1. Select a bodypart layer from the layer list")
    print("  2. Click 'Add points' mode (+ icon) in the layer controls")
    print("  3. Click on the image to place the point")
    print("  4. Use the slider to navigate between frames")
    print("  5. Label all 10 bodyparts on each frame")
    print("  6. Close napari when done - labels will be saved automatically")

    # Load existing labels if any
    existing_labels: dict[str, dict[str, tuple[float, float]]] = {}
    csv_path = folder_path / "labels.csv"
    if csv_path.exists():
        print(f"\nLoading existing labels from {csv_path}")
        with open(csv_path) as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 3:
                bp_row = rows[1][1:]
                for data_row in rows[3:]:
                    fname = data_row[0]
                    existing_labels[fname] = {}
                    for j in range(0, len(bp_row), 2):
                        bp = bp_row[j]
                        x_val = data_row[j + 1] if j + 1 < len(data_row) else ""
                        y_val = data_row[j + 2] if j + 2 < len(data_row) else ""
                        if x_val and y_val:
                            existing_labels[fname][bp] = (float(x_val), float(y_val))

    # Create napari viewer
    viewer = napari.Viewer(title=f"Label: {folder_name}")

    # Add image stack
    stack = np.stack(frames)
    viewer.add_image(stack, name="frames")

    # Add a points layer per bodypart
    point_layers = {}
    for bp in BODYPARTS:
        # Load existing points
        existing_pts = []
        for i, fname in enumerate(frame_names):
            if fname in existing_labels and bp in existing_labels[fname]:
                x, y = existing_labels[fname][bp]
                existing_pts.append([i, y, x])  # napari uses [z, row, col]

        data = np.array(existing_pts) if existing_pts else np.empty((0, 3))
        layer = viewer.add_points(
            data,
            name=bp,
            face_color=COLORS.get(bp, "white"),
            border_color="white",
            size=10,
            ndim=3,
        )
        point_layers[bp] = layer

    napari.run()

    # After closing, extract labels from point layers
    print("\nExtracting labels...")
    labels: dict[str, dict[str, tuple[float, float]]] = {}
    for bp, layer in point_layers.items():
        for pt in layer.data:
            frame_idx = int(round(pt[0]))
            if 0 <= frame_idx < len(frame_names):
                fname = frame_names[frame_idx]
                if fname not in labels:
                    labels[fname] = {}
                labels[fname][bp] = (pt[2], pt[1])  # convert back to (x, y)

    # Summary
    labeled_count = sum(1 for f in labels if len(labels[f]) == len(BODYPARTS))
    partial_count = sum(1 for f in labels if 0 < len(labels[f]) < len(BODYPARTS))
    print(f"\nFully labeled: {labeled_count}/{len(frame_names)} frames")
    if partial_count:
        print(f"Partially labeled: {partial_count} frames")

    if labels:
        save_labels(folder_path, frame_names, labels)
    else:
        print("No labels to save.")


def main():
    if len(sys.argv) > 1:
        folder_name = sys.argv[1]
    else:
        folders = list_folders()
        if not folders:
            print("No frame folders found. Run data collection first.")
            sys.exit(1)

        choice = input("\nEnter folder number or name: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                folder_name = folders[idx]
            else:
                print("Invalid choice.")
                sys.exit(1)
        else:
            folder_name = choice

    label_folder(folder_name)


if __name__ == "__main__":
    main()
