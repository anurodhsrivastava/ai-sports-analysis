"""
Tests for the pose estimation inference service.
Uses the MockPoseEstimator for all tests (no model file needed).
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from app.services.inference import MockPoseEstimator


@pytest.fixture
def mock_estimator():
    return MockPoseEstimator()


@pytest.fixture
def dummy_video(tmp_path):
    """Create a minimal valid video file for testing."""
    video_path = tmp_path / "test_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(str(video_path), fourcc, 30.0, (640, 480))
    for _ in range(30):  # 1 second at 30fps
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return video_path


class TestMockPoseEstimator:
    def test_predict_frame_shape(self, mock_estimator):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        kp = mock_estimator.predict_frame(frame)
        assert kp.shape == (10, 3)

    def test_predict_frame_coordinates_in_bounds(self, mock_estimator):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        kp = mock_estimator.predict_frame(frame)
        # x coordinates should be within frame width (with some noise)
        assert np.all(kp[:, 0] > -50)
        assert np.all(kp[:, 0] < 690)
        # y coordinates should be within frame height
        assert np.all(kp[:, 1] > -50)
        assert np.all(kp[:, 1] < 530)

    def test_predict_frame_confidence_values(self, mock_estimator):
        """Confidence should be between 0 and 1. Blank frames may have zero confidence."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        kp = mock_estimator.predict_frame(frame)
        assert np.all(kp[:, 2] >= 0.0)
        assert np.all(kp[:, 2] <= 1.0)

    def test_predict_frame_consistent_on_same_input(self, mock_estimator):
        """MediaPipe is deterministic — same frame should give same result."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        kp1 = mock_estimator.predict_frame(frame)
        kp2 = mock_estimator.predict_frame(frame)
        np.testing.assert_array_almost_equal(kp1, kp2)

    def test_predict_video(self, mock_estimator, dummy_video):
        kps, indices, fps = mock_estimator.predict_video(
            dummy_video, sample_rate=6, batch_size=4
        )
        assert len(kps) > 0
        assert len(kps) == len(indices)
        assert fps > 0
        assert all(kp.shape == (10, 3) for kp in kps)

    def test_predict_video_sample_rate(self, mock_estimator, dummy_video):
        """Higher sample rate should produce fewer keypoints."""
        kps_3, _, _ = mock_estimator.predict_video(dummy_video, sample_rate=3)
        kps_6, _, _ = mock_estimator.predict_video(dummy_video, sample_rate=6)
        assert len(kps_3) >= len(kps_6)

    def test_predict_video_indices_spaced(self, mock_estimator, dummy_video):
        """Frame indices should be spaced by sample_rate."""
        _, indices, _ = mock_estimator.predict_video(dummy_video, sample_rate=6)
        for i in range(len(indices) - 1):
            assert indices[i + 1] - indices[i] == 6

    def test_predict_video_invalid_path(self, mock_estimator):
        with pytest.raises(ValueError, match="Cannot open video"):
            mock_estimator.predict_video("/nonexistent/video.mp4")
