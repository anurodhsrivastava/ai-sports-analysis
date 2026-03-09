"""Tests for sport coach logic modules."""

import numpy as np
import pytest

from app.services.coach_logic.base import Severity, compute_angle, compute_vector_angle, merge_consecutive_tips, CoachingTip
from app.services.coach_logic.snowboard import SnowboardCoach
from app.services.coach_logic.skiing import SkiingCoach
from app.services.coach_logic.running import RunningCoach
from app.services.coach_logic.home_workout import HomeWorkoutCoach, classify_exercise
from app.services.coach_logic.golf import GolfCoach
from app.services.coach_logic.yoga import YogaCoach


# --------------------------------------------------------------------------
# Base utilities
# --------------------------------------------------------------------------

def test_compute_angle_straight():
    """Three collinear points should give ~180 degrees."""
    a = np.array([0.0, 0.0])
    vertex = np.array([1.0, 0.0])
    c = np.array([2.0, 0.0])
    angle = compute_angle(a, vertex, c)
    assert abs(angle - 180.0) < 0.1


def test_compute_angle_right():
    """90-degree angle."""
    a = np.array([0.0, 1.0])
    vertex = np.array([0.0, 0.0])
    c = np.array([1.0, 0.0])
    angle = compute_angle(a, vertex, c)
    assert abs(angle - 90.0) < 0.1


def test_compute_vector_angle():
    v1 = np.array([1.0, 0.0])
    v2 = np.array([0.0, 1.0])
    angle = compute_vector_angle(v1, v2)
    assert abs(angle - 90.0) < 0.1


def test_merge_consecutive_tips():
    tips = [
        CoachingTip("Cat", "part", 10.0, 5.0, "msg", Severity.WARNING, (0, 0)),
        CoachingTip("Cat", "part", 12.0, 5.0, "msg", Severity.WARNING, (3, 3)),
        CoachingTip("Cat", "part", 15.0, 5.0, "msg", Severity.WARNING, (20, 20)),
    ]
    merged = merge_consecutive_tips(tips, max_gap=5)
    assert len(merged) == 2
    assert merged[0].frame_range == (0, 3)
    assert merged[0].angle_value == 12.0
    assert merged[1].frame_range == (20, 20)


# --------------------------------------------------------------------------
# Snowboard coach
# --------------------------------------------------------------------------

def _snowboard_kp(front_knee_angle=130, shoulder_offset=5):
    """Create snowboard keypoints with controllable front knee angle."""
    kp = np.zeros((10, 3))
    # head, shoulders, hips
    kp[0] = [160, 50, 0.9]   # head
    kp[1] = [150, 80, 0.9]   # nose_shoulder
    kp[2] = [170, 80, 0.9]   # tail_shoulder
    kp[3] = [160, 130, 0.9]  # center_hips

    # Front leg: hip at (160,130), knee, ankle
    # Straight = knee at (150, 180), ankle at (140, 230)
    kp[4] = [150, 180, 0.9]  # front_knee
    kp[5] = [170, 180, 0.9]  # back_knee
    kp[6] = [140, 230, 0.9]  # front_ankle
    kp[7] = [180, 230, 0.9]  # back_ankle

    # Board
    kp[8] = [120, 240, 0.9]  # board_nose
    kp[9] = [200, 240, 0.9]  # board_tail
    return kp


def test_snowboard_coach_no_issues():
    coach = SnowboardCoach()
    kp = _snowboard_kp()
    tips = coach.analyze_frame(kp, 0)
    # With moderate angles, should have few or no issues
    assert isinstance(tips, list)


def test_snowboard_coach_sequence():
    coach = SnowboardCoach()
    keypoints = [_snowboard_kp() for _ in range(5)]
    indices = list(range(5))
    tips = coach.analyze_sequence(keypoints, indices)
    assert isinstance(tips, list)


def test_snowboard_coach_summary():
    coach = SnowboardCoach()
    keypoints = [_snowboard_kp() for _ in range(5)]
    stats = coach.compute_keypoints_summary(keypoints)
    assert "total_frames_analyzed" in stats
    assert stats["total_frames_analyzed"] == 5


# --------------------------------------------------------------------------
# Skiing coach
# --------------------------------------------------------------------------

