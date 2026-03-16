"""
Tests for authentication and authorization flows.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.database import get_db, Base, engine
from app.db_models import User, UserRole, UserTier
from app.dependencies import create_access_token


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    from app import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


class TestRegistration:
    """Test email/password registration."""

    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "new@test.com",
            "password": "SecurePass123",
            "display_name": "New User",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["email"] == "new@test.com"
        assert data["jwt_token"] is not None
        assert data["tier"] == "free"

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "email": "dupe@test.com",
            "password": "Pass123",
        })
        resp = client.post("/api/auth/register", json={
            "email": "dupe@test.com",
            "password": "Pass456",
        })
        assert resp.status_code == 409

    def test_register_missing_fields(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "bad@test.com",
        })
        assert resp.status_code == 422


class TestLogin:
    """Test login flow."""

    def test_email_login_success(self, client):
        # Register first
        client.post("/api/auth/register", json={
            "email": "login@test.com",
            "password": "MyPass123",
        })
        # Login
        resp = client.post("/api/auth/login", json={
            "provider": "email",
            "token": "MyPass123",
            "email": "login@test.com",
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_email_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "login2@test.com",
            "password": "CorrectPass",
        })
        resp = client.post("/api/auth/login", json={
            "provider": "email",
            "token": "WrongPass",
            "email": "login2@test.com",
        })
        assert resp.status_code == 401

    def test_oauth_login_creates_user(self, client):
        resp = client.post("/api/auth/login", json={
            "provider": "google",
            "token": "mock-google-token-12345",
            "email": "oauth@test.com",
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True


class TestGetMe:
    """Test /auth/me endpoint."""

    def test_unauthenticated(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 200
        assert resp.json()["authenticated"] is False

    def test_authenticated(self, client):
        # Register
        reg = client.post("/api/auth/register", json={
            "email": "me@test.com",
            "password": "Pass123",
        }).json()
        token = reg["jwt_token"]

        resp = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["authenticated"] is True
        assert data["email"] == "me@test.com"
        assert data["tier"] == "free"
