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
    
    if [ ! -z "$TURBO_PID" ]; then
        print_status "Stopping Turbo dev processes (PID: $TURBO_PID)..."
        kill $TURBO_PID 2>/dev/null || true
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "vinxi dev" 2>/dev/null || true
    pkill -f "turbo run dev" 2>/dev/null || true
    
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

# Start all services using Turbo
print_status "🚀 Starting all services with Turbo..."
pnpm dev &
TURBO_PID=$!

print_success "All services started via Turbo (PID: $TURBO_PID)"

# Wait for services to start
print_status "⏳ Waiting for services to be ready..."
sleep 8

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
echo -e "${CYAN}Process Management:${NC}"
echo -e "  ${GREEN}•${NC} Turbo PID:      $TURBO_PID"
echo -e "  ${GREEN}•${NC} All services managed by Turbo"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for Turbo process
wait $TURBO_PID 