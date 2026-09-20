# Bloop Relational Entity Relationships & ER Diagram

**Document Identifier:** BLOOP-DB-REL-007  
**Status:** Approved Technical Standard  
**Target Engine:** PostgreSQL 16 (Render Managed)  

---

## 1. Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o| USER_PREFERENCES : "has (1-to-1, CASCADE)"
    USERS ||--o{ SPEECH_GENERATIONS : "owns (1-to-many, SET NULL)"
    USERS ||--o{ FAVORITES : "saves (1-to-many, CASCADE)"
    USERS ||--o{ QUANTUM_EXPERIMENTS : "executes (1-to-many, SET NULL)"

    LANGUAGES ||--o{ VOICES : "classifies (1-to-many, CASCADE)"
    LANGUAGES ||--o{ USER_PREFERENCES : "preferred by (SET NULL)"

    SPEECH_GENERATIONS ||--o{ FAVORITES : "bookmarked in (1-to-many, CASCADE)"

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_superuser
        timestamp created_at
        timestamp updated_at
    }

    USER_PREFERENCES {
        int id PK
        int user_id FK,UK
        string default_language_code FK
        string default_voice_id
        string theme
        float audio_speed
        boolean auto_play
        timestamp created_at
        timestamp updated_at
    }

    LANGUAGES {
        string code PK
        string name
        string native_name
        boolean is_active
        timestamp created_at
    }

    VOICES {
        int id PK
        string voice_id UK
        string name
        string language_code FK
        string gender
        string accent
        string description
        string provider
        string preview_url
        boolean is_active
        boolean is_user_configured
        timestamp created_at
        timestamp updated_at
    }

    SPEECH_GENERATIONS {
        int id PK
        int user_id FK
        text text
        int char_count
        int word_count
        string language_code
        string voice_id
        string voice_name
        string status
        string audio_filename UK
        float duration_seconds
        int file_size_bytes
        string audio_format
        string provider
        string provider_request_id
        string error_code
        text error_message
        timestamp created_at
        timestamp updated_at
    }

    FAVORITES {
        int id PK
        int user_id FK
        int generation_id FK
        string label
        timestamp created_at
    }

    QUANTUM_EXPERIMENTS {
        int id PK
        int user_id FK
        string experiment_type
        string title
        text description
        string status
        json input_payload
        json results
        int qubit_count
        int circuit_depth
        float execution_time_ms
        string simulator
        string error_code
        timestamp created_at
        timestamp updated_at
    }
```

---

## 2. Foreign Key & Deletion Cascade Policies

| Source Table | Foreign Key Column | Target Table.Column | On Delete Action | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `user_preferences` | `user_id` | `users.id` | **CASCADE** | A preference record has no lifecycle outside its user owner. |
| `user_preferences` | `default_language_code`| `languages.code` | **SET NULL** | If a language code is disabled, retain the preference record with null. |
| `voices` | `language_code` | `languages.code` | **CASCADE** | Dynamic voices registered under a language depend on that language. |
| `speech_generations`| `user_id` | `users.id` | **SET NULL** | Retains anonymous generation history and audio metrics even if user deletes account. |
| `favorites` | `user_id` | `users.id` | **CASCADE** | If a user is deleted, all their bookmarks must be purged. |
| `favorites` | `generation_id` | `speech_generations.id` | **CASCADE** | If a generation is deleted from disk and DB, its favorite bookmarks are purged. |
| `quantum_experiments`| `user_id` | `users.id` | **SET NULL** | Scientific logs and benchmark telemetry are preserved anonymously. |

---

## 3. Ownership & Authorization Invariant

Bloop database relationships strictly enforce tenancy isolation:
1. **No Cross-User Queries:** Repositories filter records using `WHERE user_id = :authenticated_user_id`.
2. **Favoriting Authorization:** A user cannot favorite another user's generation unless explicitly made public.
3. **Compound Deletions:** Deleting a generation automatically triggers an atomic cascade delete of associated favorites.
