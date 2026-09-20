# ADR-018: User Profiles, Preferences, Speech History & Generation Management

## Status
Accepted

## Context
Following the implementation of the JWT authentication boundary (ADR-017) and speech synthesis delivery pipeline (ADR-016), Bloop required a robust, secure, production-grade management layer for user accounts, application preferences, and speech generation history.

Key design requirements:
1. **Separation of Concerns**: User identity (`User`) must remain strictly separated from personalization preferences (`UserPreference`).
2. **Safe Profile Updates**: Profile updates must never allow modifying immutable identifiers (`id`, `email`, `created_at`) or authentication credentials (`password`, `hashed_password`).
3. **Preference Independence**: User preferences indicate "what the user prefers" and must never bypass capability or authorization validation at synthesis time.
4. **Zero Hardcoded Voices**: No static voice catalogues or fake default voices may be introduced. Preferences must cleanly support `null` voice states.
5. **No Binary Blobs in PostgreSQL**: Database stores generation metadata and disk file references; binary media remains in ephemeral server storage.
6. **Strict Ownership Isolation**: Strong authorization boundary preventing Insecure Direct Object References (IDOR).
7. **Controlled History Exploration**: Pagination, search, language/status filtering, and an allowlist of sortable attributes to prevent arbitrary SQL injection or database performance degradation.

---

## Decisions

### 1. Dedicated Service-Layer Architecture
We created dedicated service domain modules (`backend/app/services/`):
* `UserService`: Handles user profile retrieval and validated mutations.
* `PreferenceService`: Handles preference retrieval, default initialization, and strict validation.
* `HistoryService`: Handles history pagination, multi-column search, filtering, and deletion.

All FastAPI routers in `backend/app/api/v1/endpoints/` were kept thin, delegating all domain logic to these services.

### 2. Explicit Pydantic Schemas for Profile & Preferences
* Introduced `UserProfileUpdateRequest` restricting profile modifications exclusively to `full_name`.
* Implemented `UserPreferenceUpdate` and `UserPreferenceResponse` validating theme choices (`dark`, `light`, `system`), playback speeds (`[0.5, 2.0]`), auto-play boolean, and language codes against registered locales.
* Maintained `null` as the valid default for unconfigured voices.

### 3. Server-Enforced Resource Ownership & IDOR Protection
* Ownership is derived exclusively from the authenticated session (`current_user.id`).
* Client-supplied `user_id` values in request bodies or query parameters are ignored.
* Cross-user access attempts to history details or deletion return HTTP 403 `FORBIDDEN`.

### 4. Controlled History Querying & Sorting Allowlist
* Querying supports search across `text` and `voice_name`, exact language filtering, and status filtering.
* Sorting is restricted to an allowlist: `created_at`, `duration_seconds`, `char_count`, and `word_count`. Arbitrary columns are disallowed.
* Pagination is bounded to `page >= 1` and `1 <= page_size <= 100`.

### 5. Physical Media Deletion Synchronization
* Deletion via `HistoryService.delete_generation` guarantees that both the database audit record and the temporary physical audio file on disk storage are deleted.

---

## Consequences

### Positive:
* Prevents privilege escalation and credential tampering via the profile endpoint.
* Enforces strict multi-tenant isolation with zero data leakage between users.
* Completely eliminates arbitrary column injection in history sorting.
* Keeps PostgreSQL database lightweight by storing media references rather than binary blobs.
* Preserves the Dynamic Voice Invariant with zero hardcoded voice identifiers.

### Negative / Trade-offs:
* Requires explicit service-to-service orchestration rather than simple direct ORM calls in route handlers.
