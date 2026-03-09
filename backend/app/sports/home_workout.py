"""Home workout sport definition and registration."""

import numpy as np

from .base import KeypointDef, SkeletonConnection, SportDefinition
from .registry import SportRegistry
from ..services.coach_logic.home_workout import HomeWorkoutCoach


def _mock_keypoints(w: int, h: int) -> np.ndarray:
    cx, cy = w / 2, h / 2
    kp = np.array([
        [cx, cy - 140, 0.95],       # head
        [cx - 25, cy - 100, 0.92],  # left_shoulder
        [cx + 25, cy - 100, 0.91],  # right_shoulder
        [cx - 45, cy - 60, 0.88],   # left_elbow
        [cx + 45, cy - 60, 0.87],   # right_elbow
        [cx - 55, cy - 30, 0.85],   # left_wrist
        [cx + 55, cy - 30, 0.84],   # right_wrist
        [cx - 15, cy - 10, 0.93],   # left_hip
        [cx + 15, cy - 10, 0.92],   # right_hip
        [cx - 20, cy + 50, 0.88],   # left_knee
        [cx + 20, cy + 50, 0.87],   # right_knee
        [cx - 20, cy + 100, 0.85],  # left_ankle
        [cx + 20, cy + 100, 0.84],  # right_ankle
    ])
    kp[:, :2] += np.random.normal(0, 3, kp[:, :2].shape)
    return kp


definition = SportDefinition(
    sport_id="home_workout",
    display_name="Home Workouts",
    emoji="\U0001f4aa",
    description="Analyze home exercises including squats, push-ups, planks, and lunges with rep counting.",
    num_keypoints=13,
    keypoints=[
        KeypointDef("head", 0, "head"),
        KeypointDef("left_shoulder", 1, "torso"),
        KeypointDef("right_shoulder", 2, "torso"),
        KeypointDef("left_elbow", 3, "left_arm"),
        KeypointDef("right_elbow", 4, "right_arm"),
        KeypointDef("left_wrist", 5, "left_arm"),
        KeypointDef("right_wrist", 6, "right_arm"),
        KeypointDef("left_hip", 7, "torso"),
        KeypointDef("right_hip", 8, "torso"),
        KeypointDef("left_knee", 9, "left_leg"),
        KeypointDef("right_knee", 10, "right_leg"),
        KeypointDef("left_ankle", 11, "left_leg"),
        KeypointDef("right_ankle", 12, "right_leg"),
    ],
    skeleton=[
        SkeletonConnection("head", "left_shoulder", "head"),
        SkeletonConnection("head", "right_shoulder", "head"),
        SkeletonConnection("left_shoulder", "right_shoulder", "torso"),
        SkeletonConnection("left_shoulder", "left_elbow", "left_arm"),
        SkeletonConnection("left_elbow", "left_wrist", "left_arm"),
        SkeletonConnection("right_shoulder", "right_elbow", "right_arm"),
        SkeletonConnection("right_elbow", "right_wrist", "right_arm"),
        SkeletonConnection("left_shoulder", "left_hip", "torso"),
        SkeletonConnection("right_shoulder", "right_hip", "torso"),
        SkeletonConnection("left_hip", "right_hip", "torso"),
        SkeletonConnection("left_hip", "left_knee", "left_leg"),
        SkeletonConnection("left_knee", "left_ankle", "left_leg"),
        SkeletonConnection("right_hip", "right_knee", "right_leg"),
        SkeletonConnection("right_knee", "right_ankle", "right_leg"),
    ],
    model_filename="home_workout_pose_model.pt",
    region_colors={
        "head": (0, 255, 255),
        "torso": (0, 255, 0),
        "left_arm": (255, 165, 0),
        "right_arm": (255, 100, 0),
        "left_leg": (255, 0, 128),
        "right_leg": (200, 0, 200),
    },
    coaching_categories=[
        "Squat Depth", "Knee Tracking", "Back Position",
        "Elbow Range", "Body Line", "Front Knee Angle", "Torso Position",
    ],
    mock_keypoints_fn=_mock_keypoints,
)

SportRegistry.register(definition, HomeWorkoutCoach())
