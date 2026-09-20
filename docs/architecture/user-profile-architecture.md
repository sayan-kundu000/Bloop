# User Profile Architecture

## 1. Overview

The User Profile subsystem establishes the domain boundaries, identity representations, and safe mutation rules for authenticated Bloop users. It operates directly on top of the authentication and session infrastructure established in Prompt 14, reusing the canonical `User` entity while isolating sensitive credentials from client exposure.

```text
                               ┌───────────────────────────────────┐
                               │       Client Authenticated        │
                               │   (Cookie or Bearer Session)      │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │           UserService             │
                               │   - Extract User via get_me       │
                               │   - Populate UserPreference       │
                               │   - Sanitize Profile Updates      │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │       UserRepository (SQL)        │
                               │   - Safe update of full_name      │
                               │   - Never touch hashed_password   │
                               │   - Never touch email or roles    │
                               └─────────────────┬─────────────────┘
                                                 │
                                                 ▼
                               ┌───────────────────────────────────┐
                               │      Safe UserDetailResponse      │
                               │   (Excludes hashes, JWTs, keys)   │
                               └───────────────────────────────────┘
```

---

## 2. Core Entities & Separation

The user domain is partitioned into two distinct database entities:
1. **`User`** (`backend/app/models/user.py`):
   - Immutable identity attributes: `id` (integer primary key), `email` (unique identifier), `created_at` (audit timestamp).
   - Authentication credentials: `hashed_password` (Bcrypt adaptive salted hash). Never exposed in API responses.
   - Authorization metadata: `is_active` (boolean status), `is_superuser` (privilege flag).
   - Mutable display attribute: `full_name` (optional display name, max 100 characters).
2. **`UserPreference`** (`backend/app/models/user_preference.py`):
   - Personalization settings: `theme` (dark/light/system), `audio_speed` (0.5x to 2.0x), `auto_play` (boolean toggle).
   - Synthesis defaults: `default_language_code` (e.g. `en-US`), `default_voice_id` (dynamic voice reference or `null`).

---

## 3. Safe Profile Update Policy (Prompt 15 §8)

Profile updates submitted via `PATCH /api/v1/users/me` strictly enforce the following security invariants:
* **Authentication Requirement**: Requests must provide a valid session cookie or Bearer token.
* **Whitelisted Attributes Only**: Only `full_name` can be modified.
* **Immutable Identifiers Protected**: Attempts to mutate `id`, `email`, `is_superuser`, `is_active`, or `created_at` are rejected or excluded.
* **Credential Isolation**: Passwords cannot be altered via the profile endpoint.
* **Data Normalization**: Incoming text is whitespace-stripped and bounded to a maximum of 100 characters. Empty strings are normalized to `null`.
* **Transactional Integrity**: Updates are executed within a single SQLAlchemy transaction and verified before returning.

---

## 4. API Schemas & Data Protection

| Field | Exposed in Profile Response? | Modifiable via `PATCH /me`? | Description |
|---|---|---|---|
| `id` | Yes (Safe identifier) | No (Immutable) | Unique integer user ID. |
| `email` | Yes | No (Requires verified flow) | Primary account email. |
| `full_name` | Yes | Yes (1-100 chars) | Display name. |
| `hashed_password` | **NO (Never)** | **NO** | Bcrypt hash. Completely omitted from schemas. |
| `is_active` | Yes | No | Account status flag. |
| `is_superuser` | Yes | No | Administrative privilege flag. |
| `created_at` | Yes | No (Immutable) | Account registration timestamp. |
| `preference` | Yes | Through `/me/preferences` | Nested personalization settings. |
