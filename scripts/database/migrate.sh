#!/usr/bin/env bash
# Bloop Database Migration Script (Linux / macOS)
set -e

echo "Running Alembic database migrations..."
alembic upgrade head
echo "Database migrations applied successfully!"
