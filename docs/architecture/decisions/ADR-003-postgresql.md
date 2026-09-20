# ADR-003: PostgreSQL Selection with SQLAlchemy 2.0 and Alembic

## Status
**Accepted**

## Context
Bloop persists structured relational data: user accounts, hashed credentials, user preferences, dynamic voice records, ISO languages, speech generation history, favorites/bookmarks, and quantum experiment logs.

Alternatives considered:
- **NoSQL Document Store (MongoDB):** Flexible document schema, but lacks ACID guarantees for multi-tenant relations and foreign-key isolation.
- **SQLite:** Lightweight and zero-configuration, but lacks concurrency for production multi-user cloud workloads (write locks).
- **PostgreSQL:** Industry-standard ACID-compliant relational database with rich indexing, JSONB support, and managed availability on Render.

## Decision
Adopt **PostgreSQL 16** as the authoritative primary database for production, managed via **SQLAlchemy 2.0 ORM** and **Alembic** for automated schema migrations. SQLite is retained strictly for ephemeral in-memory unit testing in CI environments.

## Rationale
1. **Relational Integrity & Foreign Keys:** Enforces strict multi-tenant ownership boundaries. Deleting a user can cascade cleanly or be verified across generations, favorites, and preferences.
2. **ACID Transactions:** Ensures atomicity when recording generation history and updating user stats or favorites.
3. **Managed Cloud Availability:** Render provides automated, managed PostgreSQL instances with one-click connection string injection (`DATABASE_URL`).
4. **Structured Migration Path:** Alembic provides reproducible schema versioning, avoiding manual production DDL executions (`alembic upgrade head`).
5. **SQLAlchemy 2.0 Type Safety:** Utilizes modern 2.0 typed `Mapped[...]` attributes and async-compatible query syntax (`select(Model).where(...)`).

## Consequences
### Positive
- Robust relational integrity and strict foreign-key constraints preventing orphan records.
- Deterministic schema migrations through source-controlled Alembic scripts.
- Support for complex search queries, filtering, and pagination over generation history.

### Negative / Trade-offs
- Requires running a PostgreSQL container or local service for full integration development (or using SQLite fallback locally).
- Connection pooling must be configured appropriately for async FastAPI workers to avoid connection exhaustion on Render free/starter tiers.
