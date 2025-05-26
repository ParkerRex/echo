#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Navigate to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to check if Supabase CLI is installed
check_supabase_cli() {
    if ! command -v supabase &> /dev/null; then
        log_error "Supabase CLI is not installed. Please install it first:"
        log_info "  npm install -g supabase"
        log_info "  or visit: https://supabase.com/docs/guides/cli"
        exit 1
    fi
    log_success "Supabase CLI is available"
}

# Function to check if pnpm is installed
check_pnpm() {
    if ! command -v pnpm &> /dev/null; then
        log_error "pnpm is not installed. Please install it first:"
        log_info "  npm install -g pnpm"
        exit 1
    fi
    log_success "pnpm is available"
}

# Function to check if Python virtual environment exists
check_python_env() {
    if [ ! -d "apps/core/.venv" ]; then
        log_warning "Python virtual environment not found. Creating it..."
        cd apps/core
        if command -v uv &> /dev/null; then
            uv venv
            source .venv/bin/activate
            uv pip install -e ".[dev]"
        else
            python -m venv .venv
            source .venv/bin/activate
            pip install -e ".[dev]"
        fi
        cd "$PROJECT_ROOT"
        log_success "Python environment created"
    else
        log_success "Python environment exists"
    fi
}

# Function to start Supabase if not running
start_supabase() {
    log_info "Checking Supabase status..."
    cd packages/supabase
    
    if ! supabase status &> /dev/null; then
        log_info "Starting Supabase local development..."
        supabase start
        log_success "Supabase started"
    else
        log_success "Supabase is already running"
    fi
    
    cd "$PROJECT_ROOT"
}

# Function to stop Supabase
stop_supabase() {
    log_info "Stopping Supabase..."
    cd packages/supabase
    supabase stop --no-backup
    cd "$PROJECT_ROOT"
    log_success "Supabase stopped"
}

# Function to generate types
generate_types() {
    log_info "Generating types..."
    if [ -f "scripts/generate-types.sh" ]; then
        if ./scripts/generate-types.sh all; then
            log_success "Types generated successfully"
        else
            log_warning "Type generation failed, but continuing..."
        fi
    else
        log_warning "Type generation script not found"
    fi
}

# Function to install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    # Install root dependencies
    if [ -f "package.json" ]; then
        pnpm install
    fi
    
    # Install web app dependencies
    if [ -f "apps/web/package.json" ]; then
        cd apps/web
        pnpm install
        cd "$PROJECT_ROOT"
    fi
    
    log_success "Dependencies installed"
}

# Function to start the backend API
start_backend() {
    log_info "Starting backend API..."
    cd apps/core
    
    # Activate Python virtual environment
    source .venv/bin/activate
    
    # Start the API server in the background
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_ROOT/.backend.pid"
    
    cd "$PROJECT_ROOT"
    log_success "Backend API started (PID: $BACKEND_PID)"
}

# Function to start the frontend
start_frontend() {
    log_info "Starting frontend..."
    cd apps/web
    
    # Start the frontend server in the background
    pnpm dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend.pid"
    
    cd "$PROJECT_ROOT"
    log_success "Frontend started (PID: $FRONTEND_PID)"
}

# Function to stop all services
stop_services() {
    log_info "Stopping all services..."
    
    # Stop frontend
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_success "Frontend stopped"
        fi
        rm -f .frontend.pid
    fi
    
    # Stop backend
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_success "Backend stopped"
        fi
        rm -f .backend.pid
    fi
    
    # Stop any remaining processes on our ports
    pkill -f "uvicorn.*8000" || true
    pkill -f "pnpm.*dev" || true
    
    log_success "All services stopped"
}

# Function to wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for backend
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Backend is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Backend did not start within expected time"
            return 1
        fi
        
        log_info "Waiting for backend... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    # Wait for frontend
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            log_success "Frontend is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_warning "Frontend may still be starting..."
            break
        fi
        
        log_info "Waiting for frontend... ($attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
}

# Function to show service status
show_status() {
    echo ""
    log_info "🌐 Service URLs:"
    log_info "  Frontend:     http://localhost:3000"
    log_info "  Backend API:  http://localhost:8000"
    log_info "  API Docs:     http://localhost:8000/docs"
    log_info "  Supabase:     http://localhost:54321"
    log_info "  Supabase DB:  postgresql://postgres:postgres@localhost:54322/postgres"
    log_info "  Supabase Studio: http://localhost:54323"
    echo ""
    log_info "📝 Useful commands:"
    log_info "  Stop all:     $0 stop"
    log_info "  Restart:      $0 restart"
    log_info "  Status:       $0 status"
    log_info "  Generate types: pnpm types:generate"
    echo ""
}

# Cleanup function for graceful shutdown
cleanup() {
    log_info "Received interrupt signal, cleaning up..."
    stop_services
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    log_info "🚀 Starting Echo local development environment..."
    
    # Check prerequisites
    check_supabase_cli
    check_pnpm
    check_python_env
    
    # Start Supabase
    start_supabase
    
    # Install dependencies
    install_dependencies
    
    # Generate types
    generate_types
    
    # Start services
    start_backend
    start_frontend
    
    # Wait for services to be ready
    wait_for_services
    
    # Show status
    log_success "🎉 Development environment is ready!"
    show_status
    
    # Keep the script running and wait for interrupt
    log_info "Press Ctrl+C to stop all services"
    while true; do
        sleep 1
    done
}

# Handle script arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        stop_services
        stop_supabase
        ;;
    "restart")
        log_info "Restarting development environment..."
        stop_services
        main
        ;;
    "status")
        show_status
        if [ -f ".backend.pid" ] && [ -f ".frontend.pid" ]; then
            BACKEND_PID=$(cat .backend.pid)
            FRONTEND_PID=$(cat .frontend.pid)
            if kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; then
                log_success "All services are running"
            else
                log_warning "Some services may not be running"
            fi
        else
            log_warning "Services do not appear to be running"
        fi
        ;;
    "supabase-only")
        check_supabase_cli
        start_supabase
        log_success "Supabase is running"
        show_status
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|status|supabase-only]"
        echo "  start         - Start the full development environment (default)"
        echo "  stop          - Stop all services including Supabase"
        echo "  restart       - Restart the development environment"
        echo "  status        - Show service status and URLs"
        echo "  supabase-only - Start only Supabase (useful for backend-only development)"
        exit 1
        ;;
esac 