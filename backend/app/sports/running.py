"""Running sport definition and registration."""

import numpy as np

from .base import KeypointDef, SkeletonConnection, SportDefinition
from .registry import SportRegistry
from ..services.coach_logic.running import RunningCoach


def _mock_keypoints(w: int, h: int) -> np.ndarray:
    cx, cy = w / 2, h / 2
    kp = np.array([
        [cx, cy - 140, 0.95],       # head
        [cx, cy - 115, 0.93],       # neck
        [cx - 15, cy - 100, 0.92],  # shoulder
        [cx - 25, cy - 60, 0.88],   # elbow
        [cx - 15, cy - 35, 0.85],   # wrist
        [cx + 5, cy - 20, 0.93],    # hip
        [cx - 5, cy + 35, 0.88],    # knee
        [cx - 10, cy + 90, 0.85],   # ankle
        [cx - 25, cy + 100, 0.84],  # toe
        [cx + 5, cy + 95, 0.83],    # heel
        [cx - 5, cy - 60, 0.90],    # mid_torso
        [cx + 5, cy - 10, 0.91],    # pelvis
    ])
    kp[:, :2] += np.random.normal(0, 3, kp[:, :2].shape)
    return kp


definition = SportDefinition(
    sport_id="running",
    display_name="Running",
    emoji="\U0001f3c3",
    description="Analyze running form including foot strike, forward lean, arm swing, and cadence.",
    num_keypoints=12,
    keypoints=[
        KeypointDef("head", 0, "head"),
        KeypointDef("neck", 1, "head"),
        KeypointDef("shoulder", 2, "torso"),
        KeypointDef("elbow", 3, "arm"),
        KeypointDef("wrist", 4, "arm"),
        KeypointDef("hip", 5, "torso"),
        KeypointDef("knee", 6, "leg"),
        KeypointDef("ankle", 7, "leg"),
        KeypointDef("toe", 8, "foot"),
        KeypointDef("heel", 9, "foot"),
        KeypointDef("mid_torso", 10, "torso"),
        KeypointDef("pelvis", 11, "torso"),
    ],
    skeleton=[
        SkeletonConnection("head", "neck", "head"),
        SkeletonConnection("neck", "shoulder", "torso"),
        SkeletonConnection("shoulder", "elbow", "arm"),
        SkeletonConnection("elbow", "wrist", "arm"),
        SkeletonConnection("neck", "mid_torso", "torso"),
        SkeletonConnection("mid_torso", "hip", "torso"),
        SkeletonConnection("hip", "pelvis", "torso"),
        SkeletonConnection("hip", "knee", "leg"),
        SkeletonConnection("knee", "ankle", "leg"),
        SkeletonConnection("ankle", "toe", "foot"),
        SkeletonConnection("ankle", "heel", "foot"),
    ],
    model_filename="running_pose_model.pt",
    region_colors={
        "head": (0, 255, 255),
        "torso": (0, 255, 0),
        "arm": (255, 165, 0),
        "leg": (255, 0, 128),
        "foot": (255, 100, 0),
    },
    coaching_categories=["Foot Strike", "Forward Lean", "Arm Swing", "Cadence"],
    mock_keypoints_fn=_mock_keypoints,
    inference_sample_rate=3,
)

SportRegistry.register(definition, RunningCoach())
