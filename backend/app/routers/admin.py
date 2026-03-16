"""
Admin Dashboard Router
All endpoints require admin role.
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..db_models import (
    AnalysisRecord,
    DiscountCode,
    Subscription,
    User,
    UserRole,
    UserTier,
)
from ..dependencies import require_role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])

_admin = require_role("admin")


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------

@router.get("/stats")
async def admin_stats(
    _user=Depends(_admin),
    db: Session = Depends(get_db),
):
    """Overview stats for the admin dashboard."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    pro_users = db.query(func.count(User.id)).filter(User.tier == UserTier.PRO).scalar() or 0
    total_analyses = db.query(func.count(AnalysisRecord.id)).scalar() or 0
    active_subs = (
        db.query(func.count(Subscription.id))
        .filter(Subscription.status == "active")
        .scalar() or 0
    )
    total_discount_codes = db.query(func.count(DiscountCode.id)).scalar() or 0

    return {
        "total_users": total_users,
        "pro_users": pro_users,
        "total_analyses": total_analyses,
        "active_subscriptions": active_subs,
        "total_discount_codes": total_discount_codes,
    }


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

@router.get("/users")
async def list_users(
    _user=Depends(_admin),
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 20,
    search: str = "",
    role: str = "",
):
    """List users with pagination and optional search/filter."""
    query = db.query(User)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | (User.display_name.ilike(f"%{search}%"))
        )
    if role:
        query = query.filter(User.role == role)

    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "display_name": u.display_name,
                "role": u.role.value if isinstance(u.role, UserRole) else u.role,
                "tier": u.tier.value if isinstance(u.tier, UserTier) else u.tier,
                "provider": u.provider,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
    }


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    request: Request,
    _user=Depends(_admin),
    db: Session = Depends(get_db),
):
    """Change a user's role."""
    body = await request.json()
    new_role = body.get("role")
    if new_role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail=f"Invalid role: {new_role}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.role = UserRole(new_role)
    db.commit()
    return {"success": True, "user_id": user_id, "role": new_role}


@router.patch("/users/{user_id}/tier")
async def update_user_tier(
    user_id: str,
    request: Request,
    _user=Depends(_admin),
    db: Session = Depends(get_db),
):
    """Manually set a user's tier (admin override)."""
    body = await request.json()
    new_tier = body.get("tier")
    if new_tier not in [t.value for t in UserTier]:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {new_tier}")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.tier = UserTier(new_tier)
    db.commit()
    return {"success": True, "user_id": user_id, "tier": new_tier}


# ---------------------------------------------------------------------------
# Discount codes
# ---------------------------------------------------------------------------

@router.get("/discount-codes")
async def list_discount_codes(
    _user=Depends(_admin),
    db: Session = Depends(get_db),
):
    """List all discount codes."""
    codes = db.query(DiscountCode).order_by(DiscountCode.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "code": c.code,
            "percent_off": c.percent_off,
            "amount_off": c.amount_off,
            "max_uses": c.max_uses,
            "times_used": c.times_used,
            "valid_until": c.valid_until.isoformat() if c.valid_until else None,
            "active": bool(c.active),
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in codes
    ]


@router.post("/discount-codes")
async def create_discount_code(
    request: Request,
    admin_user=Depends(_admin),
    db: Session = Depends(get_db),
):
    """Create a new discount code."""
    body = await request.json()
    code_str = body.get("code", "").strip().upper()
    if not code_str:
        raise HTTPException(status_code=400, detail="Code is required.")

    existing = db.query(DiscountCode).filter(DiscountCode.code == code_str).first()
    if existing:
        raise HTTPException(status_code=409, detail="Code already exists.")

    valid_until = None
    if body.get("valid_until"):
        valid_until = datetime.fromisoformat(body["valid_until"]).replace(tzinfo=timezone.utc)

    code = DiscountCode(
        code=code_str,
        percent_off=body.get("percent_off"),
        amount_off=body.get("amount_off"),
        max_uses=body.get("max_uses"),
        valid_until=valid_until,
        created_by=admin_user.id,
    )
    db.add(code)
    db.commit()
    db.refresh(code)

    return {
        "success": True,
        "id": code.id,
        "code": code.code,
    }


@router.delete("/discount-codes/{code_id}")
async def deactivate_discount_code(
    code_id: str,
    _user=Depends(_admin),
    db: Session = Depends(get_db),
):
    """Deactivate a discount code."""
    code = db.query(DiscountCode).filter(DiscountCode.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Discount code not found.")
    code.active = 0
    db.commit()
    return {"success": True, "message": f"Code {code.code} deactivated."}


# ---------------------------------------------------------------------------
# Analysis records
# ---------------------------------------------------------------------------

@router.get("/analyses")
async def list_analyses(
    _user=Depends(_admin),
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 20,
    sport: str = "",
):
    """List recent analysis records."""
    query = db.query(AnalysisRecord)
    if sport:
        query = query.filter(AnalysisRecord.sport == sport)

    total = query.count()
    records = (
        query.order_by(AnalysisRecord.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "analyses": [
            {
                "id": r.id,
                "task_id": r.task_id,
                "user_id": r.user_id,
                "sport": r.sport,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ],
    }
