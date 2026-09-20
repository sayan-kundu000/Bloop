# ADR-013: PostgreSQL 16, SQLAlchemy 2.x Architecture & Alembic Migrations

## Status
**Accepted**

## Context
Bloop is an intermediate-level AI speech synthesis and quantum intelligence experimentation platform. The platform requires durable relational persistence for user accounts, credentials, personalized settings, language catalogs, dynamic voice registries, speech generation requests, favorites, and quantum experiment logs.

We need a unified, typed, migration-governed database architecture that deploys reliably to Render Managed PostgreSQL 16, runs tests deterministically, preserves complete isolation between Speech synthesis and Quantum computation, and avoids unmaintainable database anti-patterns (such as storing large binary audio blobs in database rows).

## Decision
Adopt a centralized, production-grade relational database architecture based on **PostgreSQL 16**, **SQLAlchemy 2.x**, and **Alembic**:

### 1. Engine Selection: PostgreSQL 16 First
- **Canonical Production Database:** Render Managed PostgreSQL 16 is the authoritative production engine.
- **Local / Test Fallback:** SQLite is permitted strictly for zero-setup local development and isolated unit testing. The schema is engineered exclusively for PostgreSQL-compliant standards without dialect hacks.

### 2. Modern SQLAlchemy 2.x Declarative Layer
- Models inherit from a unified `DeclarativeBase` (`Base`) with standardized constraint naming conventions.
- All model attributes use modern SQLAlchemy 2.x `Mapped[...]` and `mapped_column(...)` type annotations.
- Queries across the repository layer use 2.0 `select()` statements rather than legacy 1.x `Query` chaining.

### 3. Alembic as Schema Authority
- Schema migrations are governed strictly by Alembic revisions located in `backend/alembic/versions/`.
- Manual production DDL alterations are strictly prohibited.
- Migrations execute atomically during Render build steps (`pip install && alembic upgrade head`) prior to server boot.

### 4. Zero Audio Binaries in Database
- Audio waveforms and synthesized MP3 files are written exclusively to filesystem storage (`backend/app/storage/audio/`).
- PostgreSQL stores only lightweight references, formats, duration metrics, file sizes, and status keys.

### 5. Zero Actual Voices Pre-Seeded
- In strict adherence to platform specifications, no actual ElevenLabs voice records, fake voice IDs, or hardcoded voice names are seeded into migration scripts or production databases.
- The `Voice` model provides a dynamic registry architecture populated at runtime by the user.

### 6. Timezone-Aware UTC Timestamp Policy
- All datetime columns (`created_at`, `updated_at`) use `DateTime(timezone=True)` (`TIMESTAMPTZ` in PostgreSQL).
- Default generators explicitly use `datetime.now(timezone.utc)`.

### 7. Clean Repository & Request-Scoped Sessions
- Routes acquire database sessions through the FastAPI `get_db` generator.
- Any unhandled exception triggers an automatic `db.rollback()` before returning the connection to the pool.
- Repositories encapsulate query logic, ownership filters (`WHERE user_id = :user_id`), and pagination (`LIMIT/OFFSET`).

### 8. Access-Pattern-Driven Indexing
- Composite B-tree indexes (`user_id, created_at`) are created on `speech_generations` and `quantum_experiments` to eliminate in-memory sorting during paginated history lookups.

## Alternatives Considered
1. **Storing MP3 Audio as PostgreSQL Bytea / BLOBs:** Rejected due to severe page bloat, write amplification, and degradation of buffer pool cache efficiency.
2. **Microservices / Multi-Database Architecture:** Rejected because splitting Auth, TTS, and Quantum into separate databases adds distributed transaction overhead (2PC/Sagas) inappropriate for an intermediate-level platform.
3. **NoSQL / Document Store (MongoDB):** Rejected because Bloop's core data model is intrinsically relational (users -> generations -> favorites).
4. **Redis / Kafka / Elasticsearch:** Excluded as unnecessary architectural overhead for the current phase; PostgreSQL provides sufficient performance, indexing, and JSON querying.

## Consequences

### Positive
- **Rock-Solid Data Integrity:** Foreign key cascades, unique constraints, and composite indexes protect data consistency at the database level.
- **Zero Secret Leakage:** Database passwords are masked in settings representations and never logged.
- **Fail-Fast Test Safety:** Automated test suites are mathematically blocked from connecting to production databases.
- **Deployment-Ready:** Seamless integration with Render's build and release pipelines.

### Trade-offs
- Requires discipline to generate and review an Alembic migration whenever an entity model is updated.
