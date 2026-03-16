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
    message_key: str = ""  # i18n translation key
    message_params: dict = {}  # interpolation values for translation
    severity: Severity
    frame_range: tuple[int, int]
    confidence: str = "high"  # "high" or "low" — low = equipment-based, approximate


class SportSpecificStats(BaseModel):
    stats: dict[str, float | int | str | None]


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    avg_angle_value: float
    worst_severity: Severity


class CoachingSummary(BaseModel):
    overall_assessment: str
    overall_assessment_key: str = ""  # i18n key
    overall_score: int = 0  # 0-100 numeric score
    overall_grade: str = ""  # A-F letter grade
    category_breakdowns: list[CategoryBreakdown]
    top_tips: list[CoachingTipSchema]


class UploadResponse(BaseModel):
    task_id: str
    status: AnalysisStatus
    sport: str


class SportMismatchWarning(BaseModel):
    selected_sport: str
    detected_environment: str
    suggested_sport: str
    message: str


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
    sport_mismatch: SportMismatchWarning | None = None


# ---------------------------------------------------------------------------
# Sport configuration
# ---------------------------------------------------------------------------

class SportInfo(BaseModel):
    id: str
    label: str
    emoji: str
    available: bool


# ---------------------------------------------------------------------------
# Auth models
# ---------------------------------------------------------------------------

class AuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    EMAIL = "email"


class LoginRequest(BaseModel):
    provider: AuthProvider
    token: str  # OAuth token or password
    email: str | None = None  # Required for email provider


class LoginResponse(BaseModel):
    success: bool
    user_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    jwt_token: str | None = None
    tier: str = "free"
    message: str | None = None


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str | None = None


class RegisterResponse(BaseModel):
    success: bool
    user_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    jwt_token: str | None = None
    tier: str = "free"


class GuestSaveRequest(BaseModel):
    task_id: str


class UserProfile(BaseModel):
    authenticated: bool = False
    user_id: str | None = None
    display_name: str | None = None
    email: str | None = None
    role: str | None = None
    tier: str | None = None


# ---------------------------------------------------------------------------
# Wishlist
# ---------------------------------------------------------------------------

class WishlistRequest(BaseModel):
    sport: str
    email: str | None = None


class WishlistResponse(BaseModel):
    success: bool
    message: str


# ---------------------------------------------------------------------------
# Saved videos
# ---------------------------------------------------------------------------

class SavedVideoResponse(BaseModel):
    id: str
    task_id: str
    sport: str
    status: str
    created_at: str
    video_url: str | None = None
