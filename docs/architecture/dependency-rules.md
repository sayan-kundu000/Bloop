# Bloop Architecture — Dependency & Import Rules

## 1. Directional Dependency Principle

All dependencies in Bloop must flow **unidirectionally downward** from consumers to producers. Circular imports and backward references are strictly prohibited.

```text
FRONTEND:
  app (bootstrap, router)
   ↓
  pages (route composition)
   ↓
  features (domain logic, hooks)
   ↓
  components/ui & common (presentation primitives)
   ↓
  lib/api & utils (infrastructure, formatting)

BACKEND:
  api/routes (HTTP handlers)
   ↓
  services (business orchestration)
   ↓
  repositories / providers / quantum (persistence & external adapters)
   ↓
  db / core (infrastructure, models, session, security)
```

---

## 2. Forbidden Import Matrix

| Initiating Module | Prohibited Target | Violation Reason |
| :--- | :--- | :--- |
| `repositories/*` | `api/routes/*` | Data access layer must not know about HTTP routing. |
| `providers/*` | `api/routes/*` | Third-party adapters must be transport-agnostic. |
| `models/*` | `services/*` | Persistent data models must not depend on business workflows. |
| `quantum/*` | `api/routes/*` | Quantum computing layer must remain standalone & testable without web servers. |
| `quantum/*` | `models/*` | Algorithm simulations must not depend on SQL tables. |
| `components/ui/*` | `features/*` | Visual UI primitives must remain reusable across all features. |
| `stores/*` | `pages/*` | State containers must not import route pages. |
| `backend/*` | `frontend/*` | Complete separation of server and client codebases. |

---

## 3. Allowed Import Patterns

### Frontend
```typescript
// ✅ Good: Feature importing a UI primitive
import { Button } from '../../components/ui';

// ✅ Good: Feature importing the centralized API client
import { apiClient } from '../../lib/api/client';

// ✅ Good: Page composing feature components
import { WorkspacePage } from '../features/tts/components/Workspace';

// ❌ FORBIDDEN: UI primitive importing a domain feature
import { useTTS } from '../features/tts'; // VIOLATION!
```

### Backend
```python
# ✅ Good: Route importing a service and schema
from backend.app.services.tts_service import TTSService
from backend.app.schemas.tts import TTSRequest

# ✅ Good: Service importing a repository and provider
from backend.app.repositories.user_repository import UserRepository
from backend.app.providers.tts.base import TTSProvider

# ❌ FORBIDDEN: Repository importing a route handler
from backend.app.api.routes.tts import generate_speech # VIOLATION!
```