def _skiing_kp():
    kp = np.zeros((14, 3))
    kp[0] = [160, 40, 0.9]   # head
    kp[1] = [145, 70, 0.9]   # left_shoulder
    kp[2] = [175, 70, 0.9]   # right_shoulder
    kp[3] = [160, 120, 0.9]  # center_hips
    kp[4] = [150, 170, 0.9]  # left_knee
    kp[5] = [170, 170, 0.9]  # right_knee
    kp[6] = [145, 220, 0.9]  # left_ankle
    kp[7] = [175, 220, 0.9]  # right_ankle
    kp[8] = [120, 230, 0.9]  # left_ski_tip
    kp[9] = [145, 235, 0.9]  # left_ski_tail
    kp[10] = [175, 230, 0.9] # right_ski_tip
    kp[11] = [200, 235, 0.9] # right_ski_tail
    kp[12] = [130, 100, 0.9] # left_pole_tip
    kp[13] = [190, 100, 0.9] # right_pole_tip
    return kp


def test_skiing_coach_basic():
    coach = SkiingCoach()
    kp = _skiing_kp()
    tips = coach.analyze_frame(kp, 0)
    assert isinstance(tips, list)


def test_skiing_coach_summary():
    coach = SkiingCoach()
    keypoints = [_skiing_kp() for _ in range(3)]
    stats = coach.compute_keypoints_summary(keypoints)
    assert stats["total_frames_analyzed"] == 3
    assert "avg_ski_parallelism" in stats


# --------------------------------------------------------------------------
# Running coach
# --------------------------------------------------------------------------

def _running_kp():
    kp = np.zeros((12, 3))
    kp[0] = [160, 30, 0.9]   # head
    kp[1] = [160, 55, 0.9]   # neck
    kp[2] = [150, 70, 0.9]   # shoulder
    kp[3] = [140, 100, 0.9]  # elbow
    kp[4] = [145, 85, 0.9]   # wrist
    kp[5] = [165, 130, 0.9]  # hip
    kp[6] = [160, 180, 0.9]  # knee
    kp[7] = [155, 230, 0.9]  # ankle
    kp[8] = [145, 240, 0.9]  # toe
    kp[9] = [165, 235, 0.9]  # heel
    kp[10] = [155, 100, 0.9] # mid_torso
    kp[11] = [165, 125, 0.9] # pelvis
    return kp


def test_running_coach_basic():
    coach = RunningCoach()
    kp = _running_kp()
    tips = coach.analyze_frame(kp, 0)
    assert isinstance(tips, list)


def test_running_coach_summary():
    coach = RunningCoach()
    keypoints = [_running_kp() for _ in range(5)]
    stats = coach.compute_keypoints_summary(keypoints)
    assert stats["total_frames_analyzed"] == 5
    assert "avg_forward_lean" in stats


# --------------------------------------------------------------------------
# Home workout coach
# --------------------------------------------------------------------------

def _workout_kp_standing():
    kp = np.zeros((13, 3))
    kp[0] = [160, 30, 0.9]   # head
    kp[1] = [145, 70, 0.9]   # left_shoulder
    kp[2] = [175, 70, 0.9]   # right_shoulder
    kp[3] = [130, 100, 0.9]  # left_elbow
    kp[4] = [190, 100, 0.9]  # right_elbow
    kp[5] = [125, 130, 0.9]  # left_wrist
    kp[6] = [195, 130, 0.9]  # right_wrist
    kp[7] = [150, 140, 0.9]  # left_hip
    kp[8] = [170, 140, 0.9]  # right_hip
    kp[9] = [148, 200, 0.9]  # left_knee
    kp[10] = [172, 200, 0.9] # right_knee
    kp[11] = [145, 260, 0.9] # left_ankle
    kp[12] = [175, 260, 0.9] # right_ankle
    return kp


def test_classify_exercise_standing():
    kp = _workout_kp_standing()
    assert classify_exercise(kp) == "standing"


def test_home_workout_coach_basic():
    coach = HomeWorkoutCoach()
    kp = _workout_kp_standing()
    tips = coach.analyze_frame(kp, 0)
    assert isinstance(tips, list)


def test_home_workout_coach_summary():
    coach = HomeWorkoutCoach()
    keypoints = [_workout_kp_standing() for _ in range(3)]
    stats = coach.compute_keypoints_summary(keypoints)
    assert stats["total_frames_analyzed"] == 3
    assert "detected_exercise" in stats


