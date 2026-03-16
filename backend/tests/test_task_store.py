"""
Tests for the TaskStore and task orchestration.
"""

import json
import time
from pathlib import Path

import pytest

from app.models.schemas import AnalysisResult, AnalysisStatus
from app.tasks.analysis_tasks import TaskStore


@pytest.fixture
def store(tmp_path):
    return TaskStore(tmp_path / "tasks")


class TestTaskStore:
    def test_set_and_get(self, store):
        result = AnalysisResult(task_id="t1", status=AnalysisStatus.PROCESSING)
        store.set("t1", result)
        retrieved = store.get("t1")
        assert retrieved is not None
        assert retrieved.task_id == "t1"
        assert retrieved.status == AnalysisStatus.PROCESSING

    def test_get_nonexistent(self, store):
        assert store.get("nonexistent") is None

    def test_update_status(self, store):
        store.set("t1", AnalysisResult(task_id="t1", status=AnalysisStatus.PROCESSING))
        store.set("t1", AnalysisResult(task_id="t1", status=AnalysisStatus.COMPLETED))
        result = store.get("t1")
        assert result.status == AnalysisStatus.COMPLETED

    def test_persists_to_disk(self, tmp_path):
        store_dir = tmp_path / "tasks"
        store1 = TaskStore(store_dir)
        store1.set("t1", AnalysisResult(task_id="t1", status=AnalysisStatus.COMPLETED))

        # Create a new store from same directory — should load from disk
        store2 = TaskStore(store_dir)
        result = store2.get("t1")
        assert result is not None
        assert result.status == AnalysisStatus.COMPLETED

    def test_cleanup_old_tasks(self, store, tmp_path):
        store.set("t1", AnalysisResult(task_id="t1", status=AnalysisStatus.COMPLETED))

        # Manually make the file old
        task_file = store._store_dir / "t1.json"
        old_time = time.time() - 100 * 3600  # 100 hours ago
        import os
        os.utime(task_file, (old_time, old_time))

        removed = store.cleanup(max_age_hours=48)
        assert removed == 1
        assert store.get("t1") is None

    def test_cleanup_keeps_recent(self, store):
        store.set("t1", AnalysisResult(task_id="t1", status=AnalysisStatus.COMPLETED))
        removed = store.cleanup(max_age_hours=48)
        assert removed == 0
        assert store.get("t1") is not None

    def test_stores_sport(self, store):
        result = AnalysisResult(
            task_id="t1",
            status=AnalysisStatus.COMPLETED,
            sport="skiing",
        )
        store.set("t1", result)
        retrieved = store.get("t1")
        assert retrieved.sport == "skiing"

    def test_json_format_on_disk(self, store):
        store.set("t1", AnalysisResult(task_id="t1", status=AnalysisStatus.PROCESSING))
        task_file = store._store_dir / "t1.json"
        data = json.loads(task_file.read_text())
        assert data["task_id"] == "t1"
        assert data["status"] == "processing"
