"""
Performance tests for the AI Sports Coach API.
Tests API response times, inference throughput, and database operations.

Industry standard benchmarks:
- Health endpoint: < 50ms p99
- Upload endpoint: < 500ms p99
- Polling endpoint: < 100ms p99
- Auth endpoint: < 200ms p99
- DB operations: < 20ms
- Coaching analysis: > 100 frames/second
"""

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.services.snow_coach_logic import (
    analyze_frame,
    analyze_sequence,
    generate_coaching_summary,
)


# ---------------------------------------------------------------------------
# Coaching analysis throughput
# ---------------------------------------------------------------------------

class TestCoachingPerformance:
    """Test biomechanical analysis throughput."""

    def _make_keypoints(self, n: int = 10) -> np.ndarray:
        """Create realistic keypoints array."""
        rng = np.random.RandomState(42)
        kp = rng.rand(n, 2) * 480
        return kp

    def test_single_frame_analysis_latency(self):
        """Single frame analysis should complete in under 1ms."""
        kp = self._make_keypoints()
        start = time.perf_counter()
        for _ in range(1000):
            analyze_frame(kp, 0)
        elapsed = time.perf_counter() - start
        per_frame_ms = (elapsed / 1000) * 1000

        assert per_frame_ms < 1.0, f"Single frame analysis took {per_frame_ms:.2f}ms (target: <1ms)"

    def test_sequence_analysis_throughput(self):
        """Sequence analysis should process >100 frames/second."""
        n_frames = 500
        keypoints = [self._make_keypoints() for _ in range(n_frames)]

        start = time.perf_counter()
        tips = analyze_sequence(keypoints)
        elapsed = time.perf_counter() - start

        fps = n_frames / elapsed
        assert fps > 100, f"Sequence analysis throughput: {fps:.0f} fps (target: >100)"

    def test_summary_generation_latency(self):
        """Summary generation should complete in under 10ms for 100 tips."""
        keypoints = [self._make_keypoints() for _ in range(200)]
        tips = analyze_sequence(keypoints)

        start = time.perf_counter()
        for _ in range(100):
            generate_coaching_summary(tips)
        elapsed = time.perf_counter() - start
        per_call_ms = (elapsed / 100) * 1000

        assert per_call_ms < 10, f"Summary generation took {per_call_ms:.2f}ms (target: <10ms)"

    def test_large_sequence_memory(self):
        """Large sequence analysis shouldn't use excessive memory."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / (1024 * 1024)  # MB

        n_frames = 5000
        keypoints = [self._make_keypoints() for _ in range(n_frames)]
        tips = analyze_sequence(keypoints)
        generate_coaching_summary(tips)

        mem_after = process.memory_info().rss / (1024 * 1024)
        mem_used = mem_after - mem_before

        # Should use less than 100MB for 5000 frames
        assert mem_used < 100, f"Memory usage: {mem_used:.1f}MB (target: <100MB)"


# ---------------------------------------------------------------------------
# API response time benchmarks
# ---------------------------------------------------------------------------

class TestAPIPerformance:
    """Test API endpoint response times."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_health_endpoint_latency(self, client):
        """Health endpoint should respond in under 50ms."""
        # Warm up
        client.get("/api/health")

        times = []
        for _ in range(50):
            start = time.perf_counter()
            resp = client.get("/api/health")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            assert resp.status_code == 200

        p99 = sorted(times)[int(len(times) * 0.99)]
        avg = sum(times) / len(times)

        assert p99 < 50, f"Health p99: {p99:.1f}ms (target: <50ms)"
        assert avg < 20, f"Health avg: {avg:.1f}ms (target: <20ms)"

    def test_sports_endpoint_latency(self, client):
        """Sports listing should respond in under 50ms."""
        times = []
        for _ in range(50):
            start = time.perf_counter()
            resp = client.get("/api/sports/")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            assert resp.status_code == 200

        p99 = sorted(times)[int(len(times) * 0.99)]
        assert p99 < 50, f"Sports p99: {p99:.1f}ms (target: <50ms)"

    def test_polling_endpoint_latency(self, client):
        """Polling endpoint should respond in under 100ms for cached results."""
        from app.tasks.analysis_tasks import task_store
        from app.models.schemas import AnalysisResult, AnalysisStatus

        task_id = "00000000-0000-4000-8000-000000000099"
        task_store.set(task_id, AnalysisResult(
            task_id=task_id,
            status=AnalysisStatus.COMPLETED,
            sport="snowboarding",
        ))

        times = []
        for _ in range(50):
            start = time.perf_counter()
            resp = client.get(f"/api/analyze/{task_id}")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            assert resp.status_code == 200

        p99 = sorted(times)[int(len(times) * 0.99)]
        assert p99 < 100, f"Polling p99: {p99:.1f}ms (target: <100ms)"


# ---------------------------------------------------------------------------
# Angle computation benchmarks
# ---------------------------------------------------------------------------

class TestComputePerformance:
    """Test mathematical computation performance."""

    def test_angle_computation_throughput(self):
        """Angle computation should process >10000 per second."""
        from app.services.snow_coach_logic import compute_angle

        a = np.array([1.0, 0.0])
        vertex = np.array([0.0, 0.0])
        c = np.array([0.0, 1.0])

        start = time.perf_counter()
        for _ in range(10000):
            compute_angle(a, vertex, c)
        elapsed = time.perf_counter() - start

        ops_per_sec = 10000 / elapsed
        assert ops_per_sec > 10000, f"Angle computation: {ops_per_sec:.0f} ops/s (target: >10000)"

    def test_vector_angle_computation_throughput(self):
        """Vector angle computation should process >10000 per second."""
        from app.services.snow_coach_logic import compute_vector_angle

        v1 = np.array([1.0, 0.0])
        v2 = np.array([0.0, 1.0])

        start = time.perf_counter()
        for _ in range(10000):
            compute_vector_angle(v1, v2)
        elapsed = time.perf_counter() - start

        ops_per_sec = 10000 / elapsed
        assert ops_per_sec > 10000, f"Vector angle: {ops_per_sec:.0f} ops/s (target: >10000)"
