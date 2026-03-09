"""
Shared biomechanical analysis utilities.
Extracted from the original snowboard coach logic.
"""

import math
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

import numpy as np


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CoachingTip:
    category: str
    body_part: str
    angle_value: float
    threshold: float
    message: str
    severity: Severity
    frame_range: tuple[int, int]


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


_SEVERITY_RANK = {Severity.OK: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}


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
    merged: list[CoachingTip] = []
    for tip in tips:
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
            )
        else:
            merged.append(tip)
    return merged


def generate_coaching_summary(tips: list[CoachingTip]) -> CoachingSummaryData:
    """Distill a list of coaching tips into a concise summary."""
    if not tips:
        return CoachingSummaryData(
            overall_assessment="Excellent technique! No issues detected.",
            category_breakdowns=[],
            top_tips=[],
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
    top_tips = sorted_tips[:5]

    has_critical = any(t.severity == Severity.CRITICAL for t in tips)
    if has_critical:
        overall_assessment = "Several issues need attention \u2014 focus on the critical items below."
    else:
        overall_assessment = "Solid technique overall, with a few areas to refine."

    return CoachingSummaryData(
        overall_assessment=overall_assessment,
        category_breakdowns=breakdowns,
        top_tips=top_tips,
    )
