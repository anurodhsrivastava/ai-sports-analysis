"""Golf biomechanical analysis — spine angle, hip rotation, arm extension, head movement."""

import math

import numpy as np

from .base import (
    CoachingTip,
    CoachingSummaryData,
    Severity,
    compute_angle,
    compute_vector_angle,
    generate_coaching_summary,
    get_point,
    merge_consecutive_tips,
)

BODYPART_INDICES = {
    "head": 0,
    "neck": 1,
    "lead_shoulder": 2,
    "trail_shoulder": 3,
    "lead_elbow": 4,
    "trail_elbow": 5,
    "lead_wrist": 6,
    "trail_wrist": 7,
    "lead_hip": 8,
    "trail_hip": 9,
    "lead_knee": 10,
    "trail_knee": 11,
}


def _p(kp: np.ndarray, name: str) -> np.ndarray:
    return get_point(kp, name, BODYPART_INDICES)


def analyze_spine_angle(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Angle of neck→midpoint(lead_hip, trail_hip) from vertical. Ideal 30-45° forward tilt."""
    neck = _p(kp, "neck")
    lead_hip = _p(kp, "lead_hip")
    trail_hip = _p(kp, "trail_hip")
    hip_mid = (lead_hip + trail_hip) / 2.0

    spine_vec = hip_mid - neck
    vertical = np.array([0.0, 1.0])  # Down in image coords
    angle = compute_vector_angle(spine_vec, vertical)

    if angle < 15 or angle > 60:
        desc = "too upright" if angle < 15 else "too hunched over"
        return CoachingTip(
            category="Spine Angle", body_part="torso", angle_value=round(angle, 1),
            threshold=15.0 if angle < 15 else 60.0,
            message=f"Your spine angle is {angle:.0f}° ({desc}). Maintain a 30-45° forward tilt at address for optimal posture.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle < 25 or angle > 50:
        desc = "slightly upright" if angle < 25 else "leaning too far forward"
        return CoachingTip(
            category="Spine Angle", body_part="torso", angle_value=round(angle, 1),
            threshold=25.0 if angle < 25 else 50.0,
            message=f"Your spine angle is {angle:.0f}° ({desc}). Ideal forward tilt is 30-45° at address.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_hip_rotation(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Angle between shoulder line and hip line. Ideal 40-50° separation during backswing."""
    lead_shoulder = _p(kp, "lead_shoulder")
    trail_shoulder = _p(kp, "trail_shoulder")
    lead_hip = _p(kp, "lead_hip")
    trail_hip = _p(kp, "trail_hip")

    shoulder_vec = trail_shoulder - lead_shoulder
    hip_vec = trail_hip - lead_hip

    # Angle between shoulder line and hip line
    angle = compute_vector_angle(shoulder_vec, hip_vec)

    if angle > 25:
        return CoachingTip(
            category="Hip Rotation", body_part="hip", angle_value=round(angle, 1),
            threshold=25.0,
            message=f"Shoulder-hip separation is {angle:.0f}° — excessive rotation differential. Aim for 40-50° at the top of your backswing, but this may indicate over-rotation or early extension.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 15:
        return CoachingTip(
            category="Hip Rotation", body_part="hip", angle_value=round(angle, 1),
            threshold=15.0,
            message=f"Shoulder-hip separation is {angle:.0f}°. Monitor your hip turn — ideal separation is 40-50° at the top of the backswing.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_arm_extension(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Lead arm angle: lead_shoulder→lead_elbow→lead_wrist. Ideal ~170° at impact."""
    lead_shoulder = _p(kp, "lead_shoulder")
    lead_elbow = _p(kp, "lead_elbow")
    lead_wrist = _p(kp, "lead_wrist")

    angle = compute_angle(lead_shoulder, lead_elbow, lead_wrist)

    if angle < 140:
        return CoachingTip(
            category="Arm Extension", body_part="lead_elbow", angle_value=round(angle, 1),
            threshold=140.0,
            message=f"Lead arm is severely bent at {angle:.0f}° (chicken wing). Keep your lead arm nearly straight (~170°) through impact for consistent contact.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle < 155:
        return CoachingTip(
            category="Arm Extension", body_part="lead_elbow", angle_value=round(angle, 1),
            threshold=155.0,
            message=f"Lead arm angle is {angle:.0f}° — slightly bent. Aim for ~170° (nearly straight) at impact for better extension and power.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_head_movement(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Track head position relative to midpoint of hips."""
    head = _p(kp, "head")
    neck = _p(kp, "neck")
    lead_hip = _p(kp, "lead_hip")
    trail_hip = _p(kp, "trail_hip")
    hip_mid = (lead_hip + trail_hip) / 2.0

    torso_length = float(np.linalg.norm(neck - hip_mid))
    if torso_length == 0:
        return None

    # Lateral (horizontal) movement: head x vs hip midpoint x
    lateral_ratio = abs(float(head[0] - hip_mid[0])) / torso_length

    if lateral_ratio > 0.15:
        return CoachingTip(
            category="Head Movement", body_part="head", angle_value=round(lateral_ratio, 3),
            threshold=0.15,
            message=f"Significant head sway detected (ratio {lateral_ratio:.2f}). Keep your head steady as a pivot point — excessive lateral movement causes inconsistent contact.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif lateral_ratio > 0.08:
        return CoachingTip(
            category="Head Movement", body_part="head", angle_value=round(lateral_ratio, 3),
            threshold=0.08,
            message=f"Slight head sway detected (ratio {lateral_ratio:.2f}). Try to keep your head centered over the ball throughout the swing.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


class GolfCoach:
    def __init__(self) -> None:
        pass

    def analyze_frame(self, kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
        tips: list[CoachingTip] = []
        for fn in (analyze_spine_angle, analyze_hip_rotation, analyze_arm_extension, analyze_head_movement):
            tip = fn(kp, frame_idx)
            if tip:
                tips.append(tip)
        return tips

    def analyze_sequence(
        self, all_keypoints: list[np.ndarray], frame_indices: list[int] | None = None
    ) -> list[CoachingTip]:
        if frame_indices is None:
            frame_indices = list(range(len(all_keypoints)))

        raw: list[CoachingTip] = []
        for kp, idx in zip(all_keypoints, frame_indices):
            raw.extend(self.analyze_frame(kp, idx))
        return merge_consecutive_tips(raw)

    def compute_keypoints_summary(self, all_keypoints: list[np.ndarray]) -> dict[str, float | int | str | None]:
        spine_angles, arm_angles, head_ratios = [], [], []
        for kp in all_keypoints:
            neck = _p(kp, "neck")
            lead_hip = _p(kp, "lead_hip")
            trail_hip = _p(kp, "trail_hip")
            hip_mid = (lead_hip + trail_hip) / 2.0
            spine_vec = hip_mid - neck
            vertical = np.array([0.0, 1.0])
            spine_angles.append(compute_vector_angle(spine_vec, vertical))

            lead_shoulder = _p(kp, "lead_shoulder")
            lead_elbow = _p(kp, "lead_elbow")
            lead_wrist = _p(kp, "lead_wrist")
            arm_angles.append(compute_angle(lead_shoulder, lead_elbow, lead_wrist))

            head = _p(kp, "head")
            torso_length = float(np.linalg.norm(neck - hip_mid))
            if torso_length > 0:
                head_ratios.append(abs(float(head[0] - hip_mid[0])) / torso_length)

        return {
            "total_frames_analyzed": len(all_keypoints),
            "avg_spine_angle": round(float(np.mean(spine_angles)), 1) if spine_angles else None,
            "avg_arm_extension": round(float(np.mean(arm_angles)), 1) if arm_angles else None,
            "head_stability": round(float(np.mean(head_ratios)), 3) if head_ratios else None,
        }

    def generate_coaching_summary(self, tips: list[CoachingTip]) -> CoachingSummaryData:
        return generate_coaching_summary(tips)
