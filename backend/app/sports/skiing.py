"""Skiing sport definition and registration."""

import numpy as np

from .base import KeypointDef, SkeletonConnection, SportDefinition
from .registry import SportRegistry
from ..services.coach_logic.skiing import SkiingCoach


def _mock_keypoints(w: int, h: int) -> np.ndarray:
    cx, cy = w / 2, h / 2
    kp = np.array([
        [cx, cy - 130, 0.95],       # head
        [cx - 25, cy - 90, 0.92],   # left_shoulder
        [cx + 25, cy - 90, 0.91],   # right_shoulder
        [cx, cy - 20, 0.93],        # center_hips
        [cx - 20, cy + 30, 0.88],   # left_knee
        [cx + 20, cy + 30, 0.87],   # right_knee
        [cx - 25, cy + 90, 0.85],   # left_ankle
        [cx + 25, cy + 90, 0.84],   # right_ankle
        [cx - 60, cy + 100, 0.90],  # left_ski_tip
        [cx - 10, cy + 105, 0.89],  # left_ski_tail
        [cx + 10, cy + 100, 0.90],  # right_ski_tip
        [cx + 60, cy + 105, 0.89],  # right_ski_tail
        [cx - 50, cy - 30, 0.82],   # left_pole_tip
        [cx + 50, cy - 30, 0.81],   # right_pole_tip
    ])
    kp[:, :2] += np.random.normal(0, 3, kp[:, :2].shape)
    return kp


definition = SportDefinition(
    sport_id="skiing",
    display_name="Skiing",
    emoji="\u26f7\ufe0f",
    description="Analyze skiing technique including knee flexion, ski parallelism, hip alignment, and pole position.",
    num_keypoints=14,
    keypoints=[
        KeypointDef("head", 0, "head"),
        KeypointDef("left_shoulder", 1, "torso"),
        KeypointDef("right_shoulder", 2, "torso"),
        KeypointDef("center_hips", 3, "torso"),
        KeypointDef("left_knee", 4, "left_leg"),
        KeypointDef("right_knee", 5, "right_leg"),
        KeypointDef("left_ankle", 6, "left_leg"),
        KeypointDef("right_ankle", 7, "right_leg"),
        KeypointDef("left_ski_tip", 8, "left_ski"),
        KeypointDef("left_ski_tail", 9, "left_ski"),
        KeypointDef("right_ski_tip", 10, "right_ski"),
        KeypointDef("right_ski_tail", 11, "right_ski"),
        KeypointDef("left_pole_tip", 12, "left_pole"),
        KeypointDef("right_pole_tip", 13, "right_pole"),
    ],
    skeleton=[
        SkeletonConnection("head", "left_shoulder", "head"),
        SkeletonConnection("head", "right_shoulder", "head"),
        SkeletonConnection("left_shoulder", "right_shoulder", "torso"),
        SkeletonConnection("left_shoulder", "center_hips", "torso"),
        SkeletonConnection("right_shoulder", "center_hips", "torso"),
        SkeletonConnection("center_hips", "left_knee", "left_leg"),
        SkeletonConnection("center_hips", "right_knee", "right_leg"),
        SkeletonConnection("left_knee", "left_ankle", "left_leg"),
        SkeletonConnection("right_knee", "right_ankle", "right_leg"),
        SkeletonConnection("left_ankle", "left_ski_tip", "left_ski"),
        SkeletonConnection("left_ankle", "left_ski_tail", "left_ski"),
        SkeletonConnection("left_ski_tip", "left_ski_tail", "left_ski"),
        SkeletonConnection("right_ankle", "right_ski_tip", "right_ski"),
        SkeletonConnection("right_ankle", "right_ski_tail", "right_ski"),
        SkeletonConnection("right_ski_tip", "right_ski_tail", "right_ski"),
        SkeletonConnection("left_shoulder", "left_pole_tip", "left_pole"),
        SkeletonConnection("right_shoulder", "right_pole_tip", "right_pole"),
    ],
    model_filename="skiing_pose_model.pt",
    region_colors={
        "head": (0, 255, 255),
        "torso": (0, 255, 0),
        "left_leg": (255, 165, 0),
        "right_leg": (255, 0, 128),
        "left_ski": (255, 100, 0),
        "right_ski": (255, 100, 0),
        "left_pole": (200, 200, 200),
        "right_pole": (200, 200, 200),
    },
    coaching_categories=["Knee Flexion", "Ski Parallelism", "Hip Alignment", "Pole Position"],
    mock_keypoints_fn=_mock_keypoints,
)

SportRegistry.register(definition, SkiingCoach())
