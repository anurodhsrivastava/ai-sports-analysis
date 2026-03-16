"""Shared test fixtures."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "testing"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def test_db():
    """Create a test database."""
    from app.database import Base
    from app import db_models  # noqa: F401

    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    yield TestSession

    Base.metadata.drop_all(bind=engine)
    try:
        os.unlink("./test.db")
    except OSError:
        pass


@pytest.fixture
def db_session(test_db):
    """Get a fresh database session for each test."""
    session = test_db()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    from app.db_models import User, UserRole, UserTier
    from app.dependencies import create_access_token

    user = User(
        email="admin@test.com",
        display_name="Admin",
        role=UserRole.ADMIN,
        tier=UserTier.PRO,
        provider="email",
        password_hash="$2b$12$dummy",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": "admin"})
    return user, token


@pytest.fixture
def regular_user(db_session):
    """Create a regular user for testing."""
    from app.db_models import User, UserRole, UserTier
    from app.dependencies import create_access_token

    user = User(
        email="user@test.com",
        display_name="TestUser",
        role=UserRole.USER,
        tier=UserTier.FREE,
        provider="email",
        password_hash="$2b$12$dummy",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": "user"})
    return user, token
