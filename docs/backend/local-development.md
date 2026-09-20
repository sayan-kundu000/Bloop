# Backend Local Development Guide

## 1. Prerequisites

- Python 3.12+
- Git
- PostgreSQL 16 (or local SQLite for lightweight testing)

---

## 2. Setup Workflow

### Step 1: Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/organization/bloop.git
cd bloop
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate on macOS / Linux
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 3: Configure Environment Variables
Copy the template and configure your local settings:
```bash
cp backend/.env.example backend/.env
```
Key development settings:
```ini
APP_NAME=Bloop
APP_ENV=development
APP_DEBUG=true
DATABASE_URL=sqlite:///./dev_bloop.db
JWT_SECRET_KEY=bloop-development-jwt-secret-key-32-chars!
ELEVENLABS_API_KEY=
```

### Step 4: Run Database Migrations
```bash
cd backend
alembic upgrade head
cd ..
```

### Step 5: Start the FastAPI Backend
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. Verification & Exploration

Once Uvicorn starts:
- **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON Schema**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)
- **Health Check Probe**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Liveness Probe**: [http://localhost:8000/api/v1/health/live](http://localhost:8000/api/v1/health/live)
- **Readiness Probe**: [http://localhost:8000/api/v1/health/ready](http://localhost:8000/api/v1/health/ready)
