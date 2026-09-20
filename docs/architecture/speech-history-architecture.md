# Speech Generation History Architecture

## 1. Overview & Data Flow

Every successful TTS generation in Bloop produces an immutable domain record in PostgreSQL with metadata, metrics, and references to temporary audio delivery assets:

```text
POST /api/v1/tts
       │
       ▼
[Authentication & Ownership] ─── Bind current_user.id
       │
       ▼
[Validation Engine] ─────────── Text boundaries & capabilities
       │
       ▼
[ElevenLabsProvider] ────────── Audio synthesis
       │
       ▼
[AudioProcessor & Delivery] ─── Validate bytes & store {uuid}.mp3
       │
       ▼
[SpeechGeneration Entity] ───── Persist metadata in PostgreSQL
       │
       ▼
[History API Queries] ───────── Paginated, filtered, sorted inspection
```

---

## 2. Privacy-Aware History Design (Prompt 15 §14-15)

* **No Binary Audio in PostgreSQL**: Large binary audio files are kept strictly on server temporary storage with automatic retention pruning. PostgreSQL stores only metadata and safe filename references.
* **Minimal Data Retention**: Generation records store only the necessary text, language code, voice reference, metrics (characters, words, duration, file size), provider ID, and timestamps.
* **No Secret or Header Logging**: Authentication headers, client IP addresses, JWT tokens, and provider credentials are never recorded in history models or logs.
* **Strict Deletion Semantics**: When a user deletes a speech generation (`DELETE /api/v1/history/{id}`), the physical audio file is immediately deleted from disk storage and the database row is deleted transactionally.

---

## 3. Querying, Filtering, Search & Sorting Allowlist

The History repository and service layer implement strict server-side bounds and allowlists:

### Pagination
* `page`: 1-indexed (minimum: 1).
* `page_size`: Bounded between 1 and 100 (default: 20).
* Prevents unbounded `SELECT *` queries.

### Search
* Multi-column case-insensitive search (`ILIKE`) matching across synthesized `text` and `voice_name`.

### Filtering
* `language`: Strict exact match against BCP-47 locale code (e.g. `en-US`).
* `status`: Strict allowlist filter (`completed`, `failed`, `pending`, `processing`).

### Sorting Allowlist (Prompt 15 §24)
Arbitrary SQL column names are strictly rejected. The system accepts only an allowlisted set of indexed attributes:
* `created_at` (default)
* `duration_seconds`
* `char_count`
* `word_count`
With direction: `desc` (default) or `asc`.
