"""
Background Task Orchestration
Runs the full analysis pipeline: inference -> coaching logic -> video processing.

Performance features:
- File-backed persistent task store -- Fix #8
- Semaphore-based concurrency control -- Fix #4
- Pre-loaded estimator support -- Fix #5
- Async completion events for WebSocket -- Fix #3
"""

import asyncio
import json
import threading
import time
import traceback
import uuid
from pathlib import Path

import numpy as np

from ..config import settings
from ..models.schemas import (
    AnalysisResult,
    AnalysisStatus,
    CategoryBreakdown,
    CoachingSummary,
    CoachingTipSchema,
    Severity,
    SportSpecificStats,
)
from ..services.inference import MockPoseEstimator, PyTorchPoseEstimator, create_estimator
from ..services.video_processor import create_annotated_video
from ..sports.registry import SportRegistry


# ---------------------------------------------------------------------------
# Fix #8: File-backed task store (survives restarts)
# ---------------------------------------------------------------------------

class TaskStore:
    """Persistent task store backed by JSON files with in-memory cache."""

    def __init__(self, store_dir: Path):
        self._store_dir = store_dir
        self._cache: dict[str, AnalysisResult] = {}
        self._lock = threading.Lock()
        self._store_dir.mkdir(parents=True, exist_ok=True)
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        for f in self._store_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                result = AnalysisResult(**data)
                self._cache[result.task_id] = result
            except Exception:
                pass
        if self._cache:
            print(f"TaskStore: loaded {len(self._cache)} tasks from disk")

    def set(self, task_id: str, result: AnalysisResult) -> None:
        with self._lock:
            self._cache[task_id] = result
            path = self._store_dir / f"{task_id}.json"
            path.write_text(result.model_dump_json())

    def get(self, task_id: str) -> AnalysisResult | None:
        return self._cache.get(task_id)

    def cleanup(self, max_age_hours: int) -> int:
        now = time.time()
        removed = 0
        for f in self._store_dir.glob("*.json"):
            try:
                if now - f.stat().st_mtime > max_age_hours * 3600:
                    task_id = f.stem
                    with self._lock:
                        self._cache.pop(task_id, None)
                    f.unlink(missing_ok=True)
                    removed += 1
            except Exception:
                pass
        return removed


task_store = TaskStore(settings.task_store_dir)


# ---------------------------------------------------------------------------
# Fix #4: Concurrency control via semaphore
# ---------------------------------------------------------------------------

_analysis_semaphore = threading.Semaphore(settings.max_analysis_workers)


# ---------------------------------------------------------------------------
# Fix #3: Async completion events for WebSocket push
# ---------------------------------------------------------------------------

_completion_events: dict[str, asyncio.Event] = {}
_event_loop: asyncio.AbstractEventLoop | None = None


def set_event_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _event_loop
    _event_loop = loop


def _notify_completion(task_id: str) -> None:
    event = _completion_events.get(task_id)
    if event and _event_loop:
        _event_loop.call_soon_threadsafe(event.set)


async def wait_for_completion(task_id: str, timeout: float = 600) -> None:
    event = asyncio.Event()
    _completion_events[task_id] = event
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout)
    except asyncio.TimeoutError:
        pass
    finally:
        _completion_events.pop(task_id, None)


# ---------------------------------------------------------------------------
# Fix #5: Shared pre-loaded estimators
# ---------------------------------------------------------------------------

_shared_estimators: dict[str, PyTorchPoseEstimator | MockPoseEstimator] = {}


def preload_models() -> None:
    """Load and warm up models for all registered sports at app startup."""
    for sport_info in SportRegistry.list_sports():
        sport_id = sport_info["sport_id"]
        estimator = create_estimator(sport_id)
        _shared_estimators[sport_id] = estimator
        if isinstance(estimator, PyTorchPoseEstimator):
            estimator.warmup()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_task(video_filename: str, sport: str) -> str:
    task_id = str(uuid.uuid4())
    task_store.set(
        task_id,
        AnalysisResult(task_id=task_id, status=AnalysisStatus.PROCESSING, sport=sport),
    )
    return task_id


