"""Snowboard sport definition and registration."""

import numpy as np

from .base import KeypointDef, SkeletonConnection, SportDefinition
from .registry import SportRegistry
from ..services.coach_logic.snowboard import SnowboardCoach


def _mock_keypoints(w: int, h: int) -> np.ndarray:
    cx, cy = w / 2, h / 2
    kp = np.array([
        [cx, cy - 120, 0.95],       # head
        [cx - 20, cy - 80, 0.92],   # nose_shoulder
        [cx + 20, cy - 80, 0.91],   # tail_shoulder
        [cx, cy - 20, 0.93],        # center_hips
        [cx - 30, cy + 30, 0.88],   # front_knee
        [cx + 30, cy + 30, 0.87],   # back_knee
        [cx - 40, cy + 90, 0.85],   # front_ankle
        [cx + 40, cy + 90, 0.84],   # back_ankle
        [cx - 70, cy + 100, 0.90],  # board_nose
        [cx + 70, cy + 100, 0.89],  # board_tail
    ])
    kp[:, :2] += np.random.normal(0, 3, kp[:, :2].shape)
    return kp


definition = SportDefinition(
    sport_id="snowboard",
    display_name="Snowboarding",
    emoji="\U0001f3c2",
    description="Analyze snowboarding technique including knee flexion, shoulder alignment, and stance width.",
    num_keypoints=10,
    keypoints=[
        KeypointDef("head", 0, "head"),
        KeypointDef("nose_shoulder", 1, "torso"),
        KeypointDef("tail_shoulder", 2, "torso"),
        KeypointDef("center_hips", 3, "torso"),
        KeypointDef("front_knee", 4, "front_leg"),
        KeypointDef("back_knee", 5, "back_leg"),
        KeypointDef("front_ankle", 6, "front_leg"),
        KeypointDef("back_ankle", 7, "back_leg"),
        KeypointDef("board_nose", 8, "board"),
        KeypointDef("board_tail", 9, "board"),
    ],
    skeleton=[
        SkeletonConnection("head", "nose_shoulder", "head"),
        SkeletonConnection("head", "tail_shoulder", "head"),
        SkeletonConnection("nose_shoulder", "tail_shoulder", "torso"),
        SkeletonConnection("nose_shoulder", "center_hips", "torso"),
        SkeletonConnection("tail_shoulder", "center_hips", "torso"),
        SkeletonConnection("center_hips", "front_knee", "front_leg"),
        SkeletonConnection("center_hips", "back_knee", "back_leg"),
        SkeletonConnection("front_knee", "front_ankle", "front_leg"),
        SkeletonConnection("back_knee", "back_ankle", "back_leg"),
        SkeletonConnection("front_ankle", "board_nose", "board"),
        SkeletonConnection("back_ankle", "board_tail", "board"),
        SkeletonConnection("board_nose", "board_tail", "board"),
    ],
    model_filename="snowboard_pose_model.pt",
    region_colors={
        "head": (0, 255, 255),
        "torso": (0, 255, 0),
        "front_leg": (255, 165, 0),
        "back_leg": (255, 0, 128),
        "board": (255, 0, 0),
    },
    coaching_categories=["Knee Flexion", "Shoulder Alignment", "Stance Width"],
    mock_keypoints_fn=_mock_keypoints,
)

SportRegistry.register(definition, SnowboardCoach())
