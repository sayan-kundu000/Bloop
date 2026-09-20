# Bloop Authentication Architecture

## 1. Executive Summary

Bloop implements an **intermediate-level, production-conscious authentication architecture** providing a robust security boundary between untrusted clients (React / Vercel) and protected backend services (FastAPI / Render, PostgreSQL, ElevenLabs, Quantum Intelligence).

```text
React / Vercel
      │
      │ HTTPS (Credentials Included)
      ▼
FastAPI / Render
      │
      ├── Session Extraction (HttpOnly Cookie / Bearer Header)
      ├── JWT Signature & Claims Validation (sub, exp, iat)
      ├── User Status Verification (is_active = True)
      ├── Authorization & Ownership Verification (user_id)
      │
      ├── PostgreSQL
      ├── ElevenLabs TTS Provider (Isolated)
      └── Quantum Subsystem (Resource-Guarded)
```

---

## 2. Core Identity Flow

Identity answering **"Who is this user?"** is strictly separated from authorization answering **"Can this user access this resource?"**.

```text
Register / Login
       │
       ▼
Password Hashing / Verification (Salted Bcrypt)
       │
       ▼
JWT Issuance (HS256 with Sub, Exp, Iat)
       │
       ▼
Secure Session Cookie (HttpOnly, SameSite, Secure)
       │
       ▼
Protected API Request
       │
       ▼
Current User Dependency (get_current_user)
       │
       ▼
Authorization Decision (Resource Ownership)
       │
       ▼
Protected Service Execution
```

---

## 3. Endpoints Matrix & Security Controls

| Endpoint | Method | Authentication | Rate Limit | Ownership / Scope | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/api/v1/health` | GET | None (Public) | None | N/A | Infrastructure probe |
| `/api/v1/auth/register` | POST | None (Public) | 5 req/min | N/A | Account registration |
| `/api/v1/auth/login` | POST | None (Public) | 5 req/min | N/A | Authenticates & sets cookie |
| `/api/v1/auth/logout` | POST | Session-aware | None | Current Session | Clears session cookie |
| `/api/v1/users/me` | GET | Required | 60 req/min | Current User | Current user profile |
| `/api/v1/tts` | POST | Required | 10 req/min | Current User | Speech generation |
| `/api/v1/tts/{id}/audio` | GET | Required | 60 req/min | Generation Owner | RFC 7233 range stream |
| `/api/v1/tts/{id}/download` | GET | Required | 60 req/min | Generation Owner | Attachment download |
| `/api/v1/history` | GET | Required | 60 req/min | Current User | Scoped user history |
| `/api/v1/history/{id}` | GET/DELETE | Required | 60 req/min | Generation Owner | Record ownership |
| `/api/v1/favorites` | POST/GET | Required | 60 req/min | Current User | User-scoped favorites |
| `/api/v1/favorites/{id}` | DELETE | Required | 60 req/min | Favorite Owner | Bookmark ownership |
| `/api/v1/quantum/*` | POST | Required | 15 req/min | Current User | Quantum Intelligence APIs |

---

## 4. Dual Token Transport Strategy

To satisfy browser security standards while maintaining full compatibility with automated tests, Postman, and headless API clients, Bloop supports dual token extraction:

1. **HttpOnly Browser Cookie (Primary for Web):**
   - Cookie name: `access_token` (fallback: `bloop_session`)
   - `HttpOnly = True`: JavaScript cannot access or exfiltrate the token via XSS.
   - `Secure = True`: Enforced in production mode over HTTPS.
   - `SameSite = Lax` (local dev) or `SameSite = None` (production cross-origin Vercel + Render).
2. **Authorization Header (Fallback for CLI / Postman / Tests):**
   - `Authorization: Bearer <JWT>`

---

## 5. Standard Error Contract

Authentication failures adhere to the Bloop error contract:

```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Authentication required. Session token missing.",
    "details": {}
  }
}
```

Standard Authentication Error Codes:
- `AUTHENTICATION_REQUIRED` (HTTP 401): Missing session token.
- `INVALID_CREDENTIALS` (HTTP 401): Incorrect email or password (generic to prevent user enumeration).
- `TOKEN_EXPIRED` (HTTP 401): JWT expiration timestamp exceeded.
- `INVALID_TOKEN` (HTTP 401): Tampered signature or invalid claims.
- `ACCOUNT_INACTIVE` (HTTP 401): Account is deactivated (`is_active = false`).
- `ACCESS_DENIED` (HTTP 403): User lacks permission to access another user's resource.