def get_task_result(task_id: str) -> AnalysisResult | None:
    return task_store.get(task_id)


def run_analysis(task_id: str, video_path: Path, sport: str) -> None:
    """Run the full analysis pipeline as a background task."""
    acquired = _analysis_semaphore.acquire(timeout=300)
    if not acquired:
        task_store.set(
            task_id,
            AnalysisResult(
                task_id=task_id,
                status=AnalysisStatus.FAILED,
                sport=sport,
                error="Server busy -- too many concurrent analyses. Please try again.",
            ),
        )
        _notify_completion(task_id)
        return

    try:
        definition = SportRegistry.get_definition(sport)
        coach = SportRegistry.get_coach(sport)

        # Step 1: Inference
        estimator = _shared_estimators.get(sport) or create_estimator(sport)
        sample_rate = definition.inference_sample_rate or settings.inference_sample_rate
        all_keypoints, frame_indices, video_fps = estimator.predict_video(
            video_path,
            sample_rate=sample_rate,
            batch_size=settings.inference_batch_size,
        )

        if not all_keypoints:
            task_store.set(
                task_id,
                AnalysisResult(
                    task_id=task_id,
                    status=AnalysisStatus.FAILED,
                    sport=sport,
                    error="No frames could be processed from the video.",
                ),
            )
            return

        # Step 2: Biomechanical analysis
        tips = coach.analyze_sequence(all_keypoints, frame_indices)
        coaching_tips = [
            CoachingTipSchema(
                category=t.category,
                body_part=t.body_part,
                angle_value=t.angle_value,
                threshold=t.threshold,
                message=t.message,
                severity=Severity(t.severity.value),
                frame_range=t.frame_range,
            )
            for t in tips
        ]

        # Step 3: Create annotated video
        results_dir = settings.results_dir
        results_dir.mkdir(parents=True, exist_ok=True)
        annotated_path = results_dir / f"{task_id}_annotated.mp4"

        create_annotated_video(
            video_path, annotated_path, all_keypoints, frame_indices, definition
        )

        # Step 4: Compute summary statistics
        stats = coach.compute_keypoints_summary(all_keypoints)
        summary = SportSpecificStats(stats=stats)

        # Step 5: Generate coaching summary
        coaching_summary_data = coach.generate_coaching_summary(tips)
        coaching_summary = CoachingSummary(
            overall_assessment=coaching_summary_data.overall_assessment,
            category_breakdowns=[
                CategoryBreakdown(
                    category=b.category,
                    count=b.count,
                    avg_angle_value=b.avg_angle_value,
                    worst_severity=Severity(b.worst_severity.value),
                )
                for b in coaching_summary_data.category_breakdowns
            ],
            top_tips=[
                CoachingTipSchema(
                    category=t.category,
                    body_part=t.body_part,
                    angle_value=t.angle_value,
                    threshold=t.threshold,
                    message=t.message,
                    severity=Severity(t.severity.value),
                    frame_range=t.frame_range,
                )
                for t in coaching_summary_data.top_tips
            ],
        )

        task_store.set(
            task_id,
            AnalysisResult(
                task_id=task_id,
                status=AnalysisStatus.COMPLETED,
                sport=sport,
                coaching_tips=coaching_tips,
                video_url=f"/results/{task_id}_annotated.mp4",
                keypoints_summary=summary,
                coaching_summary=coaching_summary,
                video_fps=video_fps,
            ),
        )

    except Exception as e:
        traceback.print_exc()
        task_store.set(
            task_id,
            AnalysisResult(
                task_id=task_id,
                status=AnalysisStatus.FAILED,
                sport=sport,
                error=str(e),
            ),
        )
    finally:
        _analysis_semaphore.release()
        _notify_completion(task_id)
