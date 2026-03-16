"""
Scene-based sport mismatch detection using CLIP vision model.

Uses OpenAI's CLIP to semantically classify video frames against text
descriptions of sports environments. This replaces fragile HSV color
heuristics with a model that understands actual scene content.
"""

import logging
from pathlib import Path

import cv2
import numpy as np
import torch
import open_clip
from PIL import Image

logger = logging.getLogger(__name__)

# ---- Sport / environment configuration ----

_SPORT_LABELS: dict[str, list[str]] = {
    "snowboarding": [
        "a person snowboarding down a snowy mountain",
        "snowboarding on a snow-covered slope",
        "a snowy mountain ski resort",
    ],
    "snowboard": [
        "a person snowboarding down a snowy mountain",
        "snowboarding on a snow-covered slope",
        "a snowy mountain ski resort",
    ],
    "skiing": [
        "a person skiing down a snowy mountain",
        "skiing on a snow-covered slope",
        "a snowy mountain ski resort",
    ],
    "skateboarding": [
        "a person skateboarding on concrete",
        "skateboarding in a skate park",
        "skateboarding on a street or sidewalk",
    ],
    "surfing": [
        "a person surfing on ocean waves",
        "surfing in the sea",
        "ocean waves at a beach",
    ],
    "running": [
        "a person running on a track",
        "jogging on a road or trail",
        "a running path or stadium",
    ],
    "golf": [
        "a person playing golf on a course",
        "a golf swing on a green fairway",
        "a golf course with manicured grass",
    ],
    "yoga": [
        "a person doing yoga poses",
        "yoga practice in a studio or outdoors",
        "stretching and yoga positions",
    ],
    "home_workout": [
        "a person exercising at home",
        "home workout with bodyweight exercises",
        "indoor fitness exercise",
    ],
}

_NEGATIVE_LABELS: list[str] = [
    "an indoor room or office",
    "a kitchen or cooking area",
    "a factory or warehouse",
    "a classroom or lecture hall",
    "a person dancing indoors",
    "a car driving on a road",
    "a tennis court",
    "rock climbing on a wall",
]

# Which sports share environments (cross-accept)
_COMPATIBLE_SPORTS: dict[str, set[str]] = {
    "snowboarding": {"skiing", "snowboard"},
    "snowboard": {"skiing", "snowboarding"},
    "skiing": {"snowboarding", "snowboard"},
    "skateboarding": set(),
    "surfing": set(),
    "running": set(),
    "golf": set(),
    "yoga": {"home_workout"},
    "home_workout": {"yoga"},
}

# ---- CLIP model (lazy-loaded singleton) ----

_clip_model = None
_clip_preprocess = None
_clip_tokenizer = None


def _get_clip():
    """Lazy-load CLIP model (downloads ~350MB on first use)."""
    global _clip_model, _clip_preprocess, _clip_tokenizer
    if _clip_model is None:
        logger.info("Loading CLIP model (first call, may take a moment)...")
        model, _, preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="laion2b_s34b_b79k"
        )
        tokenizer = open_clip.get_tokenizer("ViT-B-32")
        model.eval()
        _clip_model = model
        _clip_preprocess = preprocess
        _clip_tokenizer = tokenizer
        logger.info("CLIP model loaded.")
    return _clip_model, _clip_preprocess, _clip_tokenizer


