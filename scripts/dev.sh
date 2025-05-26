#!/bin/bash

# Echo Development Environment Startup Script
# This script starts all development services with proper process management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[ECHO DEV]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ECHO DEV]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ECHO DEV]${NC} $1"
}

print_error() {
    echo -e "${RED}[ECHO DEV]${NC} $1"
}

# Function to cleanup processes on exit
cleanup() {
    print_warning "Shutting down development environment..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        print_status "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        print_status "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "vinxi dev" 2>/dev/null || true
    
    print_success "Development environment stopped."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_status "🚀 Starting Echo Development Environment..."

# Check if Supabase is running
print_status "📊 Checking Supabase status..."
if ! pgrep -f "supabase" > /dev/null; then
    print_warning "Supabase not running. Starting Supabase..."
    cd packages/supabase && supabase start && cd ../..
    print_success "Supabase started successfully"
else
    print_success "Supabase is already running"
fi

# Wait a moment for Supabase to be ready
sleep 2

# Start backend in background
print_status "🐍 Starting Python FastAPI backend..."
cd apps/core
bash bin/dev.sh &
BACKEND_PID=$!
cd ../..

print_success "Backend started (PID: $BACKEND_PID) - http://localhost:8000"

# Wait for backend to start
print_status "⏳ Waiting for backend to be ready..."
sleep 5

# Start frontend in background
print_status "⚛️  Starting TypeScript frontend..."
cd apps/web
pnpm dev &
FRONTEND_PID=$!
cd ../..

print_success "Frontend started (PID: $FRONTEND_PID) - http://localhost:3000"

# Display status
echo ""
print_success "🎉 Echo Development Environment is ready!"
echo ""
echo -e "${CYAN}Services:${NC}"
echo -e "  ${GREEN}•${NC} Backend API:     http://localhost:8000"
echo -e "  ${GREEN}•${NC} API Docs:       http://localhost:8000/docs"
echo -e "  ${GREEN}•${NC} Frontend:       http://localhost:3000"
echo -e "  ${GREEN}•${NC} Supabase:       http://localhost:54321"
echo ""
echo -e "${CYAN}Process IDs:${NC}"
echo -e "  ${GREEN}•${NC} Backend PID:    $BACKEND_PID"
echo -e "  ${GREEN}•${NC} Frontend PID:   $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 