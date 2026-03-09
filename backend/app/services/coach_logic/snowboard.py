"""Snowboard biomechanical analysis — knee flexion, shoulder alignment, stance width."""

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
    "nose_shoulder": 1,
    "tail_shoulder": 2,
    "center_hips": 3,
    "front_knee": 4,
    "back_knee": 5,
    "front_ankle": 6,
    "back_ankle": 7,
    "board_nose": 8,
    "board_tail": 9,
}


def _p(kp: np.ndarray, name: str) -> np.ndarray:
    return get_point(kp, name, BODYPART_INDICES)


def analyze_knee_flexion(kp: np.ndarray, leg: str, frame_idx: int) -> CoachingTip | None:
    if leg == "front":
        hip, knee, ankle = _p(kp, "center_hips"), _p(kp, "front_knee"), _p(kp, "front_ankle")
        body_part = "front_knee"
    else:
        hip, knee, ankle = _p(kp, "center_hips"), _p(kp, "back_knee"), _p(kp, "back_ankle")
        body_part = "back_knee"

    angle = compute_angle(hip, knee, ankle)

    if angle > 170:
        return CoachingTip(
            category="Knee Flexion", body_part=body_part, angle_value=round(angle, 1),
            threshold=170.0,
            message=f"Your {leg} knee is almost locked at {angle:.0f}\u00b0. Bend your knees more to absorb terrain and maintain balance. Aim for 90-140\u00b0 of flexion.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 160:
        return CoachingTip(
            category="Knee Flexion", body_part=body_part, angle_value=round(angle, 1),
            threshold=160.0,
            message=f"Your {leg} knee is getting straight at {angle:.0f}\u00b0. Try to maintain a more athletic bend for better shock absorption.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_shoulder_alignment(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    shoulder_vec = _p(kp, "nose_shoulder") - _p(kp, "tail_shoulder")
    board_vec = _p(kp, "board_nose") - _p(kp, "board_tail")
    angle = compute_vector_angle(shoulder_vec, board_vec)
    if angle > 90:
        angle = 180 - angle

    if angle > 30:
        return CoachingTip(
            category="Shoulder Alignment", body_part="shoulders", angle_value=round(angle, 1),
            threshold=30.0,
            message=f"Your shoulders are rotated {angle:.0f}\u00b0 from the board. Keep your shoulders more aligned with the board direction for better edge control and stability.",
            severity=Severity.CRITICAL, frame_range=(frame_idx, frame_idx),
        )
    elif angle > 15:
        return CoachingTip(
            category="Shoulder Alignment", body_part="shoulders", angle_value=round(angle, 1),
            threshold=15.0,
            message=f"Your shoulders are slightly off-axis at {angle:.0f}\u00b0. Try to keep your upper body aligned with your direction of travel.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


def analyze_stance_width(kp: np.ndarray, frame_idx: int) -> CoachingTip | None:
    stance_width = float(np.linalg.norm(_p(kp, "front_ankle") - _p(kp, "back_ankle")))
    board_length = float(np.linalg.norm(_p(kp, "board_nose") - _p(kp, "board_tail")))
    if board_length == 0:
        return None
    ratio = stance_width / board_length
    if ratio < 0.2:
        return CoachingTip(
            category="Stance Width", body_part="feet", angle_value=round(ratio * 100, 1),
            threshold=20.0,
            message="Your stance looks very narrow. Widen your feet to about shoulder-width for better stability and board control.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        )
    return None


class SnowboardCoach:
    def analyze_frame(self, kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
        tips: list[CoachingTip] = []
        for leg in ("front", "back"):
            tip = analyze_knee_flexion(kp, leg, frame_idx)
            if tip:
                tips.append(tip)
        tip = analyze_shoulder_alignment(kp, frame_idx)
        if tip:
            tips.append(tip)
        tip = analyze_stance_width(kp, frame_idx)
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
        front_angles, back_angles, shoulder_angles = [], [], []
        for kp in all_keypoints:
            front_angles.append(compute_angle(_p(kp, "center_hips"), _p(kp, "front_knee"), _p(kp, "front_ankle")))
            back_angles.append(compute_angle(_p(kp, "center_hips"), _p(kp, "back_knee"), _p(kp, "back_ankle")))
            sv = _p(kp, "nose_shoulder") - _p(kp, "tail_shoulder")
            bv = _p(kp, "board_nose") - _p(kp, "board_tail")
            a = compute_vector_angle(sv, bv)
            if a > 90:
                a = 180 - a
            shoulder_angles.append(a)

        return {
            "total_frames_analyzed": len(all_keypoints),
            "avg_front_knee_angle": round(float(np.mean(front_angles)), 1) if front_angles else None,
            "avg_back_knee_angle": round(float(np.mean(back_angles)), 1) if back_angles else None,
            "avg_shoulder_alignment": round(float(np.mean(shoulder_angles)), 1) if shoulder_angles else None,
        }

    def generate_coaching_summary(self, tips: list[CoachingTip]) -> CoachingSummaryData:
        return generate_coaching_summary(tips)
