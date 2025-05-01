#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping services...${NC}"

# Store the project root directory
PROJECT_ROOT=$(pwd)

# Check if backend PID file exists and stop the backend
if [ -f "${PROJECT_ROOT}/logs/backend.pid" ]; then
  BACKEND_PID=$(cat "${PROJECT_ROOT}/logs/backend.pid")
  if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${BLUE}Stopping backend server (PID: $BACKEND_PID)...${NC}"
    kill -15 $BACKEND_PID
    echo -e "${GREEN}Backend server stopped.${NC}"
  else
    echo -e "${RED}Backend server is not running (PID: $BACKEND_PID).${NC}"
  fi
  rm "${PROJECT_ROOT}/logs/backend.pid"
else
  echo -e "${RED}Backend PID file not found. Backend may not be running.${NC}"
  # Try to find and kill Flask processes
  echo -e "${BLUE}Searching for Flask processes...${NC}"
  pkill -f "python.*video_processor/app.py" && echo -e "${GREEN}Found and killed Flask processes.${NC}" || echo -e "${RED}No Flask processes found.${NC}"
fi

# Check if frontend PID file exists and stop the frontend
if [ -f "${PROJECT_ROOT}/logs/frontend.pid" ]; then
  FRONTEND_PID=$(cat "${PROJECT_ROOT}/logs/frontend.pid")
  if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${BLUE}Stopping frontend server (PID: $FRONTEND_PID)...${NC}"
    kill -15 $FRONTEND_PID
    echo -e "${GREEN}Frontend server stopped.${NC}"
  else
    echo -e "${RED}Frontend server is not running (PID: $FRONTEND_PID).${NC}"
  fi
  rm "${PROJECT_ROOT}/logs/frontend.pid"
else
  echo -e "${RED}Frontend PID file not found. Frontend may not be running.${NC}"
  # Try to find and kill Vite/Node processes
  echo -e "${BLUE}Searching for Vite processes...${NC}"
  pkill -f "node.*vinxi" && echo -e "${GREEN}Found and killed Vite processes.${NC}" || echo -e "${RED}No Vite processes found.${NC}"
fi

echo -e "${GREEN}All services stopped successfully.${NC}" 