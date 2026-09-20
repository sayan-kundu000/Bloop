# Backend Structured Logging & Observability

## 1. Overview

Bloop implements a structured, security-sanitizing logging pipeline in [`backend/app/core/logging.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/core/logging.py) designed for high-throughput observability in Render and cloud environments.

---

## 2. Core Observability Fields

Every HTTP transaction log includes correlation metadata:
- `timestamp`: UTC ISO-8601 timestamp.
- `level`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- `logger`: Logger name (e.g. `bloop.api`, `bloop.middleware`).
- `message`: Diagnostic description.
- `request_id`: Correlation UUID propagated from `RequestIDMiddleware`.
- `method` & `path`: Target HTTP route.
- `status`: Final HTTP status code returned.
- `duration_ms`: Total request latency in milliseconds.

Example Access Log:
```text
[2026-09-17 12:28:15] [INFO] [bloop.middleware] HTTP POST /api/v1/tts returned 200 in 154.20ms [request_id=f71a938c4b12]
```

---

## 3. Secret Sanitization & Masking Policy

To comply with Prompt 06 security guidelines, `SecretMaskingFilter` intercepts all log records before output:

### Prohibited Log Contents
The following elements are strictly forbidden from logs:
- User plaintext passwords and bcrypt hash strings
- `JWT_SECRET_KEY` and raw Bearer authorization tokens
- `DATABASE_URL` connection strings with credentials
- `ELEVENLABS_API_KEY` credentials
- Full user speech synthesis text payloads
- Raw binary audio buffers

Any inadvertently passed connection strings or keys are masked:
```text
postgresql+psycopg://bloop_user:***@dpg-c123.render.com:5432/bloop_db
sk_live_***
```
