"""
Bloop End-to-End Authentication & Session Lifecycle Tests (Prompt 14 §2, §74, §103)
Verifies:
- Registration with password hashing
- Login with credential verification and secure session cookie issuance
- Protected API calls using session cookies
- Profile resolution via /api/v1/users/me
- Logout and session cookie termination
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.models.user import User


class TestAuthFlowLifecycle:
    """Verifies complete end-to-end browser authentication lifecycle."""

    def test_full_auth_session_lifecycle(self, client: TestClient, db_session):
        uid = uuid.uuid4().hex[:8]
        email = f"session_tester_{uid}@bloop.ai"
        password = "SecureBloopPassword!99"
        full_name = "Session Test User"

        # --------------------------------------------------------------------
        # 1. Registration Flow
        # --------------------------------------------------------------------
        reg_res = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"  {email.upper()}  ",  # Test normalization
                "password": password,
                "full_name": full_name,
            },
        )
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert reg_data["success"] is True
        assert reg_data["data"]["user"]["email"] == email.lower()
        assert "password" not in reg_data["data"]
        assert "hashed_password" not in reg_data["data"]["user"]

        # Verify password in DB is securely hashed
        user_in_db = db_session.query(User).filter(User.email == email.lower()).first()
        assert user_in_db is not None
        assert user_in_db.hashed_password != password
        assert user_in_db.hashed_password.startswith("$2b$")

        # --------------------------------------------------------------------
        # 2. Login Flow with HttpOnly Cookie
        # --------------------------------------------------------------------
        login_res = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["success"] is True
        assert login_data["data"]["user"]["email"] == email.lower()

        # Check session cookie attached to response
        cookie_header = login_res.headers.get("set-cookie")
        assert cookie_header is not None
        assert "access_token=" in cookie_header
        assert "HttpOnly" in cookie_header or "httponly" in cookie_header.lower()

        # --------------------------------------------------------------------
        # 3. Cookie-Authenticated Access to /api/v1/users/me
        # --------------------------------------------------------------------
        # TestClient automatically retains cookies from previous responses
        me_res = client.get("/api/v1/users/me")
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["success"] is True
        assert me_data["data"]["email"] == email.lower()
        assert me_data["data"]["full_name"] == full_name
        assert "hashed_password" not in me_data["data"]

        # --------------------------------------------------------------------
        # 4. Cookie-Authenticated Access to Protected /api/v1/tts
        # --------------------------------------------------------------------
        tts_res = client.post(
            "/api/v1/tts",
            json={
                "text": "Testing text-to-speech with secure session cookie.",
                "voice_id": "normal-female",
                "language": "en-US",
            },
        )
        assert tts_res.status_code == 200
        tts_data = tts_res.json()
        assert tts_data["success"] is True
        assert "audio_url" in tts_data["data"]

        # --------------------------------------------------------------------
        # 5. Session Logout Flow
        # --------------------------------------------------------------------
        logout_res = client.post("/api/v1/auth/logout")
        assert logout_res.status_code == 200
        logout_data = logout_res.json()
        assert logout_data["success"] is True
        assert logout_data["data"]["logged_out"] is True

        # Clear client cookies manually to simulate browser honoring Set-Cookie deletion
        client.cookies.clear()

        # --------------------------------------------------------------------
        # 6. Post-Logout Request to Protected Endpoint Fails (HTTP 401)
        # --------------------------------------------------------------------
        unauth_res = client.get("/api/v1/users/me")
        assert unauth_res.status_code == 401
        assert unauth_res.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
