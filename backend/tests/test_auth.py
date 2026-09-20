"""
Bloop Auth API Route & Rate Limiting Tests
Verifies registration, login, inactive account rejection, duplicate conflict handling,
and brute-force rate limiting defenses.
"""

import uuid
from fastapi.testclient import TestClient

from backend.app.models.user import User


def test_register_and_login(client: TestClient):
    uid = uuid.uuid4().hex[:8]
    email = f"tester_{uid}@example.com"
    password = "SuperSecretPassword123"

    # 1. Register
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert reg_res.status_code in (200, 201)
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data["data"]
    token = reg_data["data"]["access_token"]

    # 2. Login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["success"] is True
    assert login_data["data"]["user"]["email"] == email

    # 3. Access protected /me via header
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["data"]["email"] == email


def test_duplicate_registration_returns_409(client: TestClient):
    uid = uuid.uuid4().hex[:8]
    email = f"dup_{uid}@example.com"
    password = "SuperSecretPassword123"

    # First registration succeeds
    res_1 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert res_1.status_code == 201

    # Second registration with same email returns 409 Conflict
    res_2 = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert res_2.status_code == 409
    assert res_2.json()["success"] is False
    assert res_2.json()["error"]["code"] in ("CONFLICT", "RESOURCE_CONFLICT")


def test_login_invalid_password(client: TestClient):
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert res.status_code == 401
    assert res.json()["success"] is False
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_inactive_user_cannot_login(client: TestClient, db_session):
    uid = uuid.uuid4().hex[:8]
    email = f"inactive_{uid}@example.com"
    password = "SuperSecretPassword123"

    # Create inactive user directly in DB
    from backend.app.core.security import get_password_hash
    inactive_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()

    res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "ACCOUNT_INACTIVE"


def test_auth_rate_limiting(client: TestClient):
    """Verifies that exceeding the auth rate limit returns HTTP 429 Too Many Requests."""
    # settings.RATE_LIMIT_PER_MINUTE_AUTH is 5
    # Rapidly fire requests to trigger rate limiter
    responses = []
    for i in range(10):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": f"ratelimit_{i}@example.com", "password": "wrongpassword"},
            headers={"X-Test-Enforce-Rate-Limit": "true"},
        )
        responses.append(res.status_code)

    assert 429 in responses