# --------------------------------------------------------------------------
# Golf coach
# --------------------------------------------------------------------------

def _golf_kp():
    kp = np.zeros((12, 3))
    kp[0] = [160, 30, 0.9]   # head
    kp[1] = [160, 60, 0.9]   # neck
    kp[2] = [145, 80, 0.9]   # lead_shoulder
    kp[3] = [175, 80, 0.9]   # trail_shoulder
    kp[4] = [130, 110, 0.9]  # lead_elbow
    kp[5] = [190, 110, 0.9]  # trail_elbow
    kp[6] = [120, 140, 0.9]  # lead_wrist
    kp[7] = [200, 140, 0.9]  # trail_wrist
    kp[8] = [150, 140, 0.9]  # lead_hip
    kp[9] = [170, 140, 0.9]  # trail_hip
    kp[10] = [148, 200, 0.9] # lead_knee
    kp[11] = [172, 200, 0.9] # trail_knee
    return kp


def test_golf_coach_basic():
    coach = GolfCoach()
    kp = _golf_kp()
    tips = coach.analyze_frame(kp, 0)
    assert isinstance(tips, list)


def test_golf_coach_summary():
    coach = GolfCoach()
    keypoints = [_golf_kp() for _ in range(5)]
    stats = coach.compute_keypoints_summary(keypoints)
    assert stats["total_frames_analyzed"] == 5
    assert "avg_spine_angle" in stats


# --------------------------------------------------------------------------
# Yoga coach
# --------------------------------------------------------------------------

def _yoga_kp():
    kp = np.zeros((15, 3))
    kp[0] = [160, 30, 0.9]   # head
    kp[1] = [160, 55, 0.9]   # neck
    kp[2] = [145, 75, 0.9]   # left_shoulder
    kp[3] = [175, 75, 0.9]   # right_shoulder
    kp[4] = [130, 105, 0.9]  # left_elbow
    kp[5] = [190, 105, 0.9]  # right_elbow
    kp[6] = [125, 135, 0.9]  # left_wrist
    kp[7] = [195, 135, 0.9]  # right_wrist
    kp[8] = [150, 140, 0.9]  # left_hip
    kp[9] = [170, 140, 0.9]  # right_hip
    kp[10] = [148, 200, 0.9] # left_knee
    kp[11] = [172, 200, 0.9] # right_knee
    kp[12] = [145, 260, 0.9] # left_ankle
    kp[13] = [175, 260, 0.9] # right_ankle
    kp[14] = [160, 135, 0.9] # pelvis
    return kp


def test_yoga_coach_basic():
    coach = YogaCoach()
    kp = _yoga_kp()
    tips = coach.analyze_frame(kp, 0)
    assert isinstance(tips, list)


def test_yoga_coach_summary():
    coach = YogaCoach()
    keypoints = [_yoga_kp() for _ in range(4)]
    stats = coach.compute_keypoints_summary(keypoints)
    assert stats["total_frames_analyzed"] == 4
    assert "avg_spine_alignment" in stats


# --------------------------------------------------------------------------
# Sport registry
# --------------------------------------------------------------------------

def test_sport_registry():
    from app.sports.registry import SportRegistry
    # Import all sports to trigger registration
    import app.sports  # noqa: F401

    sports = SportRegistry.list_sports()
    sport_ids = [s["sport_id"] for s in sports]
    assert "snowboard" in sport_ids
    assert "skiing" in sport_ids
    assert "running" in sport_ids
    assert "home_workout" in sport_ids
    assert "golf" in sport_ids
    assert "yoga" in sport_ids

    assert SportRegistry.has_sport("snowboard")
    assert SportRegistry.has_sport("golf")
    assert SportRegistry.has_sport("yoga")
    assert not SportRegistry.has_sport("tennis")

    defn = SportRegistry.get_definition("snowboard")
    assert defn.num_keypoints == 10

    coach = SportRegistry.get_coach("skiing")
    assert hasattr(coach, "analyze_frame")


# --------------------------------------------------------------------------
# Inference factory
# --------------------------------------------------------------------------

def test_create_estimator_mock():
    from app.services.inference import create_estimator, MockPoseEstimator
    # Without model files, should get mock estimators
    est = create_estimator("snowboard")
    assert isinstance(est, MockPoseEstimator)
