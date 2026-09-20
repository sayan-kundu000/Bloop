# Bloop Development — Project Navigation Guide

## 1. Quick Development Commands

### Frontend
```bash
cd frontend
npm run dev      # Launch Vite dev server on http://localhost:3000
npm run build    # Strict TypeScript compile + production bundle build
npm test         # Run Vitest test runner
npm run lint     # Run fast Oxlint static analysis
```

### Backend
```bash
# Using uv (recommended)
uv run uvicorn backend.app.main:app --reload --port 8000
uv run pytest backend/tests tests -v
uv run alembic upgrade head
```

### Automation Scripts
```powershell
# Windows PowerShell
.\scripts\development\dev.ps1          # Launch frontend & backend concurrently
.\scripts\database\migrate.ps1         # Run pending Alembic migrations
.\scripts\deployment\check-health.ps1  # Probe /api/v1/health status
```
```bash
# Unix / macOS
./scripts/development/dev.sh
./scripts/database/migrate.sh
./scripts/deployment/check-health.sh
```

---

## 2. Fast File Resolution Guide

When asked to implement or update a component, navigate directly to:

- **Speech Synthesis Engine:** `backend/app/services/tts_service.py`
- **Voice Catalog Data:** `backend/app/services/voice_service.py`
- **Simulation Fallback Provider:** `backend/app/providers/mock_provider.py`
- **ElevenLabs Live Provider:** `backend/app/providers/elevenlabs_provider.py`
- **Quantum Classifier:** `backend/app/quantum/text_classifier.py`
- **Quantum Emotion Analyzer:** `backend/app/quantum/emotion_qnn.py`
- **Quantum Voice Modulator:** `backend/app/quantum/voice_modulator.py`
- **Frontend Workspace:** `frontend/src/pages/WorkspacePage.tsx`
- **Audio Store:** `frontend/src/stores/audioStore.ts`
- **Workspace Store:** `frontend/src/stores/workspaceStore.ts`
- **API Client:** `frontend/src/lib/api/client.ts`
- **Query Keys:** `frontend/src/lib/query/index.ts`
