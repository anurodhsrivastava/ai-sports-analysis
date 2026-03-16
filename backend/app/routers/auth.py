"""
Authentication Router
POST /auth/login       - Login via OAuth provider or email/password
POST /auth/register    - Register with email/password
POST /auth/guest-save  - Save results for guest users after login
GET  /auth/me          - Get current user info
"""

import hashlib
import hmac
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


def _hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + dk.hex()


def _verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        salt_hex, dk_hex = stored.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, AttributeError):
        return False

from ..database import get_db
from ..db_models import User, UserRole, UserTier
from ..dependencies import create_access_token, get_current_user, get_current_user_optional
from ..models.schemas import (
    AuthProvider,
    GuestSaveRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserProfile,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new account with email and password."""
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        email=request.email,
        display_name=request.display_name or request.email.split("@")[0],
        password_hash=_hash_password(request.password),
        provider="email",
        role=UserRole.USER,
        tier=UserTier.FREE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role.value})
    return RegisterResponse(
        success=True,
        user_id=user.id,
        display_name=user.display_name,
        email=user.email,
        jwt_token=token,
        tier=user.tier.value,
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate via email/password or OAuth provider."""
    if request.provider == AuthProvider.EMAIL:
        # Email/password login
        user = db.query(User).filter(User.email == request.email).first()
        if not user or not user.password_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        if not _verify_password(request.token, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
    else:
        # OAuth login — find or create user
        provider_id = f"{request.provider.value}_{request.token[:20]}"
        user = db.query(User).filter(
            User.provider == request.provider.value,
            User.provider_id == provider_id,
        ).first()

        if not user:
            email = request.email or f"{provider_id}@oauth.local"
            user = User(
                email=email,
                display_name=request.email.split("@")[0] if request.email else "User",
                provider=request.provider.value,
                provider_id=provider_id,
                role=UserRole.USER,
                tier=UserTier.FREE,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role.value})
    return LoginResponse(
        success=True,
        user_id=user.id,
        display_name=user.display_name,
        email=user.email,
        jwt_token=token,
        tier=user.tier.value,
        message=f"Logged in via {request.provider.value}",
    )


@router.post("/guest-save")
async def guest_save(
    request: GuestSaveRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Associate a guest analysis task with the authenticated user's account."""
    from ..db_models import AnalysisRecord

    record = db.query(AnalysisRecord).filter(AnalysisRecord.task_id == request.task_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if record.user_id and record.user_id != user.id:
        raise HTTPException(status_code=403, detail="Analysis belongs to another user.")

    record.user_id = user.id
    db.commit()
    return {"success": True, "message": f"Results for task {request.task_id} saved to your account."}


@router.get("/me", response_model=UserProfile)
async def get_me(user: User | None = Depends(get_current_user_optional)):
    """Get info about the currently authenticated user."""
    if user is None:
        return UserProfile(authenticated=False)
    return UserProfile(
        authenticated=True,
        user_id=user.id,
        display_name=user.display_name,
        email=user.email,
        role=user.role.value,
        tier=user.tier.value,
    )
