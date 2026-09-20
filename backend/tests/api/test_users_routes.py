"""
API Tests — Users and Preferences Domain Endpoints
Verifies /api/v1/users/me profile and preference management.
"""

import pytest
from fastapi.testclient import TestClient


def test_get_current_user_profile_unauthenticated(client: TestClient):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_get_and_update_user_preferences(client: TestClient):
    email = "preference_tester@example.com"
    password = "SecurePassword456!"

    # 1. Register a test user
    reg_res = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Preference Tester"},
    )
    assert reg_res.status_code in (200, 201)
    token = reg_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Retrieve user profile via /api/v1/users/me
    profile_res = client.get("/api/v1/users/me", headers=headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert profile_data["success"] is True
    assert profile_data["data"]["email"] == email
    assert profile_data["data"]["preference"] is not None
    assert profile_data["data"]["preference"]["theme"] == "dark"

    # 3. Update user preferences
    patch_res = client.patch(
        "/api/v1/users/me/preferences",
        headers=headers,
        json={"theme": "light", "audio_speed": 1.25, "auto_play": False},
    )
    assert patch_res.status_code == 200
    patch_data = patch_res.json()
    assert patch_data["success"] is True
    assert patch_data["data"]["theme"] == "light"
    assert patch_data["data"]["audio_speed"] == 1.25
    assert patch_data["data"]["auto_play"] is False

    # 4. Verify updated preferences persist in subsequent /users/me query
    recheck_res = client.get("/api/v1/users/me", headers=headers)
    assert recheck_res.status_code == 200
    recheck_data = recheck_res.json()
    assert recheck_data["data"]["preference"]["theme"] == "light"
    assert recheck_data["data"]["preference"]["audio_speed"] == 1.25
    assert recheck_data["data"]["preference"]["auto_play"] is False
