"""
DeepLabCut Project Initialization
Creates a DLC project configured for snowboard pose estimation
with 10 bodyparts and launches the labeling GUI.
"""

import os
from pathlib import Path

import deeplabcut


PROJECT_NAME = "snowboard-coach"
EXPERIMENTER = "coach"
WORKING_DIR = Path(__file__).parent.parent
VIDEOS_DIR = WORKING_DIR / "videos"

BODYPARTS = [
    "head",
    "nose_shoulder",     # Front shoulder (nose-side of board)
    "tail_shoulder",     # Rear shoulder (tail-side of board)
    "center_hips",
    "front_knee",
    "back_knee",
    "front_ankle",
    "back_ankle",
    "board_nose",
    "board_tail",
]

SKELETON = [
    ["nose_shoulder", "tail_shoulder"],       # Shoulder line
    ["nose_shoulder", "center_hips"],         # Front torso
    ["tail_shoulder", "center_hips"],         # Rear torso
    ["center_hips", "front_knee"],            # Front upper leg
    ["center_hips", "back_knee"],             # Back upper leg
    ["front_knee", "front_ankle"],            # Front lower leg
    ["back_knee", "back_ankle"],              # Back lower leg
    ["board_nose", "board_tail"],             # Board line
    ["front_ankle", "board_nose"],            # Front binding
    ["back_ankle", "board_tail"],             # Rear binding
    ["head", "nose_shoulder"],                # Neck front
    ["head", "tail_shoulder"],                # Neck rear
]


def find_videos(videos_dir: Path) -> list[str]:
    """Find all mp4 videos in the videos directory."""
    videos = list(videos_dir.glob("*.mp4"))
    if not videos:
        print(f"No videos found in {videos_dir}")
        print("Run data-collection/collect_frames.py first to download videos.")
        return []
    return [str(v) for v in videos]


def create_project(video_paths: list[str]) -> str:
    """Create a new DLC project and return the config path."""
    config_path = deeplabcut.create_new_project(
        PROJECT_NAME,
        EXPERIMENTER,
        video_paths,
        working_directory=str(WORKING_DIR),
        copy_videos=False,
        multianimal=False,
    )
    print(f"Project created at: {config_path}")
    return config_path


def configure_project(config_path: str) -> None:
    """Update the DLC config.yaml with snowboard-specific settings."""
    import yaml

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Set bodyparts
    config["bodyparts"] = BODYPARTS

    # Set skeleton
    config["skeleton"] = SKELETON

    # Frame extraction settings
    config["numframes2pick"] = 20
    config["extraction_method"] = "kmeans"

    # Training settings
    config["TrainingFraction"] = [0.8]
    config["default_net_type"] = "resnet_50"
    config["default_augmenter"] = "imgaug"

    # Snapshot settings
    config["snapshotindex"] = -1  # Use the latest snapshot

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print("Config updated with snowboard bodyparts and skeleton.")
    print(f"  Bodyparts: {len(BODYPARTS)}")
    print(f"  Skeleton connections: {len(SKELETON)}")


def extract_and_label(config_path: str) -> None:
    """Extract frames and launch the labeling GUI."""
    print("\nExtracting frames for labeling...")
    deeplabcut.extract_frames(
        config_path,
        mode="automatic",
        algo="kmeans",
        userfeedback=False,
    )

    print("\nLaunching labeling GUI...")
    print("Instructions:")
    print("  1. Label all 10 bodyparts on each frame")
    print("  2. Use right-click to place a point")
    print("  3. If a bodypart is occluded, skip it")
    print("  4. Save and close when done")
    deeplabcut.label_frames(config_path)


def main() -> None:
    """Main entry point."""
    video_paths = find_videos(VIDEOS_DIR)
    if not video_paths:
        return

    print(f"Found {len(video_paths)} video(s)")

    config_path = create_project(video_paths)
    configure_project(config_path)

    print("\nProject initialized successfully!")
    print(f"Config: {config_path}")

    response = input("\nExtract frames and launch labeling GUI? [y/N]: ")
    if response.lower() == "y":
        extract_and_label(config_path)
    else:
        print("Run later with:")
        print(f"  deeplabcut.extract_frames('{config_path}', ...)")
        print(f"  deeplabcut.label_frames('{config_path}')")


if __name__ == "__main__":
    main()