def _sample_frames(video_path: Path, n_frames: int = 5) -> list[np.ndarray]:
    """Sample evenly spaced frames from a video."""
    cap = cv2.VideoCapture(str(video_path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return []

    indices = np.linspace(0, total - 1, n_frames, dtype=int)
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames


def _classify_with_clip(
    frames: list[np.ndarray], selected_sport: str
) -> dict[str, float]:
    """
    Score frames against sport-specific and negative text labels using CLIP.
    Returns dict with keys: selected_sport score, each compatible sport score,
    and 'unrelated' score.
    """
    model, preprocess, tokenizer = _get_clip()

    # Build text labels
    sport_labels = _SPORT_LABELS.get(selected_sport, [])
    compatible = _COMPATIBLE_SPORTS.get(selected_sport, set())

    all_labels = []
    label_groups = {}  # group_name -> (start_idx, end_idx)

    # Selected sport labels
    start = len(all_labels)
    all_labels.extend(sport_labels)
    label_groups[selected_sport] = (start, len(all_labels))

    # Compatible sport labels
    for compat_sport in compatible:
        start = len(all_labels)
        all_labels.extend(_SPORT_LABELS.get(compat_sport, []))
        label_groups[compat_sport] = (start, len(all_labels))

    # Negative labels
    start = len(all_labels)
    all_labels.extend(_NEGATIVE_LABELS)
    label_groups["unrelated"] = (start, len(all_labels))

    # Encode text
    text_tokens = tokenizer(all_labels)
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    # Encode frames and compute similarities
    group_scores: dict[str, list[float]] = {g: [] for g in label_groups}

    for frame in frames:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        img_tensor = preprocess(pil_img).unsqueeze(0)

        with torch.no_grad():
            img_features = model.encode_image(img_tensor)
            img_features = img_features / img_features.norm(dim=-1, keepdim=True)

        similarities = (img_features @ text_features.T).squeeze(0).numpy()

        for group_name, (start_idx, end_idx) in label_groups.items():
            group_sim = float(np.mean(similarities[start_idx:end_idx]))
            group_scores[group_name].append(group_sim)

    return {group: float(np.mean(scores)) for group, scores in group_scores.items()}


def detect_sport_mismatch(
    video_path: Path,
    selected_sport: str,
) -> dict | None:
    """
    Analyze video content using CLIP and check for sport mismatch.
    Returns a mismatch dict if detected, None otherwise.
    """
    if selected_sport not in _SPORT_LABELS:
        return None

    frames = _sample_frames(video_path, n_frames=5)
    if not frames:
        return None

    scores = _classify_with_clip(frames, selected_sport)
    compatible = _COMPATIBLE_SPORTS.get(selected_sport, set())

    sport_score = scores.get(selected_sport, 0)
    unrelated_score = scores.get("unrelated", 0)

    # Accept if selected sport or a compatible sport scores highest
    all_sport_scores = {selected_sport: sport_score}
    for compat in compatible:
        all_sport_scores[compat] = scores.get(compat, 0)

    best_sport = max(all_sport_scores, key=all_sport_scores.get)  # type: ignore
    best_sport_score = all_sport_scores[best_sport]

    logger.info(
        f"CLIP scores for {video_path.name}: "
        f"selected={selected_sport}={sport_score:.3f}, "
        f"best_match={best_sport}={best_sport_score:.3f}, "
        f"unrelated={unrelated_score:.3f}"
    )

    if best_sport_score > unrelated_score:
        return None

    # Mismatch detected
    all_sport_options = {}
    for sport, labels in _SPORT_LABELS.items():
        if sport in scores:
            all_sport_options[sport] = scores[sport]
        else:
            all_sport_options[sport] = 0

    if len(all_sport_options) < len(_SPORT_LABELS):
        all_sport_options = _score_all_sports(frames)

    suggested = max(all_sport_options, key=all_sport_options.get)  # type: ignore
    if all_sport_options[suggested] <= unrelated_score:
        suggested = selected_sport

    return {
        "selected_sport": selected_sport,
        "detected_environment": "unrecognized",
        "suggested_sport": suggested,
        "message": (
            f"This video doesn't look like a typical {selected_sport.replace('_', ' ').title()} "
            f"environment. Please make sure you selected the right sport."
        ),
    }


def _score_all_sports(frames: list[np.ndarray]) -> dict[str, float]:
    """Score frames against all supported sports."""
    model, preprocess, tokenizer = _get_clip()

    all_scores = {}
    for sport, labels in _SPORT_LABELS.items():
        text_tokens = tokenizer(labels)
        with torch.no_grad():
            text_features = model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

        frame_scores = []
        for frame in frames:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb)
            img_tensor = preprocess(pil_img).unsqueeze(0)

            with torch.no_grad():
                img_features = model.encode_image(img_tensor)
                img_features = img_features / img_features.norm(dim=-1, keepdim=True)

            similarities = (img_features @ text_features.T).squeeze(0).numpy()
            frame_scores.append(float(np.mean(similarities)))

        all_scores[sport] = float(np.mean(frame_scores))

    return all_scores
