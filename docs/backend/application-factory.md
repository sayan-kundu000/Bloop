# Application Factory (`create_app`)

## 1. Purpose & Design Rationale

The Bloop application is assembled using the **Application Factory** pattern in [`backend/app/factory.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/factory.py).

Instead of instantiating `FastAPI` globally at module import time, `create_app(custom_settings: Optional[Settings] = None) -> FastAPI` provides:
1. **Test Isolation**: Automated tests can instantiate isolated app instances with custom settings or mocked dependencies without polluting the global process.
2. **Deterministic Lifecycle**: Clear startup and shutdown boundaries via FastAPI's modern `lifespan` context manager.
3. **Environment-Driven Configuration**: Documentation routes (`/docs`, `/redoc`, `/openapi.json`) are automatically enabled or disabled based on `settings.APP_DEBUG`.
4. **Decoupled Entrypoint**: [`backend/app/main.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/main.py) serves solely as the executable entrypoint for ASGI servers (Uvicorn).

---

## 2. Factory Assembly Pipeline

```text
create_app(custom_settings)
   │
   ├── 1. Initialize Structured Logging (setup_logging)
   ├── 2. Define Lifespan Context Manager
   │      ├── Startup: Verify DB connectivity, import dev voices, init HTTP client
   │      └── Shutdown: Close HTTP client, dispose DB engine connections
   ├── 3. Instantiate FastAPI with Title, Description, Version & OpenAPI Tags
   ├── 4. Register Middleware Pipeline (register_middleware)
   ├── 5. Register Exception Handlers (register_exception_handlers)
   ├── 6. Mount Versioned API Routes (app.include_router(api_router, prefix="/api/v1"))
   ├── 7. Mount Root Metadata Probe (GET /)
   └── 8. Return Configured FastAPI Instance
```

---

## 3. Lifespan Responsibilities

### Startup Phase
- **Safe DB Connectivity**: Executes baseline table verification (`init_db`) without destructive drops or migrations.
- **Dynamic Voice Seeding Rule**: When `APP_ENV == "production"`, zero voice records are seeded; in development/testing, local voice templates are imported for offline development.
- **HTTP Client Initialization**: Instantiates an application-scoped, connection-pooled `httpx.AsyncClient` in `app.state.http_client`.
- **Zero Blocking Heavy Operations**: Quantum simulations and ElevenLabs external requests are **never** executed during application startup.

### Shutdown Phase
- **HTTP Client Termination**: Closes all active connection pools in `app.state.http_client`.
- **Database Connection Disposal**: Calls `engine.dispose()` to immediately release all pooled PostgreSQL connections.
- **Graceful Log Flush**: Emits structured shutdown notice.

---

## 4. Usage Examples

### Running Locally with Uvicorn
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### In Testing with Dependency Overrides
```python
from backend.app.factory import create_app
from backend.app.core.config import Settings

custom_settings = Settings(
    APP_NAME="Test Bloop",
    APP_ENV="test",
    APP_DEBUG=False,
    DATABASE_URL="sqlite:///./test.db",
    JWT_SECRET_KEY="a" * 32,
)

test_app = create_app(custom_settings=custom_settings)
```
