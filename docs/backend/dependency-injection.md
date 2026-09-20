# Backend Dependency Injection

## 1. Overview

Bloop relies on FastAPI's native `Depends()` mechanism to handle cross-cutting concerns, session lifecycles, security resolution, and service provisioning.

Benefits:
- **Zero Global Mutable State**: Every request receives clean, request-scoped sessions.
- **Testability**: Any dependency can be overridden in tests via `app.dependency_overrides[dep] = mock_dep`.
- **Decoupled Architecture**: Routes do not instantiate database connections or service dependencies directly.

---

## 2. Dependency Graph

```mermaid
graph TD
    Request[HTTP Request] --> Handler[Route Handler]
    
    subgraph "FastAPI Dependency Injection"
        GetDB["get_db()<br/>Yields Session"]
        GetSettings["get_settings()<br/>Yields Settings"]
        GetHTTP["get_http_client()<br/>Yields AsyncClient"]
        GetAuth["get_current_user()<br/>Resolves JWT -> User"]
        GetAdmin["get_current_active_superuser()<br/>Verifies is_superuser"]
        GetTTS["get_speech_service()<br/>Instantiates TTSService"]
        GetVoice["get_voice_service()<br/>Instantiates VoiceService"]
        GetQuantum["get_quantum_service()<br/>Instantiates QuantumService"]
    end

    subgraph "Persistence & Subsystems"
        DBSession[(SQLAlchemy Session)]
        Config[(Application Settings)]
        HTTPPool[(Managed Connection Pool)]
        UserEntity[(User ORM Model)]
        ElevenLabs[(ElevenLabs Adapter)]
        Qiskit[(Quantum Simulators)]
    end

    Handler --> GetDB --> DBSession
    Handler --> GetSettings --> Config
    Handler --> GetHTTP --> HTTPPool
    Handler --> GetAuth --> GetDB
    GetAuth --> UserEntity
    Handler --> GetAdmin --> GetAuth
    Handler --> GetTTS --> GetDB
    GetTTS --> ElevenLabs
    Handler --> GetVoice --> GetDB
    Handler --> GetQuantum --> GetDB
    GetQuantum --> Qiskit
```

---

## 3. Core Dependencies

### 3.1 Database Session (`get_db`)
- Manages an isolated SQLAlchemy 2.x `Session` per incoming HTTP request.
- Automatically commits or rolls back on unhandled exceptions:
  ```python
  def get_db() -> Generator[Session, None, None]:
      db = SessionLocal()
      try:
          yield db
      except Exception:
          db.rollback()
          raise
      finally:
          db.close()
  ```

### 3.2 Authentication & Authorization
- `get_current_user`: Decodes JWT Bearer token, verifies active status, and resolves `User` model.
- `get_optional_current_user`: Returns authenticated `User` if token is provided; otherwise returns `None`.
- `get_current_active_superuser`: Asserts that `current_user.is_superuser` is `True`, rejecting others with `403 FORBIDDEN`.

### 3.3 Managed HTTP Client (`get_http_client`)
- Resolves the connection-pooled `httpx.AsyncClient` created during application lifespan.
- Enforces strict connection, read, and write timeouts for outbound provider requests.

### 3.4 Service Factory Dependencies
- `get_speech_service(db=Depends(get_db)) -> TTSService`
- `get_voice_service(db=Depends(get_db)) -> VoiceService`
- `get_quantum_service(db=Depends(get_db)) -> QuantumService`
- `get_auth_service(db=Depends(get_db)) -> AuthService`

---

## 4. Test Overrides Pattern

FastAPI allows clean test isolation by overriding dependencies without altering production code:

```python
from backend.app.db.session import get_db

def test_custom_endpoint(client, test_db_session):
    app.dependency_overrides[get_db] = lambda: test_db_session
    try:
        response = client.get("/api/v1/users/me")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```
