"""Sport definition base types."""

from dataclasses import dataclass, field
from typing import Callable, Protocol

import numpy as np


@dataclass(frozen=True)
class KeypointDef:
    name: str
    index: int
    region: str


@dataclass(frozen=True)
class SkeletonConnection:
    from_keypoint: str
    to_keypoint: str
    region: str


@dataclass
class SportDefinition:
    sport_id: str
    display_name: str
    emoji: str
    description: str
    num_keypoints: int
    keypoints: list[KeypointDef]
    skeleton: list[SkeletonConnection]
    input_size: tuple[int, int] = (256, 384)
    model_filename: str = ""
    region_colors: dict[str, tuple[int, int, int]] = field(default_factory=dict)
    coaching_categories: list[str] = field(default_factory=list)
    mock_keypoints_fn: Callable[[int, int], np.ndarray] | None = None
    inference_sample_rate: int | None = None

    @property
    def bodypart_indices(self) -> dict[str, int]:
        return {kp.name: kp.index for kp in self.keypoints}

    @property
    def skeleton_pairs(self) -> list[tuple[str, str]]:
        return [(c.from_keypoint, c.to_keypoint) for c in self.skeleton]


class SportCoach(Protocol):
    def analyze_frame(self, keypoints: np.ndarray, frame_idx: int) -> list: ...
    def analyze_sequence(
        self, all_keypoints: list[np.ndarray], frame_indices: list[int] | None = None
    ) -> list: ...
    def compute_keypoints_summary(self, all_keypoints: list[np.ndarray]) -> dict[str, float | int | str | None]: ...
    def generate_coaching_summary(self, tips: list, total_frames: int = 0) -> object: ...
