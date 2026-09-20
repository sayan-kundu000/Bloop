# ADR-019: Favorites, Saved Generations & Content Organization Engine

## Status
Accepted

## Context
In Prompt 15, Bloop established user profiles, preferences, speech generation metadata, and baseline history retrieval. However, users needed a way to bookmark high-priority speech outputs (favorites), filter records by bookmark status, search through synthesized text and voice names, restrict results by date ranges, and organize content without introducing heavy external infrastructure (such as Elasticsearch, Redis, or document databases).

Furthermore, previous history listings suffered from an N+1 query issue where the favorite state of each history item was queried sequentially in a loop.

## Decisions

1. **Reference Model for Favorites**:
   - `Favorite` is modeled as a lightweight reference table linking `users.id` and `speech_generations.id`.
   - The speech text, audio parameters, duration, and disk storage references remain exclusively in `speech_generations`.
   - A database unique constraint `uq_user_generation_favorite(user_id, generation_id)` guarantees duplicate prevention transactionally.

2. **Cascade Delete Integrity**:
   - Deleting a `SpeechGeneration` record cascades (`ondelete="CASCADE"`) to delete associated `Favorite` rows automatically, eliminating orphaned bookmarks.
   - Deleting a `Favorite` row deletes only the bookmark reference, leaving the underlying `SpeechGeneration` and its physical audio file on disk completely intact.

3. **Elimination of N+1 Queries via Left Outer Join**:
   - `SpeechGenerationRepository.list_by_user` performs a `LEFT OUTER JOIN` on `Favorite` within the requesting user's boundary.
   - Both the generation and its `favorite_id` are returned in a single SQL query, reducing query count from $O(N)$ to $O(1)$.

4. **Multi-Factor Filtering & Search**:
   - Case-insensitive parameterized ILIKE search over `text` and `voice_name`.
   - Exact matching for `language_code` and `status`.
   - Optional `favorite=true/false` filtering directly resolved from the outer join.
   - ISO 8601 date range filtering with service-layer validation ensuring $\text{created\_after} \le \text{created\_before}$.

5. **Sort Allowlist & Stable Pagination**:
   - Sort columns restricted to: `created_at`, `duration_seconds`, `char_count`, `word_count`.
   - Secondary tie-breaker `id DESC` added to prevent pagination drift across records with identical timestamps.

6. **Frontend State Synchronization**:
   - Search query, filters, sort order, and page number are bidirectionally synchronized with browser URL search parameters (`useSearchParams`), enabling shareable URLs and seamless browser back/forward navigation.

7. **Dynamic Voice Invariant Maintained**:
   - Zero hardcoded actual or fake ElevenLabs voices or voice IDs added. Empty voice catalogs remain fully supported.

## Consequences
- **Positive**:
  - High query efficiency with zero N+1 queries.
  - Strict anti-IDOR security preventing cross-user bookmarking, deletion, or viewing.
  - Fast, responsive frontend search and filter UX with URL persistence.
  - Clean separation of concerns between Repositories, Services, and thin API controllers.
- **Negative / Trade-offs**:
  - Substring search (`%search%`) uses ILIKE, which is optimal for thousands of user records but does not provide fuzzy ranking (sufficient for intermediate-level scope).
