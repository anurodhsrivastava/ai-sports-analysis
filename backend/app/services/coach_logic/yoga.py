"""Yoga pose analysis — alignment, balance, joint angles, symmetry."""

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
    "left_shoulder": 2,
    "right_shoulder": 3,
    "left_elbow": 4,
    "right_elbow": 5,
    "left_wrist": 6,
    "right_wrist": 7,
    "left_hip": 8,
    "right_hip": 9,
    "left_knee": 10,
    "right_knee": 11,
    "left_ankle": 12,
    "right_ankle": 13,
    "pelvis": 14,
}


def _p(kp: np.ndarray, name: str) -> np.ndarray:
    return get_point(kp, name, BODYPART_INDICES)


def analyze_alignment(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Check spine alignment — angle of head→neck→pelvis from vertical."""
    head = _p(kp, "head")
    neck = _p(kp, "neck")
    pelvis = _p(kp, "pelvis")

    spine_vec = head - pelvis
    vertical = np.array([0.0, -1.0])  # Up in image coords
    angle = compute_vector_angle(spine_vec, vertical)

    if angle > 25:
        return CoachingTip(
            category="Alignment", body_part="spine", angle_value=round(angle, 1),
            threshold=25.0,
            message=f"Your spine is {angle:.0f}\u00b0 from vertical \u2014 significant misalignment reduces pose effectiveness and risks strain. Engage your core and stack your vertebrae.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 15:
        return CoachingTip(
            category="Alignment", body_part="spine", angle_value=round(angle, 1),
            threshold=15.0,
            message=f"Spine alignment is {angle:.0f}\u00b0 from vertical. For standing poses, aim for less than 10\u00b0. Focus on lengthening through the crown of your head.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_balance(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Check weight distribution by comparing left vs right ankle-to-hip distances."""
    left_ankle = _p(kp, "left_ankle")
    right_ankle = _p(kp, "right_ankle")
    left_hip = _p(kp, "left_hip")
    right_hip = _p(kp, "right_hip")

    left_dist = float(np.linalg.norm(left_ankle - left_hip))
    right_dist = float(np.linalg.norm(right_ankle - right_hip))

    avg_dist = (left_dist + right_dist) / 2
    if avg_dist == 0:
        return None

    asymmetry = abs(left_dist - right_dist) / avg_dist * 100

    if asymmetry > 25:
        return CoachingTip(
            category="Balance", body_part="ankles", angle_value=round(asymmetry, 1),
            threshold=25.0,
            message=f"Weight distribution is {asymmetry:.0f}% asymmetric \u2014 uneven loading stresses joints and reduces stability. Press evenly through both feet.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif asymmetry > 15:
        return CoachingTip(
            category="Balance", body_part="ankles", angle_value=round(asymmetry, 1),
            threshold=15.0,
            message=f"Slight weight imbalance detected ({asymmetry:.0f}% asymmetry). Engage both legs equally and activate your stabiliser muscles.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_joint_angles(kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
    """Check knee hyperextension and elbow angles."""
    tips: list[CoachingTip] = []

    # Check both knees for hyperextension
    for side in ("left", "right"):
        hip = _p(kp, f"{side}_hip")
        knee = _p(kp, f"{side}_knee")
        ankle = _p(kp, f"{side}_ankle")
        knee_angle = compute_angle(hip, knee, ankle)

        if knee_angle > 195:
            tips.append(CoachingTip(
                category="Joint Angles", body_part=f"{side}_knee",
                angle_value=round(knee_angle, 1), threshold=195.0,
                message=f"Your {side} knee is severely hyperextended at {knee_angle:.0f}\u00b0 \u2014 this risks joint damage. Maintain a micro-bend in standing poses.",
                severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
            ))
        elif knee_angle > 185:
            tips.append(CoachingTip(
                category="Joint Angles", body_part=f"{side}_knee",
                angle_value=round(knee_angle, 1), threshold=185.0,
                message=f"Your {side} knee is slightly hyperextended at {knee_angle:.0f}\u00b0. Keep a soft micro-bend to protect the joint.",
                severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
            ))

    # Check elbow angles
    for side in ("left", "right"):
        shoulder = _p(kp, f"{side}_shoulder")
        elbow = _p(kp, f"{side}_elbow")
        wrist = _p(kp, f"{side}_wrist")
        elbow_angle = compute_angle(shoulder, elbow, wrist)

        if elbow_angle > 195:
            tips.append(CoachingTip(
                category="Joint Angles", body_part=f"{side}_elbow",
                angle_value=round(elbow_angle, 1), threshold=195.0,
                message=f"Your {side} elbow is hyperextended at {elbow_angle:.0f}\u00b0. Keep a slight bend to avoid joint strain.",
                severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
            ))

    return tips


def analyze_symmetry(kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
    """Compare left side angles vs right side angles."""
    tips: list[CoachingTip] = []

    # Compare shoulder→elbow→wrist angles
    left_elbow_angle = compute_angle(
        _p(kp, "left_shoulder"), _p(kp, "left_elbow"), _p(kp, "left_wrist")
    )
    right_elbow_angle = compute_angle(
        _p(kp, "right_shoulder"), _p(kp, "right_elbow"), _p(kp, "right_wrist")
    )
    arm_diff = abs(left_elbow_angle - right_elbow_angle)

    if arm_diff > 20:
        tips.append(CoachingTip(
            category="Symmetry", body_part="elbows",
            angle_value=round(arm_diff, 1), threshold=20.0,
            message=f"Arm angles differ by {arm_diff:.0f}\u00b0 \u2014 this asymmetry creates muscular imbalances. Use a mirror to match both sides.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        ))
    elif arm_diff > 10:
        tips.append(CoachingTip(
            category="Symmetry", body_part="elbows",
            angle_value=round(arm_diff, 1), threshold=10.0,
            message=f"Arm angles differ by {arm_diff:.0f}\u00b0. Work on matching both sides for balanced muscle development.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        ))

    # Compare hip→knee→ankle angles
    left_knee_angle = compute_angle(
        _p(kp, "left_hip"), _p(kp, "left_knee"), _p(kp, "left_ankle")
    )
    right_knee_angle = compute_angle(
        _p(kp, "right_hip"), _p(kp, "right_knee"), _p(kp, "right_ankle")
    )
    leg_diff = abs(left_knee_angle - right_knee_angle)

    if leg_diff > 20:
        tips.append(CoachingTip(
            category="Symmetry", body_part="knees",
            angle_value=round(leg_diff, 1), threshold=20.0,
            message=f"Leg angles differ by {leg_diff:.0f}\u00b0 \u2014 asymmetric poses create imbalances over time. Hold your weaker side longer.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        ))
    elif leg_diff > 10:
        tips.append(CoachingTip(
            category="Symmetry", body_part="knees",
            angle_value=round(leg_diff, 1), threshold=10.0,
            message=f"Leg angles differ by {leg_diff:.0f}\u00b0. Focus on equal engagement on both sides.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        ))

    return tips


class YogaCoach:
    def __init__(self) -> None:
        pass

    def analyze_frame(self, kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
        tips: list[CoachingTip] = []
        for fn in (analyze_alignment, analyze_balance):
            tip = fn(kp, frame_idx)
            if tip:
                tips.append(tip)
        tips.extend(analyze_joint_angles(kp, frame_idx))
        tips.extend(analyze_symmetry(kp, frame_idx))
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
        spine_angles, knee_angles, balance_scores = [], [], []
        arm_diffs, leg_diffs = [], []

        for kp in all_keypoints:
            # Spine alignment
            head = _p(kp, "head")
            pelvis = _p(kp, "pelvis")
            spine_vec = head - pelvis
            vertical = np.array([0.0, -1.0])
            spine_angles.append(compute_vector_angle(spine_vec, vertical))

            # Balance
            left_dist = float(np.linalg.norm(_p(kp, "left_ankle") - _p(kp, "left_hip")))
            right_dist = float(np.linalg.norm(_p(kp, "right_ankle") - _p(kp, "right_hip")))
            avg_dist = (left_dist + right_dist) / 2
            if avg_dist > 0:
                balance_scores.append(100 - abs(left_dist - right_dist) / avg_dist * 100)

            # Knee angles (average of both sides)
            for side in ("left", "right"):
                knee_angle = compute_angle(
                    _p(kp, f"{side}_hip"), _p(kp, f"{side}_knee"), _p(kp, f"{side}_ankle")
                )
                knee_angles.append(knee_angle)

            # Symmetry — arm diff
            left_elbow_angle = compute_angle(
                _p(kp, "left_shoulder"), _p(kp, "left_elbow"), _p(kp, "left_wrist")
            )
            right_elbow_angle = compute_angle(
                _p(kp, "right_shoulder"), _p(kp, "right_elbow"), _p(kp, "right_wrist")
            )
            arm_diffs.append(abs(left_elbow_angle - right_elbow_angle))

            left_knee_angle = compute_angle(
                _p(kp, "left_hip"), _p(kp, "left_knee"), _p(kp, "left_ankle")
            )
            right_knee_angle = compute_angle(
                _p(kp, "right_hip"), _p(kp, "right_knee"), _p(kp, "right_ankle")
            )
            leg_diffs.append(abs(left_knee_angle - right_knee_angle))

        symmetry_diffs = arm_diffs + leg_diffs
        symmetry_score = round(100 - float(np.mean(symmetry_diffs)), 1) if symmetry_diffs else None

        return {
            "total_frames_analyzed": len(all_keypoints),
            "avg_spine_alignment": round(float(np.mean(spine_angles)), 1) if spine_angles else None,
            "balance_score": round(float(np.mean(balance_scores)), 1) if balance_scores else None,
            "avg_knee_angle": round(float(np.mean(knee_angles)), 1) if knee_angles else None,
            "symmetry_score": symmetry_score,
        }

    def generate_coaching_summary(self, tips: list[CoachingTip]) -> CoachingSummaryData:
        return generate_coaching_summary(tips)
