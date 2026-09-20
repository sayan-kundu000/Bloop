# ADR-003: Selection of PostgreSQL for Production Relational Persistence

## Status
**Accepted**

## Context
Bloop requires persistent storage for user credentials, user preferences, dynamic voice catalogues, ISO language locales, speech generation history, bookmarked favorites, and quantum experiment execution logs. The storage engine must provide strong ACID transaction guarantees, multi-tenant relational integrity, robust indexing for multi-parametric filtering, and seamless deployment on cloud PaaS providers (Render).

## Decision
Adopt **PostgreSQL 16** as the authoritative production database. Support **SQLite 3** strictly as an ephemeral, zero-configuration fallback for automated unit testing in CI environments.

## Alternatives Considered
1. **MongoDB / NoSQL Document Databases:** Offers flexible schemas, but lacks strict foreign-key referential integrity, making multi-tenant user isolation and cascade deletions error-prone.
2. **MySQL / MariaDB:** Capable relational database, but offers less sophisticated JSONB query operators and is less natively integrated with Render's automated one-click managed database infrastructure compared to PostgreSQL.
3. **SQLite in Production:** Zero cost and zero configuration, but suffers from file-level write locking, concurrency bottlenecks under multi-user loads, lack of native connection pooling, and data loss risks on ephemeral container platforms like Render.

## Consequences

### Positive
- **Referential Integrity:** Mandatory foreign-key constraints ensure orphaned generations or favorites cannot exist if a user account is deleted.
- **Advanced Querying & Indexing:** B-tree and composite indexes ensure sub-50ms query times across paginated speech history, multi-parametric filters (language, voice, date), and text search.
- **Render PaaS Integration:** Render provides automated, managed PostgreSQL instances with automated backups, connection pooling, TLS 1.3, and automatic `DATABASE_URL` environment binding.
- **JSONB Capabilities:** Structured JSONB columns allow flexible metadata storage for dynamic voice attributes and quantum circuit metrics without breaking relational schemas.

### Negative / Trade-offs
- **Infrastructure Requirement:** Requires a running PostgreSQL instance for full local integration testing (mitigated by environment-driven connection string fallback to SQLite for quick local unit test runs).
- **Connection Management:** Connection pools must be sized appropriately to avoid exhausting connection limits on Render free/starter tiers.
