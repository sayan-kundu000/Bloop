# Bloop — Render Deployment Specification & Runbook

**Document Identifier:** BLOOP-DEPLOY-RENDER-006  
**Status:** Approved Deployment Guide  
**Target Platform:** Render Web Service (Python 3.12+) & Render Managed PostgreSQL 16  
**Authority:** Prompt 06 — Environment Configuration, Secrets Management & Profiles  

---

## 1. Executive Deployment Architecture

Bloop's backend API and relational persistence layer run entirely on **Render** (render.com):
- **Web Service (`bloop-backend`):** A containerized Python 3.12 web service running FastAPI under Uvicorn ASGI.
- **Managed Database (`bloop-postgres`):** A managed PostgreSQL 16 database instance communicating over Render's private internal network.
- **Declarative Infrastructure:** Defined in the root `render.yaml` blueprint with zero committed secrets.

```
                   GitHub Repository (main branch)
                                 │
                                 ▼
                     Render Blueprint Execution
                                 │
              ┌──────────────────┴──────────────────┐
              ▼                                     ▼
     bloop-postgres (DB)                   bloop-backend (Web)
    PostgreSQL 16 Managed                 FastAPI + Uvicorn ASGI
              │                                     │
              │  Internal Private Connection        │
              └────────────────►────────────────────┤
                                                    │
                                     Outbound HTTPS │
                                                    ▼
                                           ElevenLabs Cloud API
```

---

## 2. Declarative Blueprint (`render.yaml`)

The authoritative `render.yaml` declares services and references secrets dynamically:

```yaml
services:
  # Backend FastAPI Web Service
  - type: web
    name: bloop-backend
    runtime: python
    buildCommand: "pip install -r backend/requirements.txt && alembic upgrade head"
    startCommand: "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /api/v1/health
    envVars:
      - key: APP_ENV
        value: production
      - key: APP_DEBUG
        value: "false"
      - key: APP_NAME
        value: Bloop
      - key: APP_VERSION
        value: 0.1.0
      - key: API_V1_PREFIX
        value: /api/v1
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "1440"
      - key: DATABASE_URL
        fromDatabase:
          name: bloop-postgres
          property: connectionString
      - key: ELEVENLABS_API_KEY
        sync: false
      - key: CORS_ORIGINS
        value: "https://bloop.vercel.app"
      - key: AUDIO_STORAGE_PATH
        value: "backend/app/storage/audio"
      - key: LOG_LEVEL
        value: "INFO"
      - key: QUANTUM_ENABLED
        value: "true"

databases:
  # Managed PostgreSQL 16 Database
  - name: bloop-postgres
    databaseName: bloop_db
    user: bloop_user
    plan: free
```

---

## 3. Production Environment Variable Specification

The following variables must be configured in the Render Dashboard for `bloop-backend`:

| Variable | Secret? | Source | Description |
| :--- | :---: | :--- | :--- |
| `APP_ENV` | No | Static | Must be `production`. |
| `APP_DEBUG` | No | Static | Must be `false`. (Startup fails if `true`). |
| `APP_NAME` | No | Static | `Bloop` |
| `APP_VERSION` | No | Static | `0.1.0` |
| `API_V1_PREFIX` | No | Static | `/api/v1` |
| `DATABASE_URL` | **Yes** | `bloop-postgres` | PostgreSQL connection string with internal hostname. |
| `JWT_SECRET_KEY` | **Yes** | Render Auto-Gen | High-entropy secret key (min 32 chars) for JWT signing. |
| `JWT_ALGORITHM` | No | Static | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| No | Static | `1440` (24 hours) |
| `ELEVENLABS_API_KEY` | **Yes** | User Input | Live vendor API key from ElevenLabs console. |
| `ELEVENLABS_API_BASE` | No | Static | `https://api.elevenlabs.io/v1` |
| `CORS_ORIGINS` | No | User Input | Comma-separated Vercel domain (`https://bloop.vercel.app`). Wildcard `*` rejected. |
| `AUDIO_STORAGE_PATH` | No | Static | `backend/app/storage/audio` |
| `LOG_LEVEL` | No | Static | `INFO` |
| `QUANTUM_ENABLED` | No | Static | `true` |

---

## 4. Build, Migration & Execution Pipeline

1. **Build Command:**
   ```bash
   pip install -r backend/requirements.txt && alembic upgrade head
   ```
   *Installs frozen production dependencies and executes Alembic schema migrations against Render PostgreSQL before server boot.*

2. **Start Command:**
   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```
   *Binds to all network interfaces on the dynamically assigned `$PORT`.*

3. **Zero-Downtime Health Check Probe:**
   - **Path:** `/api/v1/health`
   - Render verifies that the service returns HTTP 200 OK before routing public traffic to the new instance.

---

## 5. Security & Fail-Fast Safeguards

During startup, `backend/app/core/config.py` runs validation:
- **Debug Protection:** If `APP_DEBUG=true` in production, container terminates immediately.
- **Weak Key Protection:** If `JWT_SECRET_KEY` is missing or matches dev defaults, startup is rejected.
- **Database Enforcement:** If `DATABASE_URL` is SQLite, startup is rejected.
- **CORS Protection:** If wildcard `*` is present in `CORS_ORIGINS`, startup is rejected.
- **Log Masking:** `SecretMaskingFilter` scrubs all passwords, JWT tokens, and ElevenLabs keys from Render runtime logs.
