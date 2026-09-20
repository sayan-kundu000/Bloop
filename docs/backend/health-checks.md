# Health, Liveness & Readiness Probes

## 1. Overview

Bloop exposes dedicated health check endpoints implemented in [`backend/app/api/v1/endpoints/health.py`](file:///c:/Users/DELL/Downloads/Bloop/backend/app/api/v1/endpoints/health.py) to integrate with cloud load balancers, Render zero-downtime deployments, and uptime monitoring services.

---

## 2. Probe Specifications

### 2.1 Comprehensive Health Probe (`GET /api/v1/health`)
Provides complete subsystem status across persistence, provider, and quantum modules without leaking sensitive infrastructure parameters.

Response (200 OK):
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "healthy",
    "provider": "configured",
    "quantum": "available",
    "app_name": "Bloop",
    "version": "1.0.0",
    "environment": "production"
  },
  "message": "Bloop service is operational."
}
```

### 2.2 Liveness Probe (`GET /api/v1/health/live`)
Answers: **Is the application process alive and executing?**
- Used by container supervisors to detect deadlocks.
- Does not depend on external providers or databases.
- Returns `200 OK` immediately:
```json
{
  "success": true,
  "data": {
    "status": "alive"
  },
  "message": "Application process is alive."
}
```

### 2.3 Readiness Probe (`GET /api/v1/health/ready`)
Answers: **Can this instance currently serve API traffic and interact with PostgreSQL?**
- Executes a fast query (`SELECT 1`) on the database session.
- Returns `200 OK` when ready:
```json
{
  "success": true,
  "data": {
    "status": "ready",
    "database": "connected"
  },
  "message": "Application is ready to receive traffic."
}
```
- Returns `503 SERVICE_UNAVAILABLE` if PostgreSQL connection fails, instructing the load balancer to halt traffic routing to this instance.

---

## 3. Render Deployment Configuration

In [`render.yaml`](file:///c:/Users/DELL/Downloads/Bloop/render.yaml), Render monitors instance health using:

```yaml
services:
  - type: web
    name: bloop-api
    healthCheckPath: /api/v1/health
```

Deployments will not switch traffic to a new instance until `/api/v1/health` returns HTTP 200.
