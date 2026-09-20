# Bloop Protected API & Authorization Boundary Specification

## 1. Overview

The Bloop platform employs a strict **zero-trust authorization boundary** across all core service modules. Authentication asserts the identity of the caller; authorization independently determines whether the authenticated identity owns or is permitted to manipulate the requested resource.

---

## 2. Resource Ownership Invariants

Every sensitive entity is permanently tied to an owning `user_id`:
- `SpeechGeneration.user_id`
- `Favorite.user_id`
- `QuantumExperiment.user_id`
- `UserPreference.user_id`

### Core Authorization Principle:
```text
current_user.id == resource.user_id
```

1. **Server-Authoritative Identity**: The backend resolves `current_user` solely from cryptographically validated JWT session tokens. Client-supplied `user_id` query parameters or body fields are never trusted for authorization decisions.
2. **Database Query Scoping**: Where practical, repository queries filter directly by `user_id` (e.g. `SELECT * FROM generations WHERE user_id = :current_user_id`).
3. **Cross-User Access Denial**: If User A queries or attempts to delete a resource belonging to User B, the server responds with **HTTP 403 Forbidden** (`ACCESS_DENIED` or `GENERATION_ACCESS_DENIED`).

---

## 3. Protected Resource Matrix

| Subsystem | Operation | Endpoint | Protected Status | Authorization Check |
| :--- | :--- | :--- | :--- | :--- |
| **TTS** | Speech Synthesis | `POST /api/v1/tts` | Protected | Authenticated User |
| **Audio** | Stream Audio | `GET /api/v1/tts/{id}/audio` | Protected | Generation Owner |
| **Audio** | Download Audio | `GET /api/v1/tts/{id}/download` | Protected | Generation Owner |
| **History** | List Generations | `GET /api/v1/history` | Protected | Scoped to Current User |
| **History** | Get Record | `GET /api/v1/history/{id}` | Protected | Generation Owner |
| **History** | Delete Record | `DELETE /api/v1/history/{id}` | Protected | Generation Owner |
| **Favorites** | Add Favorite | `POST /api/v1/favorites` | Protected | Generation Owner |
| **Favorites** | List Favorites | `GET /api/v1/favorites` | Protected | Scoped to Current User |
| **Favorites** | Remove Favorite | `DELETE /api/v1/favorites/{id}` | Protected | Favorite Owner |
| **Quantum** | Text / Emotion / Semantic | `POST /api/v1/quantum/*` | Protected | Authenticated User |
| **Quantum** | Circuit / Benchmark | `POST /api/v1/quantum/*` | Protected | Authenticated User |
| **Quantum** | History | `GET /api/v1/quantum/history` | Protected | Scoped to Current User |

---

## 4. Provider & Cost Isolation Guarantee

External providers (such as ElevenLabs text-to-speech) incur network and monetary costs. Bloop guarantees that:
- Unauthenticated requests are rejected at the FastAPI dependency layer before reaching provider synthesis.
- Rate limits (e.g. 10 req/min for TTS, 5 req/min for Auth, 15 req/min for Quantum) prevent quota exhaustion and brute-force abuse.
