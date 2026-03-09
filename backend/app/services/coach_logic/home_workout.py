"""Home workout biomechanical analysis — squat, push-up, plank, lunge detection and checks."""

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
    "left_shoulder": 1,
    "right_shoulder": 2,
    "left_elbow": 3,
    "right_elbow": 4,
    "left_wrist": 5,
    "right_wrist": 6,
    "left_hip": 7,
    "right_hip": 8,
    "left_knee": 9,
    "right_knee": 10,
    "left_ankle": 11,
    "right_ankle": 12,
}


def _p(kp: np.ndarray, name: str) -> np.ndarray:
    return get_point(kp, name, BODYPART_INDICES)


def _mid(kp: np.ndarray, n1: str, n2: str) -> np.ndarray:
    return (_p(kp, n1) + _p(kp, n2)) / 2


def classify_exercise(kp: np.ndarray) -> str:
    """Classify the exercise based on body geometry heuristics."""
    mid_hip = _mid(kp, "left_hip", "right_hip")
    mid_shoulder = _mid(kp, "left_shoulder", "right_shoulder")
    mid_ankle = _mid(kp, "left_ankle", "right_ankle")

    torso_vec = mid_shoulder - mid_hip
    vertical = np.array([0.0, -1.0])
    torso_angle = compute_vector_angle(torso_vec, vertical)

    # If torso is nearly horizontal (>60 degrees from vertical) -> push-up or plank
    if torso_angle > 60:
        # Check elbow angle to distinguish push-up from plank
        left_elbow_angle = compute_angle(_p(kp, "left_shoulder"), _p(kp, "left_elbow"), _p(kp, "left_wrist"))
        right_elbow_angle = compute_angle(_p(kp, "right_shoulder"), _p(kp, "right_elbow"), _p(kp, "right_wrist"))
        avg_elbow = (left_elbow_angle + right_elbow_angle) / 2
        if avg_elbow < 150:
            return "pushup"
        return "plank"

    # Upright position: check knee angles
    left_knee_angle = compute_angle(_p(kp, "left_hip"), _p(kp, "left_knee"), _p(kp, "left_ankle"))
    right_knee_angle = compute_angle(_p(kp, "right_hip"), _p(kp, "right_knee"), _p(kp, "right_ankle"))

    # Check if one leg is significantly more bent than the other -> lunge
    if abs(left_knee_angle - right_knee_angle) > 30:
        return "lunge"

    # Both knees bent -> squat
    if left_knee_angle < 150 or right_knee_angle < 150:
        return "squat"

    return "standing"


