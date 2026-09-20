# ADR-017: Authentication, JWT Sessions, Password Security, and Protected API Architecture

## Status
Accepted

## Context
Bloop requires a secure, intermediate-level identity and access boundary separating the React frontend on Vercel from the FastAPI backend on Render. As established in the system design, this identity boundary protects:
- Users & Personal Profiles (`/api/v1/users/me`)
- Speech Generations (`POST /api/v1/tts`)
- Audio Streaming & Downloads (`/api/v1/tts/{id}/audio`, `/api/v1/tts/{id}/download`)
- Audio History (`/api/v1/history`)
- Favorites (`/api/v1/favorites`)
- Quantum Intelligence Experiments (`/api/v1/quantum/*`)

Key architectural requirements include:
1. **Separation of Authentication and Authorization**: Authenticating "Who are you?" must remain separate from authorizing "Are you allowed to access this resource?".
2. **Credential & Secret Protection**: Passwords must never be stored in plaintext. JWT secrets and third-party API keys (ElevenLabs) must remain strictly on the backend.
3. **Browser Security Contract**: Client-side JavaScript in React must not have access to authentication tokens, mitigating XSS exfiltration risks.
4. **Intermediate Scope Integrity**: Avoid over-engineering with distributed microservices, Redis clusters, or external OAuth brokers before the platform requires them.

## Decision

1. **Password Security**:
   - Persist passwords strictly as salted, one-way hashes using **bcrypt**.
   - Enforce pre-commit validation: required, non-empty, minimum 6 characters, maximum 100 characters.
   - Use constant-time comparison (`bcrypt.checkpw`) and generic error responses (`INVALID_CREDENTIALS`, HTTP 401) to eliminate user enumeration and timing side-channels.

2. **JWT Session Architecture**:
   - Issue cryptographically signed JSON Web Tokens using `HS256` with strict algorithm pinning.
   - Minimal claims payload: `sub` (canonical integer User ID string), `iat` (UTC timestamp), `exp` (UTC expiration).
   - Secret key provided via Twelve-Factor environment configuration (`JWT_SECRET_KEY`) with production safeguards.

3. **Secure Cookie Session Transport**:
   - Deliver JWT tokens to browsers via secure `HttpOnly` session cookies (`access_token`).
   - Configure `Secure=True` in production mode over HTTPS.
   - Set `SameSite=None` in production to support credentialed cross-origin communications between Vercel and Render, and `SameSite=Lax` for local development.
   - Retain `Authorization: Bearer <token>` extraction fallback for automated test suites, Postman collections, and external tools.

4. **FastAPI Authorization Boundary & Resource Ownership**:
   - Implement `get_current_user` dependency resolving token claims and verifying active account status (`is_active = True`).
   - Enforce resource ownership checks directly in API route handlers and repository queries (`current_user.id == resource.user_id`).
   - Cross-user access attempts strictly return **HTTP 403 Forbidden** (`ACCESS_DENIED` or `GENERATION_ACCESS_DENIED`).

5. **Scope Control & Intentional Non-Requirements**:
   - **No Redis / Distributed Caching**: Stateless JWT verification eliminates the operational overhead of managing distributed session clusters for this intermediate stage.
   - **No OAuth / Social Login**: Bloop's core identity model relies directly on email and password credentials, keeping deployment on Render and Vercel lightweight and self-contained.
   - **No Complex RBAC**: Single-tenant user ownership provides the required security boundary without unnecessary role-hierarchy complexity.

## Consequences

### Positive
- **Robust Security Posture**: Complete XSS mitigation via HttpOnly cookies and brute-force mitigation via rate-limiting.
- **Provider & Cost Isolation**: Unauthenticated callers are rejected at the FastAPI boundary before invoking ElevenLabs or Quantum pipelines.
- **Deployment Simplicity**: Zero external state dependencies (no Redis, Kafka, or OAuth apps required on Render).
- **Comprehensive Testability**: Full coverage across unit, security, and integration layers.

### Trade-offs & Mitigations
- *Stateless JWT Revocation*: Immediate server-side token revocation prior to natural expiration requires short-lived tokens or server-side blocklists.
  - *Mitigation*: Session expiration is centrally configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` (defaults to short durations in production), and account deactivation (`is_active = False`) is checked on every authenticated request.
