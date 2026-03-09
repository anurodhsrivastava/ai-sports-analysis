"""
Video Processor
Overlays skeleton visualization on the original video.

Performance features:
- ffmpeg post-compression with faststart for web streaming -- Fix #7
"""

import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np

from ..sports.base import SportDefinition

CONFIDENCE_THRESHOLD = 0.3


def get_limb_color(
    part1: str,
    part2: str,
    skeleton: list,
    region_colors: dict[str, tuple[int, int, int]],
) -> tuple[int, int, int]:
    """Get the color for a skeleton limb based on the connection's region."""
    for conn in skeleton:
        if {conn.from_keypoint, conn.to_keypoint} == {part1, part2}:
            return region_colors.get(conn.region, (0, 255, 0))
    return (0, 255, 0)


def draw_skeleton(
    frame: np.ndarray,
    keypoints: np.ndarray,
    definition: SportDefinition,
    confidence_threshold: float = CONFIDENCE_THRESHOLD,
) -> np.ndarray:
    """Draw skeleton overlay on a frame using sport-specific skeleton."""
    annotated = frame.copy()
    bp_indices = definition.bodypart_indices

    # Draw limbs
    for conn in definition.skeleton:
        idx1 = bp_indices[conn.from_keypoint]
        idx2 = bp_indices[conn.to_keypoint]

        x1, y1, conf1 = keypoints[idx1]
        x2, y2, conf2 = keypoints[idx2]

        if conf1 > confidence_threshold and conf2 > confidence_threshold:
            color = definition.region_colors.get(conn.region, (0, 255, 0))
            pt1 = (int(x1), int(y1))
            pt2 = (int(x2), int(y2))
            cv2.line(annotated, pt1, pt2, color, 2, cv2.LINE_AA)

    # Draw keypoints
    for kp_def in definition.keypoints:
        x, y, conf = keypoints[kp_def.index]
        if conf > confidence_threshold:
            color = definition.region_colors.get(kp_def.region, (0, 255, 255))
            cv2.circle(annotated, (int(x), int(y)), 4, color, -1, cv2.LINE_AA)
            cv2.circle(annotated, (int(x), int(y)), 6, color, 1, cv2.LINE_AA)

    return annotated


def _compress_with_ffmpeg(input_path: Path, output_path: Path) -> bool:
    if not shutil.which("ffmpeg"):
        return False

    tmp_path = output_path.with_suffix(".tmp.mp4")
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", str(input_path),
                "-c:v", "libx264", "-crf", "28",
                "-preset", "fast",
                "-movflags", "+faststart",
                "-an",
                "-y", str(tmp_path),
            ],
            check=True,
            capture_output=True,
        )
        tmp_path.replace(output_path)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        tmp_path.unlink(missing_ok=True)
        return False


def create_annotated_video(
    input_path: str | Path,
    output_path: str | Path,
    all_keypoints: list[np.ndarray],
    frame_indices: list[int],
    definition: SportDefinition,
    sample_rate: int = 1,
) -> Path:
    """Create a new video with skeleton overlays using sport-specific skeleton."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    kp_map: dict[int, np.ndarray] = dict(zip(frame_indices, all_keypoints))

    frame_idx = 0
    last_kp = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx in kp_map:
            last_kp = kp_map[frame_idx]

        if last_kp is not None:
            frame = draw_skeleton(frame, last_kp, definition)

        writer.write(frame)
        frame_idx += 1

    cap.release()
    writer.release()

    compressed = _compress_with_ffmpeg(output_path, output_path)
    if compressed:
        print(f"Video compressed with ffmpeg: {output_path}")

    return output_path
