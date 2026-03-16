"""
Analysis Router
POST      /analyze       - Upload video and start analysis
GET       /analyze/{id}  - Get analysis status/results
WebSocket /ws/{id}       - Real-time completion push (Fix #3)
"""

import asyncio
import os
import re
from pathlib import Path

import magic

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Form,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config import settings
from ..models.schemas import AnalysisResult, AnalysisStatus, UploadResponse
from ..sports.registry import SportRegistry
from ..tasks.analysis_tasks import create_task, get_task_result, run_analysis, wait_for_completion

limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.environ.get("ENVIRONMENT") != "testing",
)
router = APIRouter(prefix="/api", tags=["analysis"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
ALLOWED_MIMES = {"video/mp4", "video/x-msvideo", "video/quicktime", "video/x-matroska", "video/webm"}
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB
_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


@router.post("/analyze", response_model=UploadResponse)
@limiter.limit("10/hour")
async def upload_and_analyze(
    request: Request,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    sport: str = Form(default="snowboard"),
):
    """Upload a video for sport-specific analysis."""
    if not SportRegistry.has_sport(sport):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown sport '{sport}'. Available: {[s['sport_id'] for s in SportRegistry.list_sports()]}",
        )

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    upload_dir = settings.upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    task_id = create_task(file.filename, sport)
    save_path = upload_dir / f"{task_id}{ext}"

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    bytes_written = 0
    with open(save_path, "wb") as f:
        while True:
            chunk = await file.read(UPLOAD_CHUNK_SIZE)
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > max_bytes:
                save_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds {settings.max_upload_size_mb} MB limit.",
                )
            f.write(chunk)

    # Validate actual file content (magic number check)
    mime = magic.from_file(str(save_path), mime=True)
    if mime not in ALLOWED_MIMES:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=f"File content doesn't appear to be a valid video (detected: {mime}).",
        )

    background_tasks.add_task(run_analysis, task_id, save_path, sport)

    return UploadResponse(task_id=task_id, status=AnalysisStatus.PROCESSING, sport=sport)


@router.get("/analyze/{task_id}", response_model=AnalysisResult)
@limiter.limit("120/minute")
async def get_analysis(request: Request, task_id: str):
    """Get the status and results of an analysis task."""
    if not _UUID_RE.match(task_id):
        raise HTTPException(status_code=400, detail="Invalid task ID format.")
    result = get_task_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    return result


# ---------------------------------------------------------------------------
# Fix #3: WebSocket endpoint
# ---------------------------------------------------------------------------

@router.websocket("/ws/{task_id}")
async def analysis_ws(websocket: WebSocket, task_id: str):
    """WebSocket that sends the analysis result once it completes."""
    if not _UUID_RE.match(task_id):
        await websocket.close(code=1008, reason="Invalid task ID format")
        return
    await websocket.accept()
    try:
        result = get_task_result(task_id)
        if result and result.status != AnalysisStatus.PROCESSING:
            await websocket.send_json(result.model_dump(mode="json"))
            await websocket.close()
            return

        await wait_for_completion(task_id, timeout=1800)

        result = get_task_result(task_id)
        if result and result.status != AnalysisStatus.PROCESSING:
            await websocket.send_json(result.model_dump(mode="json"))
        await websocket.close()
    except WebSocketDisconnect:
        pass
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
