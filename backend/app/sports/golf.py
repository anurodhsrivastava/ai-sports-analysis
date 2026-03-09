"""Golf sport definition and registration."""

import numpy as np

from .base import KeypointDef, SkeletonConnection, SportDefinition
from .registry import SportRegistry
from ..services.coach_logic.golf import GolfCoach


def _mock_keypoints(w: int, h: int) -> np.ndarray:
    cx, cy = w / 2, h / 2
    kp = np.array([
        [cx, cy - 140, 0.95],       # head
        [cx, cy - 120, 0.93],       # neck
        [cx - 20, cy - 100, 0.92],  # lead_shoulder
        [cx + 20, cy - 100, 0.92],  # trail_shoulder
        [cx - 35, cy - 65, 0.88],   # lead_elbow
        [cx + 30, cy - 60, 0.88],   # trail_elbow
        [cx - 40, cy - 30, 0.85],   # lead_wrist
        [cx + 25, cy - 25, 0.85],   # trail_wrist
        [cx - 15, cy - 20, 0.93],   # lead_hip
        [cx + 15, cy - 20, 0.93],   # trail_hip
        [cx - 18, cy + 35, 0.88],   # lead_knee
        [cx + 18, cy + 35, 0.88],   # trail_knee
    ])
    kp[:, :2] += np.random.normal(0, 3, kp[:, :2].shape)
    return kp


definition = SportDefinition(
    sport_id="golf",
    display_name="Golf",
    emoji="\u26F3",
    description="Analyze your golf swing mechanics including spine angle, hip rotation, and arm extension.",
    num_keypoints=12,
    keypoints=[
        KeypointDef("head", 0, "upper_body"),
        KeypointDef("neck", 1, "upper_body"),
        KeypointDef("lead_shoulder", 2, "upper_body"),
        KeypointDef("trail_shoulder", 3, "upper_body"),
        KeypointDef("lead_elbow", 4, "arms"),
        KeypointDef("trail_elbow", 5, "arms"),
        KeypointDef("lead_wrist", 6, "arms"),
        KeypointDef("trail_wrist", 7, "arms"),
        KeypointDef("lead_hip", 8, "lower_body"),
        KeypointDef("trail_hip", 9, "lower_body"),
        KeypointDef("lead_knee", 10, "lower_body"),
        KeypointDef("trail_knee", 11, "lower_body"),
    ],
    skeleton=[
        SkeletonConnection("head", "neck", "upper_body"),
        SkeletonConnection("neck", "lead_shoulder", "upper_body"),
        SkeletonConnection("neck", "trail_shoulder", "upper_body"),
        SkeletonConnection("lead_shoulder", "lead_elbow", "arms"),
        SkeletonConnection("lead_elbow", "lead_wrist", "arms"),
        SkeletonConnection("trail_shoulder", "trail_elbow", "arms"),
        SkeletonConnection("trail_elbow", "trail_wrist", "arms"),
        SkeletonConnection("neck", "lead_hip", "lower_body"),
        SkeletonConnection("neck", "trail_hip", "lower_body"),
        SkeletonConnection("lead_hip", "lead_knee", "lower_body"),
        SkeletonConnection("trail_hip", "trail_knee", "lower_body"),
    ],
    model_filename="golf_pose_model.pt",
    region_colors={
        "upper_body": (64, 224, 208),
        "arms": (255, 165, 0),
        "lower_body": (50, 205, 50),
    },
    coaching_categories=["Spine Angle", "Hip Rotation", "Arm Extension", "Head Movement"],
    mock_keypoints_fn=_mock_keypoints,
    inference_sample_rate=3,
)

SportRegistry.register(definition, GolfCoach())
