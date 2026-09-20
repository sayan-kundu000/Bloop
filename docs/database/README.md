# Bloop — Relational Database Specification & Migration Guide

Bloop uses **PostgreSQL 16** for production persistence on Render and supports **SQLite 3** for local developer testing.

## Relational Entity Schema

For the complete schema specification, see [Database Architecture Specification](../architecture/database-architecture.md).

```
users (1) ──────────< (many) speech_generations
users (1) ──────────< (many) favorites
users (1) ─────────── (1)    user_preferences
users (1) ──────────< (many) quantum_experiments

languages (1) ──────< (many) voices
languages (1) ──────< (many) speech_generations
voices (1) ─────────< (many) speech_generations
```

## Migration Workflow (Alembic)

All schema changes are versioned using Alembic migration scripts:

```bash
# Generate a new migration after modifying models
alembic revision --autogenerate -m "Add new column or table"

# Apply pending migrations to the active database
alembic upgrade head

# Roll back the most recent migration
alembic downgrade -1
```

> [!IMPORTANT]
> In production, Render automatically executes `alembic upgrade head` before booting Uvicorn, guaranteeing schema synchronization before the container serves traffic.
