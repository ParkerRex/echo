#!/usr/bin/env bash
set -euo pipefail

# Get the app directory (apps/core)
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_DIR"

# Set PYTHONPATH to include the project root directory (one level up from apps/core)
PROJECT_ROOT_DIR="$(cd "$APP_DIR/../.." && pwd)"
export PYTHONPATH=$PROJECT_ROOT_DIR

echo "Ensuring Python dependencies are in sync..."
uv sync # Sync dependencies from uv.lock

echo "Starting FastAPI server on port 8000..."
# Run uvicorn using uv to ensure it's from the virtual environment
uv run uvicorn apps.core.main:app --reload --port 8000