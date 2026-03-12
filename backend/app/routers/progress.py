"""
Progress Router
GET /api/progress - Returns score/grade history for the current user's analyses
"""

import json
import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_models import AnalysisRecord, User
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/")
async def get_progress(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    sport: str = Query("", description="Filter by sport"),
):
    """Return score/grade history for the user's saved analyses."""
    query = db.query(AnalysisRecord).filter(
        AnalysisRecord.user_id == user.id,
        AnalysisRecord.status == "completed",
    )
    if sport:
        query = query.filter(AnalysisRecord.sport == sport)

    records = query.order_by(AnalysisRecord.created_at.asc()).all()

    entries = []
    for r in records:
        score = None
        grade = None
        if r.result_json:
            try:
                data = json.loads(r.result_json)
                cs = data.get("coaching_summary") or {}
                score = cs.get("overall_score")
                grade = cs.get("overall_grade")
            except (json.JSONDecodeError, AttributeError):
                pass
        entries.append({
            "task_id": r.task_id,
            "sport": r.sport,
            "score": score,
            "grade": grade,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return entries
