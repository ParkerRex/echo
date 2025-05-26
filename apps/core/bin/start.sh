#!/bin/bash

# Start script for Echo Core API (Production mode)
# This script starts the FastAPI server using uvicorn in production configuration

set -e

echo "🚀 Starting Echo Core API (Production mode)..."

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
fi

# Start the FastAPI server with production settings
echo "🌐 Starting FastAPI server on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 