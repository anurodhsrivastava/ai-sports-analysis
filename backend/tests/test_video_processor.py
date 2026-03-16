"""
Tests for the video processor service.
Tests skeleton drawing, keypoint smoothing, and color assignment.
"""

import numpy as np
import pytest

from app.services.video_processor import (
    CONFIDENCE_THRESHOLD,
    _smooth_keypoints,
    draw_skeleton,
    get_limb_color,
)


def _make_frame(width: int = 640, height: int = 480) -> np.ndarray:
    """Create a blank frame for testing."""
    return np.zeros((height, width, 3), dtype=np.uint8)


def _make_keypoints(conf: float = 0.9) -> np.ndarray:
    """Create plausible keypoints in the center of a 640x480 frame."""
    cx, cy = 320, 240
    return np.array([
        [cx, cy - 120, conf],       # head
        [cx - 20, cy - 80, conf],   # nose_shoulder
        [cx + 20, cy - 80, conf],   # tail_shoulder
        [cx, cy - 20, conf],         # center_hips
        [cx - 30, cy + 30, conf],   # front_knee
        [cx + 30, cy + 30, conf],   # back_knee
        [cx - 40, cy + 90, conf],   # front_ankle
        [cx + 40, cy + 90, conf],   # back_ankle
        [cx - 70, cy + 100, conf],  # board_nose
        [cx + 70, cy + 100, conf],  # board_tail
    ])


class TestGetLimbColor:
    def test_board_color(self):
        color = get_limb_color("board_nose", "board_tail")
        assert color == (255, 50, 50)  # Blue

    def test_front_leg_color(self):
        color = get_limb_color("front_knee", "front_ankle")
        assert color == (0, 165, 255)  # Orange

    def test_back_leg_color(self):
        color = get_limb_color("back_knee", "back_ankle")
        assert color == (180, 0, 255)  # Magenta

    def test_head_color(self):
        color = get_limb_color("head", "nose_shoulder")
        assert color == (0, 255, 255)  # Yellow/Cyan

    def test_torso_color(self):
        color = get_limb_color("nose_shoulder", "center_hips")
        assert color == (0, 230, 118)  # Green


class TestDrawSkeleton:
    def test_draws_on_frame(self):
        frame = _make_frame()
        kp = _make_keypoints()
        result = draw_skeleton(frame, kp)
        assert result.shape == frame.shape
        # Result should not be identical to blank frame (skeleton was drawn)
        assert not np.array_equal(result, frame)

    def test_skips_low_confidence(self):
        frame = _make_frame()
        kp = _make_keypoints(conf=0.1)  # Below threshold
        result = draw_skeleton(frame, kp)
        # With very low confidence, nothing should be drawn
        assert np.array_equal(result, frame)

    def test_returns_copy(self):
        """draw_skeleton should not modify the original frame."""
        frame = _make_frame()
        original = frame.copy()
        kp = _make_keypoints()
        draw_skeleton(frame, kp)
        assert np.array_equal(frame, original)

    def test_handles_partial_confidence(self):
        """Some keypoints above threshold, some below."""
        frame = _make_frame()
        kp = _make_keypoints()
        # Set half to low confidence
        kp[5:, 2] = 0.1
        result = draw_skeleton(frame, kp)
        # Should still draw something (upper body)
        assert not np.array_equal(result, frame)


class TestSmoothKeypoints:
    def test_smoothing_reduces_jitter(self):
        """Smoothed keypoints should be less noisy."""
        base = _make_keypoints()
        kp_map = {}
        indices = list(range(10))
        for i in indices:
            noisy = base.copy()
            noisy[:, :2] += np.random.normal(0, 5, (10, 2))
            kp_map[i] = noisy

        smoothed = _smooth_keypoints(kp_map, indices, window=5)

        # Check that smoothed positions are closer to the mean
        raw_std = np.std([kp_map[i][:, :2] for i in indices], axis=0)
        smooth_std = np.std([smoothed[i][:, :2] for i in indices], axis=0)
        assert np.mean(smooth_std) <= np.mean(raw_std)

    def test_single_frame_unchanged(self):
        """Single frame should be returned as-is."""
        kp = _make_keypoints()
        kp_map = {0: kp}
        smoothed = _smooth_keypoints(kp_map, [0], window=3)
        assert np.array_equal(smoothed[0], kp)

    def test_preserves_confidence(self):
        """Smoothing should not change confidence values."""
        base = _make_keypoints(conf=0.85)
        kp_map = {i: base.copy() for i in range(5)}
        smoothed = _smooth_keypoints(kp_map, list(range(5)), window=3)
        for kp in smoothed.values():
            assert np.allclose(kp[:, 2], 0.85)
