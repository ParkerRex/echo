#!/bin/bash

# Simple, reliable API startup script for Echo
# Just starts the FastAPI backend - no bullshit

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Echo API (Development Mode)${NC}"
echo -e "${YELLOW}   Use 'pnpm dev:api' for convenience${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Please install uv first:${NC}"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "apps/core/.venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating it...${NC}"
    cd apps/core
    uv venv
    uv sync --dev
    cd ../..
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

echo -e "${BLUE}📦 Starting FastAPI server...${NC}"
echo -e "${YELLOW}   API will be available at: http://localhost:8000${NC}"
echo -e "${YELLOW}   API docs will be available at: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Set PYTHONPATH and start the server
export PYTHONPATH="$(pwd)"
cd apps/core
uv run uvicorn apps.core.main:app --reload --host 0.0.0.0 --port 8000 