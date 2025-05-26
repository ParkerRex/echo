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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_success "Docker is running"
}

# Function to wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    local max_attempts=60
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        local healthy_services=$(docker-compose ps --services --filter "status=running" | wc -l)
        local total_services=$(docker-compose ps --services | wc -l)
        
        if [ "$healthy_services" -eq "$total_services" ]; then
            log_success "All services are running"
            return 0
        fi
        
        log_info "Attempt $attempt/$max_attempts: $healthy_services/$total_services services running..."
        sleep 5
        ((attempt++))
    done
    
    log_error "Services did not start within expected time"
    docker-compose ps
    return 1
}

# Function to apply database migrations
apply_migrations() {
    log_info "Applying database migrations..."
    
    # Wait a bit more for the database to be fully ready
    sleep 10
    
    if docker-compose exec -T supabase-db psql -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Database is ready"
        
        # Apply migrations using the Supabase CLI in the container
        if [ -d "packages/supabase/migrations" ] && [ "$(ls -A packages/supabase/migrations)" ]; then
            log_info "Applying Supabase migrations..."
            cd packages/supabase
            
            # Apply migrations directly to the database
            for migration in migrations/*.sql; do
                if [ -f "$migration" ]; then
                    log_info "Applying migration: $(basename "$migration")"
                    docker-compose exec -T supabase-db psql -U postgres -d postgres -f "/dev/stdin" < "$migration"
                fi
            done
            
            cd "$PROJECT_ROOT"
            log_success "Migrations applied successfully"
        else
            log_warning "No migrations found to apply"
        fi
    else
        log_error "Database is not ready for migrations"
        return 1
    fi
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

# Main execution
main() {
    log_info "🚀 Starting Echo development environment..."
    
    # Check prerequisites
    check_docker
    
    # Stop any existing containers
    log_info "Stopping any existing containers..."
    docker-compose down --remove-orphans
    
    # Start services
    log_info "Starting services with Docker Compose..."
    docker-compose up -d
    
    # Wait for services to be healthy
    wait_for_services
    
    # Apply migrations
    apply_migrations
    
    # Generate types
    generate_types
    
    # Show service status
    log_success "🎉 Development environment is ready!"
    echo ""
    log_info "📊 Service Status:"
    docker-compose ps
    echo ""
    log_info "🌐 Access URLs:"
    log_info "  Frontend:     http://localhost:3000"
    log_info "  Backend API:  http://localhost:8000"
    log_info "  API Docs:     http://localhost:8000/docs"
    log_info "  Supabase:     http://localhost:54321"
    log_info "  Supabase DB:  postgresql://postgres:postgres@localhost:54322/postgres"
    log_info "  Redis:        redis://localhost:6379"
    log_info "  Mail UI:      http://localhost:54325"
    echo ""
    log_info "📝 Useful commands:"
    log_info "  View logs:    docker-compose logs -f [service_name]"
    log_info "  Stop all:     docker-compose down"
    log_info "  Restart:      docker-compose restart [service_name]"
    log_info "  Generate types: ./scripts/generate-types.sh"
    echo ""
    log_info "🔄 To follow logs from all services:"
    log_info "  docker-compose logs -f"
}

# Handle script arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        log_info "Stopping all services..."
        docker-compose down --remove-orphans
        log_success "All services stopped"
        ;;
    "restart")
        log_info "Restarting development environment..."
        docker-compose down --remove-orphans
        main
        ;;
    "logs")
        docker-compose logs -f "${2:-}"
        ;;
    "status")
        docker-compose ps
        ;;
    *)
        echo "Usage: $0 [start|stop|restart|logs|status]"
        echo "  start    - Start the development environment (default)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart the development environment"
        echo "  logs     - Follow logs (optionally specify service name)"
        echo "  status   - Show service status"
        exit 1
        ;;
esac 