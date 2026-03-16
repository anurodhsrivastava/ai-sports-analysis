"""
Saved Videos Router
GET    /my-videos          - List user's saved analysis records
GET    /my-videos/{id}     - Get a specific saved result
DELETE /my-videos/{id}     - Delete a saved result
POST   /my-videos/save     - Save analysis to user's account
"""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..db_models import AnalysisRecord, User
from ..dependencies import check_video_quota, get_current_user
from ..models.schemas import SavedVideoResponse
from ..tasks.analysis_tasks import get_task_result

router = APIRouter(prefix="/api/my-videos", tags=["videos"])


@router.get("/")
async def list_my_videos(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    sport: str = "",
):
    """List the current user's saved analyses."""
    query = db.query(AnalysisRecord).filter(AnalysisRecord.user_id == user.id)
    if sport:
        query = query.filter(AnalysisRecord.sport == sport)

    records = query.order_by(AnalysisRecord.created_at.desc()).all()
    return [
        SavedVideoResponse(
            id=r.id,
            task_id=r.task_id,
            sport=r.sport,
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else "",
            video_url=f"/results/{r.task_id}_annotated.mp4" if r.annotated_video_path else None,
        )
        for r in records
    ]


@router.get("/{record_id}")
async def get_my_video(
    record_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific saved analysis result."""
    record = db.query(AnalysisRecord).filter(
        AnalysisRecord.id == record_id,
        AnalysisRecord.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    result = None
    if record.result_json:
        result = json.loads(record.result_json)

    return {
        "id": record.id,
        "task_id": record.task_id,
        "sport": record.sport,
        "status": record.status,
        "result": result,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.delete("/{record_id}")
async def delete_my_video(
    record_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a saved analysis record and its files."""
    record = db.query(AnalysisRecord).filter(
        AnalysisRecord.id == record_id,
        AnalysisRecord.user_id == user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    # Clean up files
    if record.video_path:
        Path(record.video_path).unlink(missing_ok=True)
    if record.annotated_video_path:
        Path(record.annotated_video_path).unlink(missing_ok=True)

    db.delete(record)
    db.commit()
    return {"success": True, "message": "Record deleted."}


@router.post("/save")
async def save_analysis(
    request: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a completed analysis to the user's account."""
    task_id = request.get("task_id", "")
    if not task_id:
        raise HTTPException(status_code=400, detail="task_id is required.")

    # Check if already saved
    existing = db.query(AnalysisRecord).filter(AnalysisRecord.task_id == task_id).first()
    if existing:
        if existing.user_id == user.id:
            return {"success": True, "message": "Already saved.", "id": existing.id}
        if existing.user_id:
            raise HTTPException(status_code=403, detail="Analysis belongs to another user.")
        # Claim it
        existing.user_id = user.id
        db.commit()
        return {"success": True, "message": "Saved.", "id": existing.id}

    # Get the result from TaskStore
    result = get_task_result(task_id)
    if not result or result.status.value != "completed":
        raise HTTPException(status_code=404, detail="Analysis not found or not completed.")

    # Check quota
    check_video_quota(user, result.sport, db)

    # Determine file paths
    annotated_path = settings.results_dir / f"{task_id}_annotated.mp4"

    record = AnalysisRecord(
        user_id=user.id,
        task_id=task_id,
        sport=result.sport,
        status="completed",
        result_json=result.model_dump_json(),
        annotated_video_path=str(annotated_path) if annotated_path.exists() else None,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"success": True, "message": "Analysis saved.", "id": record.id}
