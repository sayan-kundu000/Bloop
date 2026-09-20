# User Data Isolation & Ownership Security

## 1. Security Threat Model: Insecure Direct Object References (IDOR)

In multi-tenant speech generation platforms, a critical security risk is IDOR, wherein an authenticated user alters an identifier (e.g. `generation_id` or `user_id`) to access, stream, download, or delete another user's private synthesized audio and transcripts.

Bloop prevents IDOR through a multi-layered server-side boundary:

```text
┌───────────────────────────────────┐
│        Incoming Request           │  (Cannot supply client user_id)
└─────────────────┬─────────────────┘
                  │
                  ▼
┌───────────────────────────────────┐
│       Session Authenticator       │  (deps.py: get_current_user)
│    Extracts sub claim from JWT    │  Verified against server SECRET_KEY
└─────────────────┬─────────────────┘
                  │
                  ▼
┌───────────────────────────────────┐
│     Current User (Canonical)      │  current_user.id authoritatively defined
└─────────────────┬─────────────────┘
                  │
                  ▼
┌───────────────────────────────────┐
│       Service Ownership Check     │
│   if gen.user_id != user.id:      │
│     raise AuthorizationException  │  HTTP 403 FORBIDDEN
└─────────────────┬─────────────────┘
                  │
                  ▼
┌───────────────────────────────────┐
│   Authorized Resource Delivery    │
└───────────────────────────────────┘
```

---

## 2. Server-Enforced Ownership Rules (Prompt 15 §18-19)

1. **Client `user_id` Ignored**:
   - Clients cannot specify `user_id` in request payloads or query strings.
   - Any attempt to pass `user_id` is disregarded; the backend binds all operations strictly to `current_user.id` resolved from the cryptographically signed JWT session.
2. **Strict Generation Isolation**:
   - `GET /api/v1/history` automatically appends `WHERE speech_generations.user_id = :current_user_id` to database queries. No cross-user records can ever be returned in listings.
3. **Single Record Inspection**:
   - `GET /api/v1/history/{id}` verifies `gen.user_id == current_user.id`. If a user attempts to access another user's ID, the server immediately denies access with HTTP 403 `FORBIDDEN`.
4. **Physical Asset Protection**:
   - `GET /api/v1/tts/{id}/audio` and `GET /api/v1/tts/{id}/download` perform ownership checks before opening or streaming files.
5. **Secure Deletion**:
   - `DELETE /api/v1/history/{id}` verifies ownership before deleting both the database row and the physical temporary audio file on server storage.

---

## 3. Automated Verification Matrix

| Test Case | Scenario | Expected Result | Verified In |
|---|---|---|---|
| Unauthenticated History | Request without token/cookie | HTTP 401 `AUTHENTICATION_REQUIRED` | `test_history_isolation.py` |
| List History Isolation | User A requests `/history` | Only User A generations returned | `test_history_isolation.py` |
| Detail Access IDOR | User A requests User B generation | HTTP 403 `FORBIDDEN` | `test_history_isolation.py` |
| Delete Access IDOR | User A deletes User B generation | HTTP 403 `FORBIDDEN` | `test_history_isolation.py` |
| Client Override Defense | Query param `?user_id=other` | Ignored; only owner data returned | `test_history_isolation.py` |
| Asset Cleanup on Delete | Owner deletes generation | Row deleted + disk audio file purged | `test_history_service.py` |
