"""
Mock tests for the API endpoints.
Tests upload, polling, sport selection, auth, and wishlist flows.
"""

import io
import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import AnalysisResult, AnalysisStatus
from app.sports.registry import SportRegistry

# Valid UUID for tests that need UUID-format task IDs
_TASK_UUID = "00000000-0000-4000-8000-000000000001"
_TASK_UUID_2 = "00000000-0000-4000-8000-000000000002"
_TASK_UUID_MISSING = "00000000-0000-4000-8000-ffffffffffff"


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure database tables exist for auth tests."""
    from app.database import Base, engine
    from app import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_video_file():
    """Create a minimal valid video-like file for upload testing."""
    content = b"\x00" * 1024  # 1KB dummy content
    return ("test_video.mp4", io.BytesIO(content), "video/mp4")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health_returns_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "sports" in data


# ---------------------------------------------------------------------------
# Upload endpoint
# ---------------------------------------------------------------------------

class TestUploadEndpoint:
    @patch("app.routers.analyze.magic")
    @patch("app.routers.analyze.run_analysis")
    @patch("app.routers.analyze.create_task", return_value=_TASK_UUID)
    def test_upload_valid_video(self, mock_create, mock_run, mock_magic, client, mock_video_file):
        mock_magic.from_file.return_value = "video/mp4"
        name, file_obj, content_type = mock_video_file
        resp = client.post(
            "/api/analyze",
            files={"file": (name, file_obj, content_type)},
            data={"sport": "snowboard"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task_id"] == _TASK_UUID
        assert data["status"] == "processing"

    def test_upload_invalid_extension(self, client):
        content = io.BytesIO(b"not a video")
        resp = client.post(
            "/api/analyze",
            files={"file": ("test.txt", content, "text/plain")},
            data={"sport": "snowboard"},
        )
        assert resp.status_code == 400
        assert "Unsupported file type" in resp.json()["detail"]

    @patch("app.routers.analyze.magic")
    @patch("app.routers.analyze.run_analysis")
    @patch("app.routers.analyze.create_task", return_value=_TASK_UUID)
    def test_upload_with_sport(self, mock_create, mock_run, mock_magic, client, mock_video_file):
        mock_magic.from_file.return_value = "video/mp4"
        name, file_obj, content_type = mock_video_file
        resp = client.post(
            "/api/analyze",
            files={"file": (name, file_obj, content_type)},
            data={"sport": "skiing"},
        )
        assert resp.status_code == 200
        mock_create.assert_called_once_with("test_video.mp4", "skiing")

    def test_upload_unsupported_sport(self, client, mock_video_file):
        name, file_obj, content_type = mock_video_file
        resp = client.post(
            "/api/analyze",
            files={"file": (name, file_obj, content_type)},
            data={"sport": "cricket"},
        )
        assert resp.status_code == 400
        assert "Unknown sport" in resp.json()["detail"]

    def test_upload_no_filename(self, client):
        resp = client.post(
            "/api/analyze",
            files={"file": ("", io.BytesIO(b""), "video/mp4")},
            data={"sport": "snowboard"},
        )
        assert resp.status_code in (400, 422)  # FastAPI may return 422 for validation


# ---------------------------------------------------------------------------
# Polling endpoint
# ---------------------------------------------------------------------------

class TestPollingEndpoint:
    @patch("app.routers.analyze.get_task_result")
    def test_get_completed_result(self, mock_get, client):
        mock_get.return_value = AnalysisResult(
            task_id=_TASK_UUID,
            status=AnalysisStatus.COMPLETED,
            sport="snowboard",
            coaching_tips=[],
            video_url=f"/results/{_TASK_UUID}_annotated.mp4",
            keypoints_summary=None,
            coaching_summary=None,
            video_fps=30.0,
        )
        resp = client.get(f"/api/analyze/{_TASK_UUID}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    @patch("app.routers.analyze.get_task_result")
    def test_get_processing_result(self, mock_get, client):
        mock_get.return_value = AnalysisResult(
            task_id=_TASK_UUID_2,
            status=AnalysisStatus.PROCESSING,
        )
        resp = client.get(f"/api/analyze/{_TASK_UUID_2}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "processing"

    @patch("app.routers.analyze.get_task_result", return_value=None)
    def test_get_nonexistent_task(self, mock_get, client):
        resp = client.get(f"/api/analyze/{_TASK_UUID_MISSING}")
        assert resp.status_code == 404

    def test_get_invalid_task_id_format(self, client):
        resp = client.get("/api/analyze/not-a-uuid")
        assert resp.status_code == 400
        assert "Invalid task ID" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Sports endpoint
# ---------------------------------------------------------------------------

class TestSportsEndpoint:
    def test_list_sports(self, client):
        resp = client.get("/api/sports")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        sport_ids = [s["sport_id"] for s in data]
        assert "snowboard" in sport_ids

    def test_sports_have_required_fields(self, client):
        resp = client.get("/api/sports")
        for sport in resp.json():
            assert "sport_id" in sport
            assert "display_name" in sport
            assert "emoji" in sport


# ---------------------------------------------------------------------------
# Wishlist endpoint
# ---------------------------------------------------------------------------

class TestWishlistEndpoint:
    def test_add_to_wishlist(self, client, tmp_path):
        with patch("app.routers.sports.settings") as mock_settings:
            mock_settings.wishlist_dir = tmp_path / "wishlist"
            resp = client.post(
                "/api/sports/wishlist",
                json={"sport": "tennis", "email": "test@example.com"},
            )
            assert resp.status_code == 200
            assert resp.json()["success"] is True

    def test_wishlist_without_email(self, client, tmp_path):
        with patch("app.routers.sports.settings") as mock_settings:
            mock_settings.wishlist_dir = tmp_path / "wishlist"
            resp = client.post(
                "/api/sports/wishlist",
                json={"sport": "tennis"},
            )
            assert resp.status_code == 200
            assert resp.json()["success"] is True


# ---------------------------------------------------------------------------
# Auth endpoint
# ---------------------------------------------------------------------------

class TestAuthEndpoint:
    def test_login_google(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"provider": "google", "token": "mock-token", "email": "g@test.com"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["user_id"] is not None
        assert data["jwt_token"] is not None

    def test_login_facebook(self, client):
        resp = client.post(
            "/api/auth/login",
            json={"provider": "facebook", "token": "mock-token", "email": "fb@test.com"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_register_and_login_email(self, client):
        # Register
        resp = client.post(
            "/api/auth/register",
            json={"email": "test_api@test.com", "password": "TestPass123"},
        )
        assert resp.status_code == 200
        # Login
        resp = client.post(
            "/api/auth/login",
            json={"provider": "email", "token": "TestPass123", "email": "test_api@test.com"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_get_current_user_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.json()["authenticated"] is False

    def test_guest_save_requires_auth(self, client):
        """Guest save now requires JWT authentication."""
        resp = client.post(
            "/api/auth/guest-save",
            json={"task_id": "test-task"},
        )
        # Should return 401 since no auth token
        assert resp.status_code == 401
