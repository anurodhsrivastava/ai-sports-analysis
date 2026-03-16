"""
Tests for the biomechanical analysis engine.
Uses known geometry to verify angle calculations and coaching thresholds.
"""

import math

import numpy as np
import pytest

from app.services.snow_coach_logic import (
    Severity,
    analyze_frame,
    analyze_sequence,
    compute_angle,
    compute_vector_angle,
)


class TestComputeAngle:
    """Test the Law of Cosines angle computation."""

    def test_right_angle(self):
        """90-degree angle at the vertex."""
        a = np.array([1.0, 0.0])
        vertex = np.array([0.0, 0.0])
        c = np.array([0.0, 1.0])
        angle = compute_angle(a, vertex, c)
        assert abs(angle - 90.0) < 0.01

    def test_straight_line(self):
        """180-degree angle (collinear points)."""
        a = np.array([-1.0, 0.0])
        vertex = np.array([0.0, 0.0])
        c = np.array([1.0, 0.0])
        angle = compute_angle(a, vertex, c)
        assert abs(angle - 180.0) < 0.01

    def test_acute_angle(self):
        """60-degree angle (equilateral triangle)."""
        a = np.array([1.0, 0.0])
        vertex = np.array([0.0, 0.0])
        c = np.array([0.5, math.sqrt(3) / 2])
        angle = compute_angle(a, vertex, c)
        assert abs(angle - 60.0) < 0.01

    def test_obtuse_angle(self):
        """120-degree angle."""
        a = np.array([1.0, 0.0])
        vertex = np.array([0.0, 0.0])
        c = np.array([-0.5, math.sqrt(3) / 2])
        angle = compute_angle(a, vertex, c)
        assert abs(angle - 120.0) < 0.01

    def test_zero_length_vector(self):
        """Returns 0 when a point overlaps vertex."""
        a = np.array([0.0, 0.0])
        vertex = np.array([0.0, 0.0])
        c = np.array([1.0, 0.0])
        angle = compute_angle(a, vertex, c)
        assert angle == 0.0


class TestComputeVectorAngle:
    """Test the vector angle computation."""

    def test_parallel_vectors(self):
        v1 = np.array([1.0, 0.0])
        v2 = np.array([2.0, 0.0])
        assert abs(compute_vector_angle(v1, v2)) < 0.01

    def test_perpendicular_vectors(self):
        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])
        assert abs(compute_vector_angle(v1, v2) - 90.0) < 0.01

    def test_opposite_vectors(self):
        v1 = np.array([1.0, 0.0])
        v2 = np.array([-1.0, 0.0])
        assert abs(compute_vector_angle(v1, v2) - 180.0) < 0.01


def _make_keypoints(
    front_knee_angle: float = 130.0,
    back_knee_angle: float = 130.0,
    shoulder_board_angle: float = 5.0,
) -> np.ndarray:
    """
    Generate synthetic keypoints with specific joint angles.
    All keypoints include [x, y, confidence].
    """
    # Place hips at origin, build outward
    hips = np.array([300.0, 300.0])

    # Shoulders aligned with board by default
    board_angle_rad = 0.0  # horizontal
    board_nose = hips + np.array([-100.0, 80.0])
    board_tail = hips + np.array([100.0, 80.0])

    # Shoulders: offset from board angle by shoulder_board_angle
    s_angle_rad = math.radians(shoulder_board_angle)
    nose_shoulder = hips + np.array([-40 * math.cos(s_angle_rad), -60 + 40 * math.sin(s_angle_rad)])
    tail_shoulder = hips + np.array([40 * math.cos(s_angle_rad), -60 - 40 * math.sin(s_angle_rad)])

    head = (nose_shoulder + tail_shoulder) / 2 + np.array([0.0, -40.0])

    # Front leg: hip -> knee -> ankle with specified angle at knee
    fk_rad = math.radians(front_knee_angle)
    front_knee = hips + np.array([-30.0, 50.0])
    # Place ankle so that hip-knee-ankle angle = front_knee_angle
    fk_to_hip = hips - front_knee
    fk_to_hip_angle = math.atan2(fk_to_hip[1], fk_to_hip[0])
    ankle_angle = fk_to_hip_angle - fk_rad
    front_ankle = front_knee + 50 * np.array([math.cos(ankle_angle), math.sin(ankle_angle)])

    # Back leg
    bk_rad = math.radians(back_knee_angle)
    back_knee = hips + np.array([30.0, 50.0])
    bk_to_hip = hips - back_knee
    bk_to_hip_angle = math.atan2(bk_to_hip[1], bk_to_hip[0])
    ba_angle = bk_to_hip_angle - bk_rad
    back_ankle = back_knee + 50 * np.array([math.cos(ba_angle), math.sin(ba_angle)])

    # Build keypoints array: [x, y, confidence]
    keypoints = np.array([
        [head[0], head[1], 0.95],
        [nose_shoulder[0], nose_shoulder[1], 0.93],
        [tail_shoulder[0], tail_shoulder[1], 0.93],
        [hips[0], hips[1], 0.95],
        [front_knee[0], front_knee[1], 0.90],
        [back_knee[0], back_knee[1], 0.90],
        [front_ankle[0], front_ankle[1], 0.88],
        [back_ankle[0], back_ankle[1], 0.88],
        [board_nose[0], board_nose[1], 0.92],
        [board_tail[0], board_tail[1], 0.92],
    ])

    return keypoints


