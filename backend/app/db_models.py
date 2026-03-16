"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


def _utcnow():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"
    SUPPORT = "support"
    TESTER = "tester"


class UserTier(str, PyEnum):
    FREE = "free"
    PRO = "pro"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False, default="User")
    password_hash = Column(String, nullable=True)  # null for OAuth users
    provider = Column(String, nullable=False, default="email")  # google/facebook/email
    provider_id = Column(String, nullable=True)  # OAuth provider user ID
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    tier = Column(Enum(UserTier), nullable=False, default=UserTier.FREE)
    stripe_customer_id = Column(String, nullable=True)
    locale = Column(String, nullable=False, default="en")
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

    analyses = relationship("AnalysisRecord", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    task_id = Column(String, nullable=False, unique=True, index=True)
    sport = Column(String, nullable=False)
    status = Column(String, nullable=False, default="completed")
    result_json = Column(Text, nullable=True)
    video_path = Column(String, nullable=True)
    annotated_video_path = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)

    user = relationship("User", back_populates="analyses")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    stripe_subscription_id = Column(String, nullable=True, unique=True)
    plan = Column(String, nullable=False, default="pro")
    status = Column(String, nullable=False, default="active")  # active/canceled/past_due
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)

    user = relationship("User", back_populates="subscriptions")


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(String, primary_key=True, default=_uuid)
    code = Column(String, unique=True, nullable=False, index=True)
    percent_off = Column(Float, nullable=True)
    amount_off = Column(Float, nullable=True)  # in cents
    max_uses = Column(Integer, nullable=True)
    times_used = Column(Integer, nullable=False, default=0)
    valid_until = Column(DateTime, nullable=True)
    active = Column(Integer, nullable=False, default=1)  # SQLite-friendly boolean
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
