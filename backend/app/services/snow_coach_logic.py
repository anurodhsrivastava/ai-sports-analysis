"""Compatibility shim for tests that import from the old monolithic module.

Delegates to the multi-sport coach_logic package.
"""

from .coach_logic.base import (
    CoachingTip,
    CoachingSummaryData,
    Severity,
    compute_angle,
    compute_vector_angle,
    generate_coaching_summary,
    merge_consecutive_tips,
)
from .coach_logic.snowboard import (
    BODYPART_INDICES,
    SnowboardCoach,
    analyze_knee_flexion,
    analyze_shoulder_alignment,
    analyze_stance_width,
)

# Module-level convenience functions that delegate to SnowboardCoach instance
_coach = SnowboardCoach()


def analyze_frame(kp, frame_idx: int) -> list[CoachingTip]:
    return _coach.analyze_frame(kp, frame_idx)


def analyze_sequence(all_keypoints, frame_indices=None) -> list[CoachingTip]:
    return _coach.analyze_sequence(all_keypoints, frame_indices)
