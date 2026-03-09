"""Yoga sport definition and registration."""

import numpy as np

from .base import KeypointDef, SkeletonConnection, SportDefinition
from .registry import SportRegistry
from ..services.coach_logic.yoga import YogaCoach


def _mock_keypoints(w: int, h: int) -> np.ndarray:
    cx, cy = w / 2, h / 2
    kp = np.array([
        [cx, cy - 140, 0.95],       # head
        [cx, cy - 120, 0.93],       # neck
        [cx - 20, cy - 100, 0.92],  # left_shoulder
        [cx + 20, cy - 100, 0.92],  # right_shoulder
        [cx - 25, cy - 60, 0.88],   # left_elbow
        [cx + 25, cy - 60, 0.88],   # right_elbow
        [cx - 20, cy - 30, 0.85],   # left_wrist
        [cx + 20, cy - 30, 0.85],   # right_wrist
        [cx - 15, cy + 10, 0.93],   # left_hip
        [cx + 15, cy + 10, 0.93],   # right_hip
        [cx - 15, cy + 60, 0.88],   # left_knee
        [cx + 15, cy + 60, 0.88],   # right_knee
        [cx - 15, cy + 110, 0.85],  # left_ankle
        [cx + 15, cy + 110, 0.85],  # right_ankle
        [cx, cy + 0, 0.91],         # pelvis
    ])
    kp[:, :2] += np.random.normal(0, 3, kp[:, :2].shape)
    return kp


definition = SportDefinition(
    sport_id="yoga",
    display_name="Yoga",
    emoji="\U0001f9d8",
    description="Analyze yoga poses for alignment, balance, joint safety, and left-right symmetry.",
    num_keypoints=15,
    keypoints=[
        KeypointDef("head", 0, "upper_body"),
        KeypointDef("neck", 1, "upper_body"),
        KeypointDef("left_shoulder", 2, "upper_body"),
        KeypointDef("right_shoulder", 3, "upper_body"),
        KeypointDef("left_elbow", 4, "arms"),
        KeypointDef("right_elbow", 5, "arms"),
        KeypointDef("left_wrist", 6, "arms"),
        KeypointDef("right_wrist", 7, "arms"),
        KeypointDef("left_hip", 8, "lower_body"),
        KeypointDef("right_hip", 9, "lower_body"),
        KeypointDef("left_knee", 10, "lower_body"),
        KeypointDef("right_knee", 11, "lower_body"),
        KeypointDef("left_ankle", 12, "lower_body"),
        KeypointDef("right_ankle", 13, "lower_body"),
        KeypointDef("pelvis", 14, "core"),
    ],
    skeleton=[
        SkeletonConnection("head", "neck", "upper_body"),
        SkeletonConnection("neck", "left_shoulder", "upper_body"),
        SkeletonConnection("neck", "right_shoulder", "upper_body"),
        SkeletonConnection("left_shoulder", "left_elbow", "arms"),
        SkeletonConnection("left_elbow", "left_wrist", "arms"),
        SkeletonConnection("right_shoulder", "right_elbow", "arms"),
        SkeletonConnection("right_elbow", "right_wrist", "arms"),
        SkeletonConnection("neck", "pelvis", "core"),
        SkeletonConnection("pelvis", "left_hip", "lower_body"),
        SkeletonConnection("pelvis", "right_hip", "lower_body"),
        SkeletonConnection("left_hip", "left_knee", "lower_body"),
        SkeletonConnection("left_knee", "left_ankle", "lower_body"),
        SkeletonConnection("right_hip", "right_knee", "lower_body"),
        SkeletonConnection("right_knee", "right_ankle", "lower_body"),
    ],
    model_filename="yoga_pose_model.pt",
    region_colors={
        "upper_body": (147, 112, 219),
        "arms": (255, 182, 193),
        "lower_body": (144, 238, 144),
        "core": (255, 215, 0),
    },
    coaching_categories=["Alignment", "Balance", "Joint Angles", "Symmetry"],
    mock_keypoints_fn=_mock_keypoints,
    inference_sample_rate=1,
)

SportRegistry.register(definition, YogaCoach())
