"""
Shared biomechanical analysis utilities.
Extracted from the original snowboard coach logic.
"""

import math
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

import numpy as np


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class Confidence(str, Enum):
    HIGH = "high"
    LOW = "low"


@dataclass
class CoachingTip:
    category: str
    body_part: str
    angle_value: float
    threshold: float
    message: str
    severity: Severity
    frame_range: tuple[int, int]
    message_key: str = ""
    message_params: dict = field(default_factory=dict)
    confidence: Confidence = Confidence.HIGH
    score_weight: float = 1.0


@dataclass
class CategoryBreakdownData:
    category: str
    count: int
    avg_angle_value: float
    worst_severity: Severity


@dataclass
class CoachingSummaryData:
    overall_assessment: str
    category_breakdowns: list[CategoryBreakdownData]
    top_tips: list[CoachingTip]
    overall_assessment_key: str = ""
    overall_score: int = 0
    overall_grade: str = ""


_SEVERITY_RANK = {Severity.OK: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}

# Grade ranges
_GRADE_RANGES = [
    (90, 100, "A"),
    (80, 89, "B"),
    (65, 79, "C"),
    (50, 64, "D"),
    (35, 49, "E"),
    (0, 34, "F"),
]


def _score_to_grade(score: int) -> str:
    for low, high, grade in _GRADE_RANGES:
        if low <= score <= high:
            return grade
    return "F"


def compute_angle(a: np.ndarray, vertex: np.ndarray, c: np.ndarray) -> float:
    """Compute angle at vertex using Law of Cosines. Returns degrees."""
    va = a - vertex
    vc = c - vertex

    dot = float(np.dot(va, vc))
    mag_a = float(np.linalg.norm(va))
    mag_c = float(np.linalg.norm(vc))

    if mag_a == 0 or mag_c == 0:
        return 0.0

    cos_angle = np.clip(dot / (mag_a * mag_c), -1.0, 1.0)
    return math.degrees(math.acos(cos_angle))


