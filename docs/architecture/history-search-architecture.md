# History Search & Filtering Architecture

## 1. Overview & Query Pipeline

The Bloop History Search and Filtering Engine provides high-performance, bounded, relational filtering directly within the authenticated user's data boundary.

```text
Authenticated User
       │
       ▼
Base Ownership Scope: WHERE speech_generations.user_id = :user_id
       │
       ├── Optional Keyword Search: (text ILIKE :q OR voice_name ILIKE :q)
       ├── Optional Language Filter: language_code = :lang
       ├── Optional Status Filter: status = :status
       ├── Optional Bookmark Filter: favorite IS [NOT] NULL
       └── Optional Date Range: created_at >= :from AND created_at <= :to
       │
       ▼
Controlled Sort Allowlist + Stable Tie-breaker: ORDER BY :sort_column :order, id DESC
       │
       ▼
Bounded Pagination: LIMIT :safe_page_size OFFSET :safe_offset
       │
       ▼
PostgreSQL Execution
```

---

## 2. Elimination of N+1 Queries

In prior iterations, retrieving $N$ history records incurred $N$ secondary queries to check whether each item was favorited by the requesting user.

Prompt 16 resolves this by executing a relational `LEFT OUTER JOIN` between `speech_generations` and `favorites` matching on `(Favorite.generation_id == SpeechGeneration.id) & (Favorite.user_id == user_id)`:

```sql
SELECT
    speech_generations.id,
    speech_generations.text,
    speech_generations.voice_name,
    speech_generations.language_code,
    speech_generations.status,
    speech_generations.duration_seconds,
    speech_generations.char_count,
    speech_generations.word_count,
    speech_generations.audio_filename,
    speech_generations.created_at,
    favorites.id AS favorite_id
FROM speech_generations
LEFT OUTER JOIN favorites
    ON favorites.generation_id = speech_generations.id
    AND favorites.user_id = :user_id
WHERE speech_generations.user_id = :user_id
  AND (favorites.id IS NOT NULL) -- when favorite=true
ORDER BY speech_generations.created_at DESC, speech_generations.id DESC
LIMIT :page_size OFFSET :offset;
```

This ensures:
1. Exactly **1 database query** for items, plus **1 count query** for pagination.
2. `is_favorite` (`favorite_id IS NOT NULL`) is resolved directly from the result set.
3. Zero secondary round-trips to the database regardless of page size.

---

## 3. Date Range Handling

Date range queries accept ISO 8601 strings:
- `created_after`: Lower bound timestamp (inclusive).
- `created_before`: Upper bound timestamp (inclusive).

### Validation Invariant:
If both `created_after` and `created_before` are provided, the service layer verifies that:
$$\text{created\_after} \le \text{created\_before}$$
Violations immediately reject the request with HTTP 422 `VALIDATION_ERROR` before touching the database.
