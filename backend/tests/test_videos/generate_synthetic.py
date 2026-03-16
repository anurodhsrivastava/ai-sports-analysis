"""
Generate small synthetic test videos with known color properties.

These provide deterministic, reliable test data for scene detection
without depending on external video downloads.
"""

import cv2
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "synthetic"


def _make_video(path: Path, frames: list[np.ndarray], fps: int = 10):
    """Write frames to an mp4 video file."""
    h, w = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (w, h))
    for frame in frames:
        writer.write(frame)
    writer.release()


def _snow_frames(n: int = 30, h: int = 240, w: int = 320) -> list[np.ndarray]:
    """Bright, low-saturation smooth frames simulating snow/mountain."""
    frames = []
    for i in range(n):
        # Base: uniform bright white with slight blue tint
        hsv = np.zeros((h, w, 3), dtype=np.uint8)
        hsv[:, :, 0] = 105  # slight blue hue
        hsv[:, :, 1] = 20   # very low saturation
        hsv[:, :, 2] = 220  # bright
        # Add subtle smooth gradient (sky to snow)
        gradient = np.linspace(200, 240, h, dtype=np.uint8).reshape(-1, 1)
        hsv[:, :, 2] = gradient
        # Add very gentle Gaussian noise (smooth, not per-pixel random)
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        noise = np.random.normal(0, 3, frame.shape).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        frames.append(frame)
    return frames


def _water_frames(n: int = 30, h: int = 240, w: int = 320) -> list[np.ndarray]:
    """Blue-dominant frames simulating ocean/water."""
    frames = []
    for i in range(n):
        hsv = np.zeros((h, w, 3), dtype=np.uint8)
        hsv[:, :, 0] = np.random.randint(95, 125, (h, w), dtype=np.uint8)   # blue hue
        hsv[:, :, 1] = np.random.randint(80, 180, (h, w), dtype=np.uint8)   # moderate sat
        hsv[:, :, 2] = np.random.randint(80, 200, (h, w), dtype=np.uint8)   # varied value
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        frames.append(frame)
    return frames


def _urban_frames(n: int = 30, h: int = 240, w: int = 320) -> list[np.ndarray]:
    """Gray, medium-brightness frames simulating urban/concrete."""
    frames = []
    for i in range(n):
        hsv = np.zeros((h, w, 3), dtype=np.uint8)
        hsv[:, :, 0] = np.random.randint(0, 180, (h, w), dtype=np.uint8)    # varied hue
        hsv[:, :, 1] = np.random.randint(5, 40, (h, w), dtype=np.uint8)     # low sat
        hsv[:, :, 2] = np.random.randint(60, 160, (h, w), dtype=np.uint8)   # medium value
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        frames.append(frame)
    return frames


def _indoor_frames(n: int = 30, h: int = 240, w: int = 320) -> list[np.ndarray]:
    """Mixed-color indoor frames with many edges (furniture, objects)."""
    frames = []
    for i in range(n):
        # Warm tones (reds, yellows) with moderate saturation
        hsv = np.zeros((h, w, 3), dtype=np.uint8)
        hsv[:, :, 0] = np.random.randint(5, 30, (h, w), dtype=np.uint8)     # warm hue
        hsv[:, :, 1] = np.random.randint(60, 150, (h, w), dtype=np.uint8)   # moderate sat
        hsv[:, :, 2] = np.random.randint(80, 200, (h, w), dtype=np.uint8)   # varied value
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        # Add edge-creating rectangles
        for _ in range(10):
            x1, y1 = np.random.randint(0, w-40), np.random.randint(0, h-40)
            x2, y2 = x1 + np.random.randint(20, 60), y1 + np.random.randint(20, 60)
            color = tuple(int(c) for c in np.random.randint(0, 255, 3))
            cv2.rectangle(frame, (x1, y1), (min(x2, w-1), min(y2, h-1)), color, 2)
        frames.append(frame)
    return frames


def generate_all():
    """Generate all synthetic test videos."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    videos = {
        "synthetic_snow": _snow_frames,
        "synthetic_water": _water_frames,
        "synthetic_urban": _urban_frames,
        "synthetic_indoor": _indoor_frames,
    }

    for name, frame_fn in videos.items():
        path = OUTPUT_DIR / f"{name}.mp4"
        if path.exists():
            print(f"  [exists] {name}")
            continue
        frames = frame_fn()
        _make_video(path, frames)
        print(f"  [created] {name} ({path.stat().st_size // 1024} KB)")

    return {name: str(OUTPUT_DIR / f"{name}.mp4") for name in videos}


if __name__ == "__main__":
    print("Generating synthetic test videos...")
    generate_all()
    print("Done.")
