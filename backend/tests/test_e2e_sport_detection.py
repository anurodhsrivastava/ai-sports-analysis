"""
End-to-end sport detection tests using CLIP-based scene detection.

Uses real downloaded videos to verify:
1. POSITIVE: correct sport → no mismatch warning
2. NEGATIVE: wrong sport selected → mismatch warning shown
3. UNRELATED: non-sport videos → mismatch warning shown

Run:
    python -m pytest tests/test_e2e_sport_detection.py -v
    python -m pytest tests/test_e2e_sport_detection.py -v -k positive
    python -m pytest tests/test_e2e_sport_detection.py -v -k negative
    python -m pytest tests/test_e2e_sport_detection.py -v -k unrelated
"""

import json
import os
from pathlib import Path

import pytest

# Disable rate limiting for tests
os.environ["ENVIRONMENT"] = "testing"

from app.services.scene_detection import detect_sport_mismatch

MANIFEST_PATH = Path(__file__).parent / "test_videos" / "manifest.json"


# ---- Helpers ----

def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        pytest.skip(
            "Test videos not downloaded. Run: python tests/test_videos/download_test_videos.py"
        )
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def _get_video(manifest: dict, key: str) -> Path:
    if key not in manifest:
        pytest.skip(f"Video '{key}' not in manifest (download may have failed)")
    path = Path(manifest[key]["path"])
    if not path.exists():
        pytest.skip(f"Video file missing: {path}")
    return path


# =========================================================================
# POSITIVE TESTS: Correct sport → no mismatch
# =========================================================================

class TestPositiveFlows:
    """Correct sport selected → no mismatch warning."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manifest = _load_manifest()

    def test_snowboarding_correct_sport(self):
        video = _get_video(self.manifest, "snowboarding_01")
        result = detect_sport_mismatch(video, "snowboard")
        assert result is None, f"False mismatch on snowboarding video: {result}"

    def test_skiing_correct_sport(self):
        video = _get_video(self.manifest, "skiing_01")
        result = detect_sport_mismatch(video, "skiing")
        assert result is None, f"False mismatch on skiing video: {result}"

    def test_skateboarding_correct_sport(self):
        video = _get_video(self.manifest, "skateboarding_01")
        result = detect_sport_mismatch(video, "skateboarding")
        assert result is None, f"False mismatch on skateboarding video: {result}"

    def test_surfing_correct_sport(self):
        video = _get_video(self.manifest, "surfing_01")
        result = detect_sport_mismatch(video, "surfing")
        assert result is None, f"False mismatch on surfing video: {result}"

    def test_snow_video_accepted_for_skiing(self):
        """A snowboarding video should also pass for skiing (both are snow sports)."""
        video = _get_video(self.manifest, "snowboarding_01")
        result = detect_sport_mismatch(video, "skiing")
        assert result is None, f"Snow video wrongly rejected for skiing: {result}"

    def test_snow_video_accepted_for_snowboarding(self):
        """A skiing video should also pass for snowboarding (both are snow sports)."""
        video = _get_video(self.manifest, "skiing_01")
        result = detect_sport_mismatch(video, "snowboard")
        assert result is None, f"Snow video wrongly rejected for snowboarding: {result}"


# =========================================================================
# NEGATIVE TESTS: Wrong sport selected → mismatch warning
# =========================================================================

class TestNegativeFlows:
    """Wrong sport selected → mismatch warning."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manifest = _load_manifest()

    def test_snow_video_as_skateboarding(self):
        """Snow video selected as skateboarding → should warn."""
        video = _get_video(self.manifest, "snowboarding_01")
        result = detect_sport_mismatch(video, "skateboarding")
        assert result is not None, "No mismatch warning for snow video as skateboarding"
        assert result["selected_sport"] == "skateboarding"

    def test_skateboard_video_as_skiing(self):
        """Skateboarding video selected as skiing → should warn."""
        video = _get_video(self.manifest, "skateboarding_01")
        result = detect_sport_mismatch(video, "skiing")
        assert result is not None, "No mismatch warning for skateboard video as skiing"
        assert result["selected_sport"] == "skiing"

    def test_skateboard_video_as_snowboarding(self):
        """Skateboarding video selected as snowboarding → should warn."""
        video = _get_video(self.manifest, "skateboarding_01")
        result = detect_sport_mismatch(video, "snowboard")
        assert result is not None, "No mismatch warning for skateboard video as snowboarding"

    def test_skateboard_video_as_surfing(self):
        """Skateboarding video selected as surfing → should warn."""
        video = _get_video(self.manifest, "skateboarding_01")
        result = detect_sport_mismatch(video, "surfing")
        assert result is not None, "No mismatch warning for skateboard video as surfing"

    def test_mismatch_has_required_fields(self):
        """Mismatch result should contain all required fields."""
        video = _get_video(self.manifest, "snowboarding_01")
        result = detect_sport_mismatch(video, "skateboarding")
        assert result is not None
        assert "selected_sport" in result
        assert "detected_environment" in result
        assert "suggested_sport" in result
        assert "message" in result
        assert len(result["message"]) > 10


