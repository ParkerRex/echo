#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting services...${NC}"

# Store the project root directory
PROJECT_ROOT=$(pwd)

# Environment variables for backend
export GCS_UPLOAD_BUCKET=automations-youtube-videos-2025
export GOOGLE_APPLICATION_CREDENTIALS="${PROJECT_ROOT}/@credentials/service_account.json"

# Start backend server
echo -e "${BLUE}Starting backend server...${NC}"
cd "${PROJECT_ROOT}/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo -e "${RED}Error: Python virtual environment not found in backend/venv${NC}"
  echo -e "${BLUE}Creating virtual environment...${NC}"
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

# Start backend in background
python video_processor/app.py > "${PROJECT_ROOT}/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "${PROJECT_ROOT}/logs/backend.pid"
echo -e "${GREEN}Backend server started with PID: $BACKEND_PID${NC}"
echo -e "${GREEN}Logs: ${PROJECT_ROOT}/logs/backend.log${NC}"

# Start frontend server
echo -e "${BLUE}Starting frontend server...${NC}"
cd "${PROJECT_ROOT}/frontend"
pnpm dev > "${PROJECT_ROOT}/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "${PROJECT_ROOT}/logs/frontend.pid"
echo -e "${GREEN}Frontend server started with PID: $FRONTEND_PID${NC}"
echo -e "${GREEN}Logs: ${PROJECT_ROOT}/logs/frontend.log${NC}"

echo -e "${GREEN}All services started!${NC}"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}Backend:${NC} http://localhost:8080"
echo -e "${BLUE}To stop all services, run:${NC} ./stop-services.sh" 