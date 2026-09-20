"""
Comprehensive API Contract & Schema Integration Tests (Prompt 09)
Validates JSON success and error envelopes, HTTP status codes, Pydantic schemas,
pagination metadata, ownership boundaries, and OpenAPI contracts across all 9 domain routers.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.core.config import Settings
from backend.app.core.exceptions import ErrorCode
from backend.app.factory import create_app


import uuid


@pytest.fixture
def auth_tokens(client: TestClient):
    """Creates two distinct user accounts (User A and User B) for ownership isolation tests."""
    uid = uuid.uuid4().hex[:8]
    email_a = f"contract_user_a_{uid}@example.com"
    email_b = f"contract_user_b_{uid}@example.com"
    pwd = "ContractPassword123!"

    res_a = client.post("/api/v1/auth/register", json={"email": email_a, "password": pwd, "full_name": "User Alpha"})
    assert res_a.status_code == 201
    token_a = res_a.json()["data"]["access_token"]

    res_b = client.post("/api/v1/auth/register", json={"email": email_b, "password": pwd, "full_name": "User Beta"})
    assert res_b.status_code == 201
    token_b = res_b.json()["data"]["access_token"]

    return {
        "user_a": {"token": token_a, "headers": {"Authorization": f"Bearer {token_a}"}, "email": email_a},
        "user_b": {"token": token_b, "headers": {"Authorization": f"Bearer {token_b}"}, "email": email_b},
    }


class TestAuthenticationContracts:
    """Verifies /api/v1/auth contracts, status codes, and error envelopes."""

    def test_register_duplicate_returns_409(self, client: TestClient, auth_tokens):
        res = client.post(
            "/api/v1/auth/register",
            json={"email": auth_tokens["user_a"]["email"], "password": "AnyPassword123!"},
        )
        assert res.status_code == 409
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] in (ErrorCode.RESOURCE_CONFLICT, ErrorCode.CONFLICT)

    def test_login_invalid_credentials_returns_401(self, client: TestClient):
        res = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "WrongPassword"},
        )
        assert res.status_code == 401
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.INVALID_CREDENTIALS

    def test_logout_contract(self, client: TestClient, auth_tokens):
        res = client.post(
            "/api/v1/auth/logout",
            headers=auth_tokens["user_a"]["headers"],
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["logged_out"] is True

    def test_unauthenticated_profile_returns_401(self, client: TestClient):
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 401
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.AUTHENTICATION_REQUIRED


class TestUsersContracts:
    """Verifies /api/v1/users profile and preference manipulation contracts."""

    def test_get_and_patch_user_profile(self, client: TestClient, auth_tokens):
        headers = auth_tokens["user_a"]["headers"]

        # 1. Get current profile
        res = client.get("/api/v1/users/me", headers=headers)
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["full_name"] == "User Alpha"
        assert body["data"]["preference"] is not None

        # 2. Patch profile display name
        patch_res = client.patch(
            "/api/v1/users/me",
            headers=headers,
            json={"full_name": "User Alpha Renamed"},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["data"]["full_name"] == "User Alpha Renamed"

        # 3. Patch preferences
        pref_res = client.patch(
            "/api/v1/users/me/preferences",
            headers=headers,
            json={"theme": "system", "audio_speed": 1.75, "auto_play": False},
        )
        assert pref_res.status_code == 200
        pref_data = pref_res.json()["data"]
        assert pref_data["theme"] == "system"
        assert pref_data["audio_speed"] == 1.75
        assert pref_data["auto_play"] is False


class TestLanguagesAndVoicesContracts:
    """Verifies dynamic catalogue retrieval without static voice pollution."""

    def test_languages_contract(self, client: TestClient):
        res = client.get("/api/v1/languages")
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        codes = [item["code"] for item in body["data"]]
        assert "en" in codes or "en-US" in codes or len(codes) > 0

    def test_voices_dynamic_contract(self, client: TestClient):
        res = client.get("/api/v1/voices")
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)


class TestTTSContracts:
    """Verifies Text-to-Speech synthesis contracts, validation rules, and streaming."""

    def test_tts_text_validation_boundaries(self, client: TestClient, auth_tokens):
        headers = auth_tokens["user_a"]["headers"]

        # Empty text
        res1 = client.post("/api/v1/tts", json={"text": "", "voice_id": "test_voice"}, headers=headers)
        assert res1.status_code == 422
        assert res1.json()["error"]["code"] in (ErrorCode.TEXT_EMPTY, ErrorCode.VALIDATION_ERROR)

        # Whitespace-only text
        res2 = client.post("/api/v1/tts", json={"text": "   \n\t  ", "voice_id": "test_voice"}, headers=headers)
        assert res2.status_code == 422
        assert res2.json()["error"]["code"] in (ErrorCode.TEXT_EMPTY, ErrorCode.VALIDATION_ERROR)

        # Text exceeding 2,500 characters
        res3 = client.post("/api/v1/tts", json={"text": "A" * 2501, "voice_id": "test_voice"}, headers=headers)
        assert res3.status_code == 422
        assert res3.json()["error"]["code"] in (ErrorCode.TEXT_TOO_LONG, ErrorCode.VALIDATION_ERROR)

    def test_tts_analyze_endpoint_contract(self, client: TestClient):
        res = client.post("/api/v1/tts/analyze", json={"text": "Hello world from Bloop text analyzer."})
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["char_count"] > 0
        assert body["data"]["word_count"] > 0
        assert body["data"]["is_valid"] is True


class TestHistoryAndOwnershipContracts:
    """Verifies pagination metadata and cross-user ownership isolation."""

    def test_history_pagination_and_ownership(self, client: TestClient, auth_tokens):
        headers_a = auth_tokens["user_a"]["headers"]
        headers_b = auth_tokens["user_b"]["headers"]

        # Generate speech under User A
        tts_res = client.post(
            "/api/v1/tts",
            headers=headers_a,
            json={"text": "Speech exclusively for User A", "voice_id": "sim_voice_1"},
        )
        assert tts_res.status_code == 200
        gen_id = tts_res.json()["data"]["generation_id"]
        assert gen_id is not None

        # 1. User A retrieves history with pagination meta
        hist_a = client.get("/api/v1/history", headers=headers_a)
        assert hist_a.status_code == 200
        body_a = hist_a.json()
        assert body_a["success"] is True
        assert "meta" in body_a
        assert body_a["meta"]["page"] == 1
        assert body_a["meta"]["total_pages"] >= 1
        gen_ids_a = [item["id"] for item in body_a["data"]["items"]]
        assert gen_id in gen_ids_a

        # 2. User A retrieves single generation by ID
        single_res = client.get(f"/api/v1/history/{gen_id}", headers=headers_a)
        assert single_res.status_code == 200
        assert single_res.json()["data"]["id"] == gen_id

        # 3. Ownership Isolation: User B tries to retrieve User A's private generation
        cross_res = client.get(f"/api/v1/history/{gen_id}", headers=headers_b)
        assert cross_res.status_code == 403
        assert cross_res.json()["error"]["code"] in (ErrorCode.ACCESS_DENIED, ErrorCode.FORBIDDEN)

        # 4. Ownership Isolation: User B tries to delete User A's private generation
        del_cross = client.delete(f"/api/v1/history/{gen_id}", headers=headers_b)
        assert del_cross.status_code == 403
        assert del_cross.json()["error"]["code"] in (ErrorCode.ACCESS_DENIED, ErrorCode.FORBIDDEN)


class TestFavoritesContracts:
    """Verifies bookmark creation, duplicate conflicts (409), and ownership deletion."""

    def test_favorites_lifecycle_and_conflict(self, client: TestClient, auth_tokens):
        headers_a = auth_tokens["user_a"]["headers"]
        headers_b = auth_tokens["user_b"]["headers"]

        # Create speech generation
        tts_res = client.post(
            "/api/v1/tts",
            headers=headers_a,
            json={"text": "Speech for favorite testing", "voice_id": "sim_voice_fav"},
        )
        gen_id = tts_res.json()["data"]["generation_id"]

        # 1. Add favorite (201 Created)
        fav_res = client.post(
            "/api/v1/favorites",
            headers=headers_a,
            json={"generation_id": gen_id, "label": "Key Generation"},
        )
        assert fav_res.status_code == 201
        fav_data = fav_res.json()["data"]
        fav_id = fav_data["id"]

        # 2. Duplicate favorite attempt must return 409 Conflict
        dup_res = client.post(
            "/api/v1/favorites",
            headers=headers_a,
            json={"generation_id": gen_id},
        )
        assert dup_res.status_code == 409
        assert dup_res.json()["error"]["code"] in (ErrorCode.RESOURCE_CONFLICT, ErrorCode.CONFLICT)

        # 3. Ownership Protection: User B cannot delete User A's favorite
        del_b = client.delete(f"/api/v1/favorites/{fav_id}", headers=headers_b)
        assert del_b.status_code == 403
        assert del_b.json()["error"]["code"] in (ErrorCode.ACCESS_DENIED, ErrorCode.FORBIDDEN)

        # 4. User A deletes own favorite (200 OK)
        del_a = client.delete(f"/api/v1/favorites/{fav_id}", headers=headers_a)
        assert del_a.status_code == 200
        assert del_a.json()["data"]["deleted_id"] == fav_id


class TestQuantumContractsAndIsolation:
    """Verifies quantum intelligence contracts and controlled 503 when disabled."""

    def test_quantum_endpoints_when_enabled(self, client: TestClient, auth_tokens):
        headers = auth_tokens["user_a"]["headers"]
        # When enabled (default test environment)
        res = client.post(
            "/api/v1/quantum/text",
            json={"text": "Quantum sentiment prompt", "num_qubits": 4, "shots": 512},
            headers=headers,
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert "predicted_style" in body["data"]

    def test_quantum_disabled_returns_503(self):
        settings = Settings(
            APP_NAME="Bloop Quantum Disabled",
            APP_ENV="development",
            APP_DEBUG=True,
            QUANTUM_ENABLED=False,
            DATABASE_URL="sqlite:///./test_quantum_disabled.db",
            JWT_SECRET_KEY="a" * 32,
        )
        app = create_app(custom_settings=settings)
        test_client = TestClient(app)

        res = test_client.post(
            "/api/v1/quantum/text",
            json={"text": "Test with quantum disabled", "num_qubits": 4, "shots": 512},
        )
        assert res.status_code == 503
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == ErrorCode.QUANTUM_DISABLED


class TestOpenAPIContract:
    """Verifies OpenAPI schema reflects all domain routes, tags, and zero secret exposure."""

    def test_openapi_schema_completeness(self):
        settings = Settings(
            APP_NAME="Bloop API Docs",
            APP_ENV="development",
            APP_DEBUG=True,
            DATABASE_URL="sqlite:///./test_docs.db",
            JWT_SECRET_KEY="a" * 32,
        )
        app = create_app(custom_settings=settings)
        test_client = TestClient(app)

        res = test_client.get("/api/v1/openapi.json")
        assert res.status_code == 200
        schema = res.json()

        # Check required tags
        tag_names = {t["name"] for t in schema.get("tags", [])}
        for tag in ["Health", "Authentication", "Users", "Languages", "Voices", "Speech", "History", "Favorites", "Quantum"]:
            assert tag in tag_names

        # Check key endpoint paths
        paths = schema.get("paths", {})
        assert "/api/v1/auth/register" in paths
        assert "/api/v1/auth/login" in paths
        assert "/api/v1/auth/logout" in paths
        assert "/api/v1/users/me" in paths
        assert "/api/v1/languages" in paths
        assert "/api/v1/voices" in paths
        assert "/api/v1/tts" in paths
        assert "/api/v1/tts/analyze" in paths
        assert "/api/v1/history" in paths
        assert "/api/v1/history/{generation_id}" in paths
        assert "/api/v1/favorites" in paths
        assert "/api/v1/favorites/{favorite_id}" in paths
        assert "/api/v1/quantum/text" in paths

        # Verify zero secret or credential leakage in schema
        schema_text = str(schema)
        assert "JWT_SECRET_KEY" not in schema_text
        assert "ELEVENLABS_API_KEY" not in schema_text
        assert "hashed_password" not in schema_text
