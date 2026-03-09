"""Skiing biomechanical analysis — knee flexion, ski parallelism, hip alignment, pole position."""

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
    "left_shoulder": 1,
    "right_shoulder": 2,
    "center_hips": 3,
    "left_knee": 4,
    "right_knee": 5,
    "left_ankle": 6,
    "right_ankle": 7,
    "left_ski_tip": 8,
    "left_ski_tail": 9,
    "right_ski_tip": 10,
    "right_ski_tail": 11,
    "left_pole_tip": 12,
    "right_pole_tip": 13,
}


def _p(kp: np.ndarray, name: str) -> np.ndarray:
    return get_point(kp, name, BODYPART_INDICES)


def analyze_knee_flexion(kp: np.ndarray, side: str, frame_idx: int) -> CoachingTip | None:
    hip = _p(kp, "center_hips")
    knee = _p(kp, f"{side}_knee")
    ankle = _p(kp, f"{side}_ankle")
    angle = compute_angle(hip, knee, ankle)

    if angle > 170:
        return CoachingTip(
            category="Knee Flexion", body_part=f"{side}_knee", angle_value=round(angle, 1),
            threshold=170.0,
            message=f"Your {side} knee is nearly locked at {angle:.0f}\u00b0. Maintain a flexed athletic stance for better shock absorption and turn control.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 160:
        return CoachingTip(
            category="Knee Flexion", body_part=f"{side}_knee", angle_value=round(angle, 1),
            threshold=160.0,
            message=f"Your {side} knee is getting straight at {angle:.0f}\u00b0. Bend your knees more to maintain an athletic stance.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_ski_parallelism(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    left_ski_vec = _p(kp, "left_ski_tip") - _p(kp, "left_ski_tail")
    right_ski_vec = _p(kp, "right_ski_tip") - _p(kp, "right_ski_tail")
    angle = compute_vector_angle(left_ski_vec, right_ski_vec)
    if angle > 90:
        angle = 180 - angle

    if angle > 20:
        return CoachingTip(
            category="Ski Parallelism", body_part="skis", angle_value=round(angle, 1),
            threshold=20.0,
            message=f"Your skis are diverging by {angle:.0f}\u00b0. Keep your skis parallel for cleaner turns and better speed control.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 10:
        return CoachingTip(
            category="Ski Parallelism", body_part="skis", angle_value=round(angle, 1),
            threshold=10.0,
            message=f"Your skis are slightly divergent at {angle:.0f}\u00b0. Focus on keeping them parallel through turns.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_hip_alignment(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    shoulder_vec = _p(kp, "left_shoulder") - _p(kp, "right_shoulder")
    # Use average ski direction
    left_ski = _p(kp, "left_ski_tip") - _p(kp, "left_ski_tail")
    right_ski = _p(kp, "right_ski_tip") - _p(kp, "right_ski_tail")
    ski_dir = (left_ski + right_ski) / 2
    angle = compute_vector_angle(shoulder_vec, ski_dir)
    if angle > 90:
        angle = 180 - angle

    if angle > 35:
        return CoachingTip(
            category="Hip Alignment", body_part="hips", angle_value=round(angle, 1),
            threshold=35.0,
            message=f"Your upper body is rotated {angle:.0f}\u00b0 from your ski direction. Keep your hips and shoulders square to the fall line.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 20:
        return CoachingTip(
            category="Hip Alignment", body_part="hips", angle_value=round(angle, 1),
            threshold=20.0,
            message=f"Your hips are slightly rotated at {angle:.0f}\u00b0 from your ski direction. Try to face more downhill.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_pole_position(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    angles = []
    for side in ("left", "right"):
        shoulder = _p(kp, f"{side}_shoulder")
        pole_tip = _p(kp, f"{side}_pole_tip")
        vertical = np.array([0.0, 1.0])
        pole_vec = pole_tip - shoulder
        a = compute_vector_angle(pole_vec, vertical)
        angles.append(a)

    avg_angle = float(np.mean(angles))

    if avg_angle > 80:
        return CoachingTip(
            category="Pole Position", body_part="poles", angle_value=round(avg_angle, 1),
            threshold=80.0,
            message=f"Your poles are trailing at {avg_angle:.0f}\u00b0 from vertical. Keep your hands forward with pole tips pointing down and slightly back.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif avg_angle > 60:
        return CoachingTip(
            category="Pole Position", body_part="poles", angle_value=round(avg_angle, 1),
            threshold=60.0,
            message=f"Your poles are somewhat behind you at {avg_angle:.0f}\u00b0. Bring your hands forward for better balance.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


class SkiingCoach:
    def analyze_frame(self, kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
        tips: list[CoachingTip] = []
        for side in ("left", "right"):
            tip = analyze_knee_flexion(kp, side, frame_idx)
            if tip:
                tips.append(tip)
        for fn in (analyze_ski_parallelism, analyze_hip_alignment, analyze_pole_position):
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
        left_knee_angles, right_knee_angles, parallelism_angles = [], [], []
        for kp in all_keypoints:
            left_knee_angles.append(compute_angle(_p(kp, "center_hips"), _p(kp, "left_knee"), _p(kp, "left_ankle")))
            right_knee_angles.append(compute_angle(_p(kp, "center_hips"), _p(kp, "right_knee"), _p(kp, "right_ankle")))
            lv = _p(kp, "left_ski_tip") - _p(kp, "left_ski_tail")
            rv = _p(kp, "right_ski_tip") - _p(kp, "right_ski_tail")
            a = compute_vector_angle(lv, rv)
            if a > 90:
                a = 180 - a
            parallelism_angles.append(a)

        return {
            "total_frames_analyzed": len(all_keypoints),
            "avg_left_knee_angle": round(float(np.mean(left_knee_angles)), 1) if left_knee_angles else None,
            "avg_right_knee_angle": round(float(np.mean(right_knee_angles)), 1) if right_knee_angles else None,
            "avg_ski_parallelism": round(float(np.mean(parallelism_angles)), 1) if parallelism_angles else None,
        }

    def generate_coaching_summary(self, tips: list[CoachingTip]) -> CoachingSummaryData:
        return generate_coaching_summary(tips)
