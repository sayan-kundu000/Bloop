# Backend Middleware Pipeline

## 1. Overview

The Bloop backend utilizes an ordered middleware pipeline implemented in [`backend/app/core/middleware.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/core/middleware.py) to handle cross-cutting HTTP concerns cleanly before requests reach route handlers.

---

## 2. Ordered Pipeline & Starlette Execution Order

In Starlette/FastAPI, middleware components added via `app.add_middleware()` wrap the application in reverse order of addition. The last added middleware is the first to intercept incoming requests and the last to process outgoing responses.

```text
Incoming Request
      │
      ▼
┌────────────────────────────────────────┐
│ 1. CORS Middleware                     │
│    - Evaluates Origin header           │
│    - Handles OPTIONS preflight         │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ 2. Payload Limit Middleware            │
│    - Checks Content-Length <= 2MB      │
│    - Drops oversized requests (413)    │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ 3. Request ID Middleware               │
│    - Extracts/validates X-Request-ID   │
│    - Generates clean UUID4 if missing  │
│    - Binds to request.state.request_id │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ 4. Security Headers Middleware         │
│    - Applies nosniff, DENY, etc.       │
└──────────────────┬─────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│ 5. Request Timing Middleware           │
│    - Starts high-resolution timer      │
│    - Invokes downstream application    │
│    - Attaches X-Response-Time header   │
│    - Emits structured access log       │
└──────────────────┬─────────────────────┘
                   │
                   ▼
          FastAPI Router / Route
```

---

## 3. Middleware Components

### 3.1 CORS Middleware (`CORSMiddleware`)
- Configured dynamically via `settings.cors_origins`.
- In development: Allows local frontend origin `http://localhost:5173`.
- In production: Strictly restricts origins to `https://bloop.vercel.app` (wildcards with credentials strictly prohibited).
- Exposes correlation headers: `X-Request-ID`, `X-Response-Time`.

### 3.2 Request ID Correlation (`RequestIDMiddleware`)
- Intercepts incoming `X-Request-ID`.
- Sanitizes input against injection attacks (enforcing alphanumeric, hyphens, underscores, length <= 64).
- Stores the ID in `request.state.request_id`.
- Injects `X-Request-ID` into outgoing HTTP response headers for end-to-end distributed tracing.

### 3.3 Defensive Security Headers (`SecurityHeadersMiddleware`)
Applies modern browser defense headers:
- `X-Content-Type-Options: nosniff`: Prevents MIME-type confusion attacks.
- `X-Frame-Options: DENY`: Prevents clickjacking within iframe embeds.
- `Referrer-Policy: strict-origin-when-cross-origin`: Restricts referrer leaks across origins.
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`: Blocks browser hardware access.
- `X-XSS-Protection: 1; mode=block`: Enables legacy browser XSS filters.

### 3.4 Request Timing & Observability (`RequestTimingMiddleware`)
- Captures start time using `time.perf_counter()`.
- Calculates total request processing latency and appends `X-Response-Time: <duration>ms`.
- Outputs structured access log without exposing sensitive headers (e.g. `Authorization`) or request bodies:
  ```text
  HTTP POST /api/v1/tts returned 200 in 142.30ms [request_id=c14e9f74a01c4abcb9f]
  ```

### 3.5 Payload Size Protection (`PayloadLimitMiddleware`)
- Inspects the `Content-Length` header before parsing request bodies into memory.
- If payload exceeds `2,097,152` bytes (2MB), returns `HTTP 413 REQUEST_ENTITY_TOO_LARGE`.
- Mitigates denial-of-service attempts via massive text floods.
