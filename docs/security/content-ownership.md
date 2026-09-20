# Content Ownership & Anti-IDOR Security

## 1. Threat Model & Security Guarantees

In multi-tenant AI applications, speech text and audio outputs represent sensitive, private user data. The Bloop platform enforces strict multi-tenant data isolation and Insecure Direct Object Reference (IDOR) prevention.

```text
HTTP Request
     │
     ▼
[JWT Session Middleware]
     │
     ▼
Authenticated User (current_user.id)
     │
     ├── 1. Client user_id parameter NEVER trusted
     │      (All queries strictly bind to current_user.id)
     │
     ├── 2. Scoped Database Predicates
     │      (WHERE user_id = current_user.id)
     │
     └── 3. Service Layer Ownership Verification
            (if record.user_id != current_user.id: raise 403 FORBIDDEN)
```

---

## 2. Attack Vectors & Defenses

### Attack 1: User A Bookmarks User B's Speech Generation
- **Vector**: User A sends `POST /api/v1/favorites {"generation_id": <user_b_gen_id>}`.
- **Defense**: `FavoriteService.add_favorite` retrieves the target generation and verifies `gen.user_id == user_id`. If they differ, the request is immediately aborted with HTTP 403 `FORBIDDEN`.

### Attack 2: User A Deletes User B's Favorite
- **Vector**: User A discovers or guesses a favorite ID and sends `DELETE /api/v1/favorites/<user_b_fav_id>`.
- **Defense**: `FavoriteService.remove_favorite` inspects the favorite record and checks `fav.user_id == current_user.id`. Unauthorized attempts fail with HTTP 403 `FORBIDDEN`.

### Attack 3: User A Discovers User B's Speech via History Search
- **Vector**: User A queries `GET /api/v1/history?search=<term>` expecting cross-user matching.
- **Defense**: The search filter is combined with `SpeechGeneration.user_id == current_user.id` at the database query level:
  ```sql
  WHERE speech_generations.user_id = :current_user_id
    AND (text ILIKE :search OR voice_name ILIKE :search)
  ```
  PostgreSQL never evaluates or returns records belonging to other users.

### Attack 4: SQL Injection via Search or Filter Parameters
- **Vector**: Malicious SQL fragments supplied via `search` or `sort_by`.
- **Defense**:
  - `search` is parameterized via SQLAlchemy's `.ilike(f"%{clean_search}%")` binding.
  - `sort_by` is validated against an explicit server-side allowlist (`sort_column_map`), preventing arbitrary column injection.
