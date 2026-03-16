"""
Tests for admin dashboard endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db, Base, engine
from app.db_models import User, UserRole, UserTier
from app.dependencies import create_access_token


@pytest.fixture(autouse=True)
def setup_db():
    from app import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


def _create_admin(client):
    """Create an admin user and return the JWT token."""
    reg = client.post("/api/auth/register", json={
        "email": "admin@test.com",
        "password": "Admin123",
        "display_name": "Admin",
    }).json()
    token = reg["jwt_token"]

    # Manually update role to admin
    from app.database import SessionLocal
    from app.db_models import User, UserRole
    db = SessionLocal()
    user = db.query(User).filter(User.email == "admin@test.com").first()
    user.role = UserRole.ADMIN
    db.commit()

    # Re-create token with admin role
    token = create_access_token({"sub": user.id, "email": user.email, "role": "admin"})
    db.close()
    return token


class TestAdminStats:

    def test_admin_gets_stats(self, client):
        token = _create_admin(client)
        resp = client.get("/api/admin/stats", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "pro_users" in data
        assert data["total_users"] >= 1

    def test_non_admin_denied(self, client):
        reg = client.post("/api/auth/register", json={
            "email": "user@test.com",
            "password": "User123",
        }).json()
        resp = client.get("/api/admin/stats", headers={
            "Authorization": f"Bearer {reg['jwt_token']}",
        })
        assert resp.status_code == 403


class TestUserManagement:

    def test_list_users(self, client):
        token = _create_admin(client)
        # Create some users
        client.post("/api/auth/register", json={
            "email": "u1@test.com", "password": "Pass123",
        })
        client.post("/api/auth/register", json={
            "email": "u2@test.com", "password": "Pass123",
        })

        resp = client.get("/api/admin/users", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3  # admin + 2 users

    def test_update_role(self, client):
        token = _create_admin(client)
        reg = client.post("/api/auth/register", json={
            "email": "promote@test.com", "password": "Pass123",
        }).json()

        resp = client.patch(
            f"/api/admin/users/{reg['user_id']}/role",
            json={"role": "support"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "support"

    def test_update_tier(self, client):
        token = _create_admin(client)
        reg = client.post("/api/auth/register", json={
            "email": "upgrade@test.com", "password": "Pass123",
        }).json()

        resp = client.patch(
            f"/api/admin/users/{reg['user_id']}/tier",
            json={"tier": "pro"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["tier"] == "pro"

    def test_invalid_role_rejected(self, client):
        token = _create_admin(client)
        reg = client.post("/api/auth/register", json={
            "email": "bad@test.com", "password": "Pass123",
        }).json()

        resp = client.patch(
            f"/api/admin/users/{reg['user_id']}/role",
            json={"role": "superadmin"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400


class TestDiscountCodes:

    def test_create_and_list(self, client):
        token = _create_admin(client)

        # Create
        resp = client.post(
            "/api/admin/discount-codes",
            json={"code": "SAVE20", "percent_off": 20, "max_uses": 100},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == "SAVE20"

        # List
        resp = client.get("/api/admin/discount-codes", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        codes = resp.json()
        assert len(codes) >= 1
        assert any(c["code"] == "SAVE20" for c in codes)

    def test_duplicate_code_rejected(self, client):
        token = _create_admin(client)
        client.post(
            "/api/admin/discount-codes",
            json={"code": "DUP1", "percent_off": 10},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.post(
            "/api/admin/discount-codes",
            json={"code": "DUP1", "percent_off": 15},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 409

    def test_deactivate_code(self, client):
        token = _create_admin(client)
        create_resp = client.post(
            "/api/admin/discount-codes",
            json={"code": "DEACT1", "percent_off": 5},
            headers={"Authorization": f"Bearer {token}"},
        ).json()

        resp = client.delete(
            f"/api/admin/discount-codes/{create_resp['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        # Verify it's deactivated
        codes = client.get("/api/admin/discount-codes", headers={
            "Authorization": f"Bearer {token}",
        }).json()
        code = next(c for c in codes if c["code"] == "DEACT1")
        assert code["active"] is False
