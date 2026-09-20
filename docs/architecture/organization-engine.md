# Content Organization Engine Architecture

## 1. Scope & Objective

The Content Organization Engine in Bloop organizes user-generated speech generations and quantum synthesis outputs without unnecessary complexity such as nested folder trees, tag databases, or external search clusters (Elasticsearch/Redis).

```text
User Workspace
     ├── Synthesis (Speech & Quantum)
     ▼
Speech Generation Metadata (Canonical Entity)
     ├── Speech History Engine
     │     ├── ILIKE Search (text, voice_name)
     │     ├── Language & Status Filters
     │     ├── Date Range Bounding
     │     └── Controlled Sort Allowlist
     └── Favorites & Saved Reference Engine
           ├── Bookmark & Custom Labeling
           ├── Instant Access Quick Filter
           └── Dedicated Saved Generations View
```

---

## 2. Organization Data Structure

| Feature | Entity Layer | Database Mechanism | Behavioral Characteristics |
| :--- | :--- | :--- | :--- |
| **History Trail** | `SpeechGeneration` | Primary table with index on `(user_id, created_at)` | Chronological audit log of all completed and failed requests. |
| **Favorites / Saved** | `Favorite` | Secondary join table with unique constraint `(user_id, generation_id)` | Lightweight pointer referencing primary speech generation. |
| **Filtering** | Query Engine | Relational `WHERE` predicates + `LEFT OUTER JOIN` | Dynamically filters by language, status, favorite state, or date. |
| **Search** | Query Engine | Parameterized SQL `ILIKE` across text and voice name | Case-insensitive substring matching without SQL injection risks. |

---

## 3. Performance & Resource Boundaries

1. **Bounded Page Sizes**: Page size is clamped on the server (`1 <= page_size <= 100`) to prevent memory exhaustion attacks.
2. **Deterministic Tie-Breaking**: All sort queries append `SpeechGeneration.id DESC` to ensure stable pagination even when records share identical timestamps.
3. **No Database Blobs**: Audio files reside exclusively on ephemeral server disk storage; the database stores only lightweight metadata references (`audio_filename`, `file_size_bytes`, `duration_seconds`).
