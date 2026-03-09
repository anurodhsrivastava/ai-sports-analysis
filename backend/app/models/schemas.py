"""Pydantic request/response models for the API."""

from enum import Enum

from pydantic import BaseModel


class AnalysisStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class CoachingTipSchema(BaseModel):
    category: str
    body_part: str
    angle_value: float
    threshold: float
    message: str
    severity: Severity
    frame_range: tuple[int, int]


class SportSpecificStats(BaseModel):
    stats: dict[str, float | int | str | None]


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    avg_angle_value: float
    worst_severity: Severity


class CoachingSummary(BaseModel):
    overall_assessment: str
    category_breakdowns: list[CategoryBreakdown]
    top_tips: list[CoachingTipSchema]


class UploadResponse(BaseModel):
    task_id: str
    status: AnalysisStatus
    sport: str


class AnalysisResult(BaseModel):
    task_id: str
    status: AnalysisStatus
    sport: str = "snowboard"
    coaching_tips: list[CoachingTipSchema] = []
    video_url: str | None = None
    keypoints_summary: SportSpecificStats | None = None
    coaching_summary: CoachingSummary | None = None
    video_fps: float | None = None
    error: str | None = None
