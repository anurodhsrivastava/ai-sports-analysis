"""Running biomechanical analysis — foot strike, forward lean, arm swing, cadence."""

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
    "shoulder": 2,
    "elbow": 3,
    "wrist": 4,
    "hip": 5,
    "knee": 6,
    "ankle": 7,
    "toe": 8,
    "heel": 9,
    "mid_torso": 10,
    "pelvis": 11,
}


def _p(kp: np.ndarray, name: str) -> np.ndarray:
    return get_point(kp, name, BODYPART_INDICES)


def analyze_foot_strike(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Overstriding ratio: horizontal distance ankle→hip / torso length."""
    ankle = _p(kp, "ankle")
    hip = _p(kp, "hip")
    neck = _p(kp, "neck")

    torso_length = float(np.linalg.norm(hip - neck))
    if torso_length == 0:
        return None

    # Horizontal distance (x-axis only for side-view)
    overstride = abs(float(ankle[0] - hip[0])) / torso_length

    if overstride > 0.6:
        return CoachingTip(
            category="Foot Strike", body_part="ankle", angle_value=round(overstride, 2),
            threshold=0.6,
            message=f"You're significantly overstriding (ratio {overstride:.2f}). Land with your foot closer to beneath your hips to reduce braking force and injury risk.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif overstride > 0.4:
        return CoachingTip(
            category="Foot Strike", body_part="ankle", angle_value=round(overstride, 2),
            threshold=0.4,
            message=f"Slight overstriding detected (ratio {overstride:.2f}). Try shortening your stride and increasing cadence.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_forward_lean(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Torso angle from vertical."""
    neck = _p(kp, "neck")
    hip = _p(kp, "hip")
    torso_vec = neck - hip
    vertical = np.array([0.0, -1.0])  # Up in image coords
    angle = compute_vector_angle(torso_vec, vertical)

    if angle > 25 or angle < 0:
        return CoachingTip(
            category="Forward Lean", body_part="torso", angle_value=round(angle, 1),
            threshold=25.0,
            message=f"Your torso lean is {angle:.0f}\u00b0 from vertical \u2014 too much forward lean increases lower back stress. Aim for a slight 5-15\u00b0 forward lean.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle < 3 or angle > 20:
        severity_msg = "too upright" if angle < 3 else "leaning too far forward"
        return CoachingTip(
            category="Forward Lean", body_part="torso", angle_value=round(angle, 1),
            threshold=3.0 if angle < 3 else 20.0,
            message=f"You're {severity_msg} at {angle:.0f}\u00b0. A slight 5-15\u00b0 forward lean is ideal for efficient running.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_arm_swing(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    """Elbow angle check."""
    shoulder = _p(kp, "shoulder")
    elbow = _p(kp, "elbow")
    wrist = _p(kp, "wrist")
    angle = compute_angle(shoulder, elbow, wrist)

    if angle > 120 or angle < 70:
        return CoachingTip(
            category="Arm Swing", body_part="elbow", angle_value=round(angle, 1),
            threshold=120.0 if angle > 120 else 70.0,
            message=f"Your elbow angle is {angle:.0f}\u00b0 ({'too straight' if angle > 120 else 'too tight'}). Keep your elbows at roughly 85-100\u00b0 for efficient arm drive.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def estimate_cadence(all_keypoints: list[np.ndarray], frame_indices: list[int], fps: float) -> float | None:
    """Estimate steps per minute from ankle vertical oscillation."""
    if len(all_keypoints) < 10 or fps <= 0:
        return None

    ankle_y = [kp[BODYPART_INDICES["ankle"], 1] for kp in all_keypoints]
    # Count local minima (foot strikes)
    minima = 0
    for i in range(1, len(ankle_y) - 1):
        if ankle_y[i] < ankle_y[i - 1] and ankle_y[i] < ankle_y[i + 1]:
            minima += 1

    if minima == 0:
        return None

    duration_frames = frame_indices[-1] - frame_indices[0]
    duration_sec = duration_frames / fps
    if duration_sec <= 0:
        return None

    spm = (minima / duration_sec) * 60
    return round(spm, 0)


class RunningCoach:
    def __init__(self) -> None:
        self._last_cadence: float | None = None

    def analyze_frame(self, kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
        tips: list[CoachingTip] = []
        for fn in (analyze_foot_strike, analyze_forward_lean, analyze_arm_swing):
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
        lean_angles, elbow_angles = [], []
        for kp in all_keypoints:
            neck = _p(kp, "neck")
            hip = _p(kp, "hip")
            torso_vec = neck - hip
            vertical = np.array([0.0, -1.0])
            lean_angles.append(compute_vector_angle(torso_vec, vertical))

            shoulder = _p(kp, "shoulder")
            elbow = _p(kp, "elbow")
            wrist = _p(kp, "wrist")
            elbow_angles.append(compute_angle(shoulder, elbow, wrist))

        return {
            "total_frames_analyzed": len(all_keypoints),
            "avg_forward_lean": round(float(np.mean(lean_angles)), 1) if lean_angles else None,
            "avg_elbow_angle": round(float(np.mean(elbow_angles)), 1) if elbow_angles else None,
            "cadence_spm": self._last_cadence,
        }

    def generate_coaching_summary(self, tips: list[CoachingTip]) -> CoachingSummaryData:
        return generate_coaching_summary(tips)
