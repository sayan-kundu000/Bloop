# Bloop Database Indexing & Query Performance Strategy

**Document Identifier:** BLOOP-DB-IDX-007  
**Status:** Approved Technical Standard  
**Target Engine:** PostgreSQL 16 (B-Tree Indexes)  

---

## 1. Indexing Philosophy

Bloop adheres to **access-pattern-driven indexing**. Indexes are created exclusively where query patterns justify index maintenance overhead. Unnecessary indexes degrade write throughput and waste buffer pool memory.

### Guiding Principles:
1. **Primary & Unique Constraints:** Automatically backed by B-tree indexes (`users.email`, `voices.voice_id`, `speech_generations.audio_filename`, `favorites.(user_id, generation_id)`).
2. **Foreign Key Acceleration:** Index all foreign key columns used in joins (`user_preferences.user_id`, `speech_generations.user_id`, `favorites.user_id`, `favorites.generation_id`).
3. **Composite Indexing for Time-Series Pagination:** Queries sorting by timestamp within a tenant/user scope are accelerated using composite B-tree indexes.

---

## 2. Complete Index Directory

| Table Name | Index Name | Indexed Columns | Type | Purpose |
| :--- | :--- | :--- | :---: | :--- |
| `users` | `ix_users_id` | `id` | B-Tree | Primary key lookup. |
| `users` | `ix_users_email` | `email` | Unique B-Tree | Fast credential lookup during login. |
| `user_preferences` | `ix_user_preferences_id` | `id` | B-Tree | Primary key lookup. |
| `user_preferences` | `ix_user_preferences_user_id` | `user_id` | Unique B-Tree | Fast 1-to-1 profile hydration. |
| `languages` | `ix_languages_code` | `code` | B-Tree | Primary key lookup. |
| `voices` | `ix_voices_id` | `id` | B-Tree | Primary key lookup. |
| `voices` | `ix_voices_voice_id` | `voice_id` | Unique B-Tree | Fast lookup by provider voice string. |
| `voices` | `ix_voices_language_code` | `language_code` | B-Tree | Filter voice catalog by language code. |
| `speech_generations`| `ix_speech_generations_id` | `id` | B-Tree | Primary key lookup. |
| `speech_generations`| `ix_speech_generations_audio_filename` | `audio_filename` | Unique B-Tree | Streaming endpoint lookup by file token. |
| `speech_generations`| `ix_speech_generations_user_id` | `user_id` | B-Tree | Filter generations by owning user. |
| `speech_generations`| `ix_speech_generations_status` | `status` | B-Tree | Filter by lifecycle status. |
| `speech_generations`| `ix_speech_generations_created_at` | `created_at` | B-Tree | Global time-series sorting. |
| `speech_generations`| **`ix_speech_generations_user_created`** | **`(user_id, created_at)`** | **Composite B-Tree** | **High-performance paginated history queries.** |
| `favorites` | `ix_favorites_id` | `id` | B-Tree | Primary key lookup. |
| `favorites` | `ix_favorites_user_id` | `user_id` | B-Tree | Retrieve all bookmarks for a user. |
| `favorites` | `ix_favorites_generation_id` | `generation_id` | B-Tree | Cascade verification on generation delete. |
| `favorites` | `uq_user_generation_favorite` | `(user_id, generation_id)` | Unique B-Tree | Prevent duplicate bookmarking. |
| `quantum_experiments`| `ix_quantum_experiments_id` | `id` | B-Tree | Primary key lookup. |
| `quantum_experiments`| `ix_quantum_experiments_experiment_type` | `experiment_type`| B-Tree | Filter by circuit/emotion/semantic type. |
| `quantum_experiments`| `ix_quantum_experiments_status` | `status` | B-Tree | Filter by experiment state. |
| `quantum_experiments`| `ix_quantum_experiments_user_id` | `user_id` | B-Tree | Filter by executing user. |
| `quantum_experiments`| `ix_quantum_experiments_created_at` | `created_at` | B-Tree | Global chronology. |
| `quantum_experiments`| **`ix_quantum_experiments_user_created`** | **`(user_id, created_at)`** | **Composite B-Tree** | **User-scoped experiment history pagination.** |

---

## 3. Query Optimization: Speech History Pagination

The most critical database read path in Bloop is retrieving a user's speech generation history:

```sql
SELECT id, text, char_count, word_count, voice_id, audio_filename, duration_seconds, status, created_at
FROM speech_generations
WHERE user_id = :user_id
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;
```

### Without Composite Index:
PostgreSQL performs an index scan on `user_id`, collects matching pointers, and executes an in-memory or on-disk sort over `created_at`. As a user accumulates hundreds of generations, query latency increases linearly.

### With Composite Index `(user_id, created_at)`:
PostgreSQL performs an **Index Scan Backward** directly traversing the leaf pages of the composite index in pre-sorted order. The database eliminates the sorting step entirely ($O(1)$ startup cost), reading exactly `LIMIT` index rows.