class TestAnalyzeFrame:
    """Test coaching tip generation from frame analysis."""

    def test_good_form_no_tips(self):
        """Good form should produce no coaching tips."""
        kp = _make_keypoints(
            front_knee_angle=120.0,
            back_knee_angle=120.0,
            shoulder_board_angle=5.0,
        )
        tips = analyze_frame(kp, frame_idx=0)
        assert len(tips) == 0

    def test_straight_knees_critical(self):
        """Knees at 175 degrees should trigger critical tips."""
        kp = _make_keypoints(
            front_knee_angle=175.0,
            back_knee_angle=175.0,
        )
        tips = analyze_frame(kp, frame_idx=0)
        knee_tips = [t for t in tips if t.category == "Knee Flexion"]
        assert len(knee_tips) == 2
        assert all(t.severity == Severity.CRITICAL for t in knee_tips)

    def test_slightly_straight_knees_warning(self):
        """Knees at 165 degrees should trigger warning tips."""
        kp = _make_keypoints(
            front_knee_angle=165.0,
            back_knee_angle=165.0,
        )
        tips = analyze_frame(kp, frame_idx=0)
        knee_tips = [t for t in tips if t.category == "Knee Flexion"]
        assert len(knee_tips) == 2
        assert all(t.severity == Severity.WARNING for t in knee_tips)

    def test_shoulder_misalignment_critical(self):
        """Shoulders rotated 35 degrees from board should be critical."""
        kp = _make_keypoints(shoulder_board_angle=35.0)
        tips = analyze_frame(kp, frame_idx=0)
        shoulder_tips = [t for t in tips if t.category == "Shoulder Alignment"]
        assert len(shoulder_tips) == 1
        assert shoulder_tips[0].severity == Severity.CRITICAL

    def test_shoulder_slight_misalignment_warning(self):
        """Shoulders rotated 20 degrees from board should be warning."""
        kp = _make_keypoints(shoulder_board_angle=20.0)
        tips = analyze_frame(kp, frame_idx=0)
        shoulder_tips = [t for t in tips if t.category == "Shoulder Alignment"]
        assert len(shoulder_tips) == 1
        assert shoulder_tips[0].severity == Severity.WARNING


class TestAnalyzeSequence:
    """Test sequence analysis with frame merging."""

    def test_merges_consecutive_frames(self):
        """Consecutive frames with same issue should merge into one tip."""
        frames = [
            _make_keypoints(front_knee_angle=175.0)
            for _ in range(5)
        ]
        tips = analyze_sequence(frames, frame_indices=[0, 1, 2, 3, 4])
        front_knee_tips = [
            t for t in tips
            if t.category == "Knee Flexion" and t.body_part == "front_knee"
        ]
        assert len(front_knee_tips) == 1
        assert front_knee_tips[0].frame_range == (0, 4)

    def test_separate_non_consecutive(self):
        """Frames far apart should not be merged."""
        kp_bad = _make_keypoints(front_knee_angle=175.0)
        kp_good = _make_keypoints(front_knee_angle=120.0)
        frames = [kp_bad, kp_good, kp_good, kp_good, kp_good, kp_good, kp_good, kp_bad]
        indices = [0, 1, 2, 3, 10, 11, 12, 20]
        tips = analyze_sequence(frames, indices)
        front_knee_tips = [
            t for t in tips
            if t.category == "Knee Flexion" and t.body_part == "front_knee"
        ]
        assert len(front_knee_tips) == 2

    def test_empty_sequence(self):
        """Empty sequence should return no tips."""
        tips = analyze_sequence([], [])
        assert tips == []
