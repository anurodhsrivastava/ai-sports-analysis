"""FastAPI dependencies for auth, roles, and quotas."""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .db_models import AnalysisRecord, User, UserRole, UserTier

_bearer = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"


def _decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])


def create_access_token(data: dict) -> str:
    """Create a signed JWT."""
    return jwt.encode(data, settings.jwt_secret, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Extract authenticated user from JWT. Raises 401 if invalid."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = _decode_token(credentials.credentials)
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User | None:
    """Return user if authenticated, None otherwise."""
    if credentials is None:
        return None
    try:
        payload = _decode_token(credentials.credentials)
        user_id = payload.get("sub", "")
        if not user_id:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_role(*roles: str):
    """Dependency factory: require user to have one of the given roles."""
    async def _check(user: User = Depends(get_current_user)):
        if user.role.value not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return _check


def check_video_quota(user: User, sport: str, db: Session) -> None:
    """Raise 403 if user has exceeded their tier's video storage limit."""
    limit = (
        settings.pro_tier_videos_per_sport
        if user.tier == UserTier.PRO
        else settings.free_tier_videos_per_sport
    )
    count = (
        db.query(AnalysisRecord)
        .filter(AnalysisRecord.user_id == user.id, AnalysisRecord.sport == sport)
        .count()
    )
    if count >= limit:
        tier_name = "Pro" if user.tier == UserTier.PRO else "Free"
        raise HTTPException(
            status_code=403,
            detail=f"{tier_name} tier allows {limit} saved video(s) per sport. "
            f"You have {count}. Upgrade to Pro for more storage.",
        )