def compute_vector_angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute angle between two 2D vectors in degrees."""
    dot = float(np.dot(v1, v2))
    mag1 = float(np.linalg.norm(v1))
    mag2 = float(np.linalg.norm(v2))

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = np.clip(dot / (mag1 * mag2), -1.0, 1.0)
    return math.degrees(math.acos(cos_angle))


def get_point(keypoints: np.ndarray, name: str, bodypart_indices: dict[str, int]) -> np.ndarray:
    """Extract a 2D point from the keypoints array by bodypart name."""
    idx = bodypart_indices[name]
    return keypoints[idx, :2]


def merge_consecutive_tips(tips: list[CoachingTip], max_gap: int = 5) -> list[CoachingTip]:
    """Merge consecutive tips of the same category + body_part + severity."""
    # Sort by category + body_part + severity + frame to enable merging
    sorted_tips = sorted(tips, key=lambda t: (t.category, t.body_part, t.severity.value, t.frame_range[0]))
    merged: list[CoachingTip] = []
    for tip in sorted_tips:
        if merged and (
            merged[-1].category == tip.category
            and merged[-1].body_part == tip.body_part
            and merged[-1].severity == tip.severity
            and tip.frame_range[0] - merged[-1].frame_range[1] <= max_gap
        ):
            merged[-1] = CoachingTip(
                category=tip.category,
                body_part=tip.body_part,
                angle_value=max(merged[-1].angle_value, tip.angle_value),
                threshold=tip.threshold,
                message=tip.message,
                severity=tip.severity,
                frame_range=(merged[-1].frame_range[0], tip.frame_range[1]),
                message_key=tip.message_key,
                message_params=tip.message_params,
            )
        else:
            merged.append(tip)
    return merged


def _compute_numeric_score(tips: list[CoachingTip], total_frames: int) -> int:
    """Compute a 0-100 score based on per-category frame coverage and severity.

    Tips with score_weight < 1.0 (e.g. equipment-based tips) contribute less
    to the penalty, so body-based feedback drives the score.
    """
    if not tips or total_frames == 0:
        return 100

    category_weight = {
        "Knee Flexion": 1.2,
        "Shoulder Alignment": 1.0,
        "Stance Width": 0.8,
    }
    max_penalty_per_category = 35.0

    groups: dict[str, list[CoachingTip]] = defaultdict(list)
    for tip in tips:
        groups[tip.category].append(tip)

    score = 100.0
    for category, cat_tips in groups.items():
        weight = category_weight.get(category, 1.0)
        # Apply tip-level score_weight (equipment tips have lower weight)
        avg_score_weight = float(np.mean([t.score_weight for t in cat_tips]))

        affected_frames = 0
        for tip in cat_tips:
            affected_frames += tip.frame_range[1] - tip.frame_range[0] + 1
        coverage = min(affected_frames / max(total_frames, 1), 1.0)

        overshoots = []
        for tip in cat_tips:
            if category == "Stance Width":
                ov = max(0, tip.threshold - tip.angle_value) / max(tip.threshold, 1)
            else:
                ov = max(0, tip.angle_value - tip.threshold) / max(tip.threshold, 1)
            overshoots.append(ov)
        avg_overshoot = float(np.mean(overshoots)) if overshoots else 0.0

        has_critical = any(t.severity == Severity.CRITICAL for t in cat_tips)
        severity_mult = 1.2 if has_critical else 0.6

        penalty = max_penalty_per_category * coverage * severity_mult * (1.0 + avg_overshoot) * weight * avg_score_weight
        penalty = min(penalty, max_penalty_per_category * weight * avg_score_weight)
        score -= penalty

    return max(0, min(100, round(score)))


def generate_coaching_summary(tips: list[CoachingTip], total_frames: int = 0) -> CoachingSummaryData:
    """Distill a list of coaching tips into a concise summary with score and grade."""
    if not tips:
        return CoachingSummaryData(
            overall_assessment="Excellent technique! No issues detected.",
            category_breakdowns=[],
            top_tips=[],
            overall_assessment_key="coaching.summary.excellent",
            overall_score=100,
            overall_grade="A",
        )

    by_category: dict[str, list[CoachingTip]] = defaultdict(list)
    for t in tips:
        by_category[t.category].append(t)

    breakdowns: list[CategoryBreakdownData] = []
    for cat, cat_tips in sorted(by_category.items()):
        angles = [t.angle_value for t in cat_tips]
        worst = max(cat_tips, key=lambda t: _SEVERITY_RANK[t.severity])
        breakdowns.append(
            CategoryBreakdownData(
                category=cat,
                count=len(cat_tips),
                avg_angle_value=round(float(np.mean(angles)), 1),
                worst_severity=worst.severity,
            )
        )

    sorted_tips = sorted(
        tips,
        key=lambda t: (
            -_SEVERITY_RANK[t.severity],
            -(t.frame_range[1] - t.frame_range[0]),
        ),
    )
    # Diversify top tips: max 2 per category to avoid repetition
    top_tips: list[CoachingTip] = []
    cat_counts: dict[str, int] = {}
    for t in sorted_tips:
        if len(top_tips) >= 5:
            break
        c = cat_counts.get(t.category, 0)
        if c < 2:
            top_tips.append(t)
            cat_counts[t.category] = c + 1

    # Compute numeric score
    score = _compute_numeric_score(tips, total_frames)
    grade = _score_to_grade(score)

    if grade in ("A", "B"):
        assessment = "Solid technique overall, with a few areas to refine."
        assessment_key = "coaching.summary.solid"
    elif grade == "C":
        assessment = "Decent form with some areas that need work."
        assessment_key = "coaching.summary.decent"
    else:
        assessment = "Several issues need attention \u2014 focus on the critical items below."
        assessment_key = "coaching.summary.needsAttention"

    return CoachingSummaryData(
        overall_assessment=assessment,
        category_breakdowns=breakdowns,
        top_tips=top_tips,
        overall_assessment_key=assessment_key,
        overall_score=score,
        overall_grade=grade,
    )