def analyze_squat(kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
    tips: list[CoachingTip] = []

    # Squat depth - knee angle
    for side in ("left", "right"):
        knee_angle = compute_angle(_p(kp, f"{side}_hip"), _p(kp, f"{side}_knee"), _p(kp, f"{side}_ankle"))
        if knee_angle > 100:
            tips.append(CoachingTip(
                category="Squat Depth", body_part=f"{side}_knee", angle_value=round(knee_angle, 1),
                threshold=100.0,
                message=f"Your {side} knee angle is {knee_angle:.0f}\u00b0 \u2014 squat deeper. Aim for thighs parallel to the floor (around 80-90\u00b0).",
                severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
            ))

    # Knee tracking (knees should track over toes, check lateral deviation)
    for side in ("left", "right"):
        knee = _p(kp, f"{side}_knee")
        ankle = _p(kp, f"{side}_ankle")
        hip = _p(kp, f"{side}_hip")
        # Check if knee is caving in (x position relative to ankle)
        knee_ankle_x = abs(float(knee[0] - ankle[0]))
        hip_ankle_x = abs(float(hip[0] - ankle[0]))
        if hip_ankle_x > 0 and knee_ankle_x / max(hip_ankle_x, 1) > 1.3:
            tips.append(CoachingTip(
                category="Knee Tracking", body_part=f"{side}_knee",
                angle_value=round(knee_ankle_x, 1), threshold=0.0,
                message=f"Your {side} knee appears to be caving inward. Push your knees out in line with your toes.",
                severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
            ))

    # Back rounding (forward lean)
    mid_shoulder = _mid(kp, "left_shoulder", "right_shoulder")
    mid_hip = _mid(kp, "left_hip", "right_hip")
    torso_vec = mid_shoulder - mid_hip
    vertical = np.array([0.0, -1.0])
    lean = compute_vector_angle(torso_vec, vertical)
    if lean > 45:
        tips.append(CoachingTip(
            category="Back Position", body_part="torso", angle_value=round(lean, 1),
            threshold=45.0,
            message=f"Your torso is leaning forward {lean:.0f}\u00b0. Keep your chest up and back straight during squats.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        ))

    return tips


def analyze_pushup(kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
    tips: list[CoachingTip] = []

    # Elbow range of motion
    for side in ("left", "right"):
        elbow_angle = compute_angle(_p(kp, f"{side}_shoulder"), _p(kp, f"{side}_elbow"), _p(kp, f"{side}_wrist"))
        if elbow_angle > 110:
            tips.append(CoachingTip(
                category="Elbow Range", body_part=f"{side}_elbow", angle_value=round(elbow_angle, 1),
                threshold=110.0,
                message=f"Your {side} elbow angle is {elbow_angle:.0f}\u00b0. Lower your chest more \u2014 aim for elbows at 90\u00b0 at the bottom.",
                severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
            ))

    # Body line check (shoulder-hip-ankle should be roughly straight)
    mid_shoulder = _mid(kp, "left_shoulder", "right_shoulder")
    mid_hip = _mid(kp, "left_hip", "right_hip")
    mid_ankle = _mid(kp, "left_ankle", "right_ankle")
    body_line_angle = compute_angle(mid_shoulder, mid_hip, mid_ankle)
    deviation = abs(180 - body_line_angle)
    if deviation > 10:
        tips.append(CoachingTip(
            category="Body Line", body_part="torso", angle_value=round(deviation, 1),
            threshold=10.0,
            message=f"Your body is sagging or piking ({deviation:.0f}\u00b0 deviation). Keep a straight line from shoulders to ankles.",
            severity=Severity.WARNING if deviation <= 20 else Severity.CRITICAL,
            frame_range=(frame_idx, frame_idx),
        ))

    return tips


def analyze_plank(kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
    tips: list[CoachingTip] = []

    mid_shoulder = _mid(kp, "left_shoulder", "right_shoulder")
    mid_hip = _mid(kp, "left_hip", "right_hip")
    mid_ankle = _mid(kp, "left_ankle", "right_ankle")
    body_line_angle = compute_angle(mid_shoulder, mid_hip, mid_ankle)
    deviation = abs(180 - body_line_angle)
    if deviation > 10:
        tips.append(CoachingTip(
            category="Body Line", body_part="torso", angle_value=round(deviation, 1),
            threshold=10.0,
            message=f"Your plank has {deviation:.0f}\u00b0 deviation from straight. Engage your core and glutes to maintain a flat body line.",
            severity=Severity.WARNING if deviation <= 20 else Severity.CRITICAL,
            frame_range=(frame_idx, frame_idx),
        ))

    return tips


def analyze_lunge(kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
    tips: list[CoachingTip] = []

    # Determine which leg is in front (lower knee = front leg)
    left_knee_angle = compute_angle(_p(kp, "left_hip"), _p(kp, "left_knee"), _p(kp, "left_ankle"))
    right_knee_angle = compute_angle(_p(kp, "right_hip"), _p(kp, "right_knee"), _p(kp, "right_ankle"))

    front_side = "left" if left_knee_angle < right_knee_angle else "right"
    front_angle = min(left_knee_angle, right_knee_angle)

    if front_angle < 80 or front_angle > 100:
        if front_angle < 80:
            msg = f"Your front knee is too bent at {front_angle:.0f}\u00b0. Don't let your knee go past your toes."
        else:
            msg = f"Your front knee angle is {front_angle:.0f}\u00b0 \u2014 step further forward to achieve a 90\u00b0 angle."
        tips.append(CoachingTip(
            category="Front Knee Angle", body_part=f"{front_side}_knee",
            angle_value=round(front_angle, 1),
            threshold=80.0 if front_angle < 80 else 100.0,
            message=msg,
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        ))

    # Torso position
    mid_shoulder = _mid(kp, "left_shoulder", "right_shoulder")
    mid_hip = _mid(kp, "left_hip", "right_hip")
    torso_vec = mid_shoulder - mid_hip
    vertical = np.array([0.0, -1.0])
    lean = compute_vector_angle(torso_vec, vertical)
    if lean > 20:
        tips.append(CoachingTip(
            category="Torso Position", body_part="torso", angle_value=round(lean, 1),
            threshold=20.0,
            message=f"Your torso is leaning {lean:.0f}\u00b0 from vertical during the lunge. Keep your chest upright.",
            severity=Severity.WARNING, frame_range=(frame_idx, frame_idx),
        ))

    return tips


_EXERCISE_ANALYZERS = {
    "squat": analyze_squat,
    "pushup": analyze_pushup,
    "plank": analyze_plank,
    "lunge": analyze_lunge,
}


def count_reps(all_keypoints: list[np.ndarray]) -> int:
    """Count reps via knee/elbow angle oscillation minima."""
    if len(all_keypoints) < 5:
        return 0

    # Use the average knee angle as the signal
    angles = []
    for kp in all_keypoints:
        left = compute_angle(_p(kp, "left_hip"), _p(kp, "left_knee"), _p(kp, "left_ankle"))
        right = compute_angle(_p(kp, "right_hip"), _p(kp, "right_knee"), _p(kp, "right_ankle"))
        angles.append((left + right) / 2)

    # Count local minima
    reps = 0
    for i in range(1, len(angles) - 1):
        if angles[i] < angles[i - 1] and angles[i] < angles[i + 1]:
            reps += 1

    return reps


class HomeWorkoutCoach:
    def analyze_frame(self, kp: np.ndarray, frame_idx: int) -> list[CoachingTip]:
        exercise = classify_exercise(kp)
        analyzer = _EXERCISE_ANALYZERS.get(exercise)
        if analyzer:
            return analyzer(kp, frame_idx)
        return []

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
        # Detect dominant exercise
        exercise_counts: dict[str, int] = {}
        for kp in all_keypoints:
            ex = classify_exercise(kp)
            exercise_counts[ex] = exercise_counts.get(ex, 0) + 1

        dominant = max(exercise_counts, key=exercise_counts.get) if exercise_counts else "unknown"
        reps = count_reps(all_keypoints)

        knee_angles, elbow_angles = [], []
        for kp in all_keypoints:
            left_k = compute_angle(_p(kp, "left_hip"), _p(kp, "left_knee"), _p(kp, "left_ankle"))
            right_k = compute_angle(_p(kp, "right_hip"), _p(kp, "right_knee"), _p(kp, "right_ankle"))
            knee_angles.append((left_k + right_k) / 2)
            left_e = compute_angle(_p(kp, "left_shoulder"), _p(kp, "left_elbow"), _p(kp, "left_wrist"))
            right_e = compute_angle(_p(kp, "right_shoulder"), _p(kp, "right_elbow"), _p(kp, "right_wrist"))
            elbow_angles.append((left_e + right_e) / 2)

        return {
            "total_frames_analyzed": len(all_keypoints),
            "detected_exercise": dominant,
            "estimated_reps": reps,
            "avg_knee_angle": round(float(np.mean(knee_angles)), 1) if knee_angles else None,
            "avg_elbow_angle": round(float(np.mean(elbow_angles)), 1) if elbow_angles else None,
        }

    def generate_coaching_summary(self, tips: list[CoachingTip]) -> CoachingSummaryData:
        return generate_coaching_summary(tips)
