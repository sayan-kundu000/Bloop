# Bloop — Automation Scripts Directory

This directory contains cross-platform automation scripts for local development, database operations, and deployment verification:

```
scripts/
├── development/     # Local setup and full-stack launch scripts (dev.sh, dev.ps1)
├── database/        # Alembic schema migration helpers (migrate.sh, migrate.ps1)
└── deployment/      # Uptime and health check verification probes (check-health.sh, check-health.ps1)
```

## Quick Commands:

### Launch Local Full-Stack Environment:
- **Windows:** `.\scripts\development\dev.ps1`
- **Linux / macOS:** `./scripts/development/dev.sh`

### Run Database Migrations:
- **Windows:** `.\scripts\database\migrate.ps1`
- **Linux / macOS:** `./scripts/database/migrate.sh`

### Check Backend Health:
- **Windows:** `.\scripts\deployment\check-health.ps1 http://localhost:8000`
- **Linux / macOS:** `./scripts/deployment/check-health.sh http://localhost:8000`