# =========================================================================
# UNRELATED TESTS: Non-sport videos → mismatch warning
# =========================================================================

class TestUnrelatedVideos:
    """Non-sport videos → mismatch warning for snow sports."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manifest = _load_manifest()

    _UNRELATED_KEYS = ["cooking_01", "teaching_01", "tennis_01"]

    @pytest.mark.parametrize("video_key", _UNRELATED_KEYS)
    def test_unrelated_video_as_skiing(self, video_key):
        """Unrelated video selected as skiing → should warn."""
        video = _get_video(self.manifest, video_key)
        result = detect_sport_mismatch(video, "skiing")
        assert result is not None, f"No mismatch for {video_key} as skiing"

    @pytest.mark.parametrize("video_key", _UNRELATED_KEYS)
    def test_unrelated_video_as_snowboarding(self, video_key):
        """Unrelated video selected as snowboarding → should warn."""
        video = _get_video(self.manifest, video_key)
        result = detect_sport_mismatch(video, "snowboard")
        assert result is not None, f"No mismatch for {video_key} as snowboarding"

    @pytest.mark.parametrize("video_key", _UNRELATED_KEYS)
    def test_unrelated_video_as_skateboarding(self, video_key):
        """Unrelated video selected as skateboarding → should warn."""
        video = _get_video(self.manifest, video_key)
        result = detect_sport_mismatch(video, "skateboarding")
        assert result is not None, f"No mismatch for {video_key} as skateboarding"

    @pytest.mark.parametrize("video_key", _UNRELATED_KEYS)
    def test_unrelated_video_as_surfing(self, video_key):
        """Unrelated video selected as surfing → should warn."""
        video = _get_video(self.manifest, video_key)
        result = detect_sport_mismatch(video, "surfing")
        assert result is not None, f"No mismatch for {video_key} as surfing"


# =========================================================================
# API INTEGRATION TESTS: Full upload → result pipeline
# =========================================================================

class TestAPIIntegration:
    """Test full upload + analysis pipeline with real videos."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.manifest = _load_manifest()

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def _upload_and_wait(self, client, video_path: Path, sport: str) -> dict:
        """Upload a video and poll until analysis completes."""
        with open(video_path, "rb") as f:
            resp = client.post(
                "/api/analyze",
                files={"file": (video_path.name, f, "video/mp4")},
                data={"sport": sport},
            )
        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        task_id = resp.json()["task_id"]

        import time
        for _ in range(60):
            result = client.get(f"/api/analyze/{task_id}")
            assert result.status_code == 200
            data = result.json()
            if data["status"] != "processing":
                return data
            time.sleep(1)

        pytest.fail(f"Analysis timed out for task {task_id}")

    def test_positive_upload_returns_coaching_tips(self, client):
        """Upload a snow video as snowboarding → should get coaching tips."""
        video = _get_video(self.manifest, "snowboarding_01")
        result = self._upload_and_wait(client, video, "snowboard")

        assert result["status"] == "completed"
        assert result["sport"] == "snowboard"
        assert result["video_url"] is not None
        assert result["keypoints_summary"] is not None
        assert result["keypoints_summary"]["stats"]["total_frames_analyzed"] > 0

    def test_negative_upload_has_mismatch_warning(self, client):
        """Upload a cooking video as snowboard → should have mismatch warning."""
        video = _get_video(self.manifest, "cooking_01")
        result = self._upload_and_wait(client, video, "snowboard")

        assert result["status"] == "completed"
        assert result["sport_mismatch"] is not None

    def test_unrelated_upload_has_mismatch_warning(self, client):
        """Upload a cooking video as skiing → should have mismatch warning."""
        video = _get_video(self.manifest, "cooking_01")
        result = self._upload_and_wait(client, video, "skiing")

        assert result["status"] == "completed"
        assert result["sport_mismatch"] is not None
