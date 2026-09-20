#!/usr/bin/env bash
# Bloop Development Launch Script (Linux / macOS)
set -e

echo "===================================================="
echo "  Launching Bloop Full-Stack Development Environment"
echo "===================================================="

if [ ! -f ".env" ]; then
    echo "[INFO] Creating .env from .env.example..."
    cp .env.example .env
fi

# Activate virtual environment if available
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start backend
echo "[1/2] Starting FastAPI Backend on http://localhost:8000..."
uvicorn backend.app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Starting Vite Frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
