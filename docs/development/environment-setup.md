# Bloop Developer Environment Setup Guide

**Document Identifier:** BLOOP-DEV-SETUP-006  
**Status:** Approved Technical Guide  
**Applies to:** Local Workstation Setup (Windows, macOS, Linux)  

---

## 1. Prerequisites

Ensure you have the following toolchains installed on your development machine:
- **Python 3.12+** (tested with 3.12.x)
- **Node.js 20+** with `npm`
- **Git**

---

## 2. Step-by-Step Local Environment Configuration

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/bloop.git
cd bloop
```

### Step 2: Configure Backend Environment
Copy the backend environment template to active local configuration:
```bash
# Linux / macOS
cp backend/.env.example backend/.env

# Windows PowerShell
Copy-Item backend\.env.example backend\.env
```

Review the values in `backend/.env`. By default, it is preconfigured for local development:
- `APP_ENV=development`
- `APP_DEBUG=true`
- `DATABASE_URL=sqlite:///./bloop.db` (zero-setup local database)
- `ELEVENLABS_API_KEY=` (leave empty to use offline SimulationTTSProvider)

*(Optional)* If you wish to test with local PostgreSQL instead of SQLite:
```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/bloop_dev
```

### Step 3: Configure Frontend Environment
Copy the frontend environment template to active local configuration:
```bash
# Linux / macOS
cp frontend/.env.example frontend/.env

# Windows PowerShell
Copy-Item frontend\.env.example frontend\.env
```

The default contents:
```env
VITE_API_BASE_URL=http://localhost:8000
```
> **IMPORTANT:** Never add private API keys, database strings, or JWT secrets to `frontend/.env`. Variables prefixed with `VITE_` are publicly accessible in the browser bundle.

---

## 3. Installing Dependencies & Running Services

### Step 4: Setup Backend Virtual Environment & Install Dependencies
```bash
# Create and activate virtual environment
python -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Install runtime and development dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt
```

### Step 5: Start FastAPI Backend Server
```bash
# Run backend server with auto-reload
python -m uvicorn backend.app.main:app --reload --port 8000
```
FastAPI will start listening at: `http://localhost:8000`

### Step 6: Setup Frontend & Start Vite Dev Server
In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
Vite will start listening at: `http://localhost:5173`

---

## 4. Verifying Health & Running Tests

### Step 7: Verify Backend Health Endpoint
Send an HTTP GET request to verify the server is operational:
```bash
curl http://localhost:8000/api/v1/health
```
Expected JSON Response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "app_name": "Bloop",
    "version": "0.1.0",
    "environment": "development",
    "elevenlabs_configured": false
  },
  "message": "Bloop service is operational."
}
```

Interactive API documentation is available at `http://localhost:8000/docs` while `APP_DEBUG=true`.

### Step 8: Run Automated Test Suites

#### Backend Test Suite (pytest)
```bash
pytest backend/tests
```

#### Frontend Test Suite (vitest)
```bash
cd frontend
npm test
```

---

## 5. Troubleshooting Local Issues

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| `ConfigurationError` or `ValueError` at boot | `APP_DEBUG=true` while `APP_ENV=production` | Ensure `APP_ENV=development` in your local `.env`. |
| CORS error in browser console | Origin mismatch | Verify `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`. |
| Speech synthesis fails | Missing ElevenLabs key | Leave `ELEVENLABS_API_KEY` empty to use offline simulation, or provide a valid key. |
| Test suite fails with production DB error | Production DB string in test run | Ensure tests run with `APP_ENV=test` and SQLite test URI (`sqlite:///./test_bloop.db`). |
