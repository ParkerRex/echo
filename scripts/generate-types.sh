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

# Load environment variables from root directory
ENV_FILES=(".env" ".env.development")
for ENV_FILE in "${ENV_FILES[@]}"; do
    if [ -f "$ENV_FILE" ]; then
        set -a
        source "$ENV_FILE"
        set +a
        log_info "Loaded environment variables from $ENV_FILE"
        break
    fi
done

if [ ! -f ".env" ] && [ ! -f ".env.development" ]; then
    log_warning "No .env or .env.development file found. Using default values."
fi

# Set default values for local development
DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:54322/postgres}"
SUPABASE_URL="${SUPABASE_URL:-http://localhost:54321}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU}"

# Function to check if a service is running
check_service() {
    local service_name="$1"
    local url="$2"
    local max_attempts=30
    local attempt=1

    log_info "Checking if $service_name is available at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$service_name is available"
            return 0
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "$service_name is not available after $max_attempts attempts"
            return 1
        fi
        
        log_info "Attempt $attempt/$max_attempts: $service_name not ready, waiting..."
        sleep 2
        ((attempt++))
    done
}

# Function to validate generated files
validate_file() {
    local file_path="$1"
    local file_type="$2"
    
    if [ ! -f "$file_path" ]; then
        log_error "$file_type file not generated: $file_path"
        return 1
    fi
    
    if [ ! -s "$file_path" ]; then
        log_error "$file_type file is empty: $file_path"
        return 1
    fi
    
    log_success "$file_type generated successfully: $file_path"
    return 0
}

# Function to generate SQLAlchemy ORM models
generate_orm_models() {
    log_info "Generating SQLAlchemy ORM models..."
    
    local output_dir="$PROJECT_ROOT/apps/core/app/db"
    local output_file="$output_dir/models.py"
    
    mkdir -p "$output_dir"
    
    cd "$PROJECT_ROOT/apps/core"
    
    if ! uv run sqlacodegen "$DATABASE_URL" --outfile "$output_file"; then
        log_error "Failed to generate SQLAlchemy models"
        return 1
    fi
    
    validate_file "$output_file" "SQLAlchemy models"
}

# Function to generate Pydantic models from Supabase
generate_pydantic_models() {
    log_info "Generating Pydantic models from Supabase schema..."
    
    local output_dir="$PROJECT_ROOT/apps/core/app/db_pydantic_models"
    local output_file="$output_dir/supabase_models.py"
    
    mkdir -p "$output_dir"
    
    cd "$PROJECT_ROOT/apps/core"
    
    # Export environment variables for supabase-pydantic
    export SUPABASE_URL
    export SUPABASE_SERVICE_ROLE_KEY
    
    if ! uv run supabase-pydantic --output "$output_file" --schema public --pydantic-v2; then
        log_error "Failed to generate Pydantic models"
        return 1
    fi
    
    validate_file "$output_file" "Pydantic models"
}

# Function to generate TypeScript types from Supabase
generate_typescript_types() {
    log_info "Generating TypeScript types from Supabase schema..."
    
    local output_dir="$PROJECT_ROOT/packages/supabase/types"
    local output_file="$output_dir/generated.ts"
    
    mkdir -p "$output_dir"
    
    cd "$PROJECT_ROOT/packages/supabase"
    
    # For local development, generate types directly from the database
    if ! npx supabase gen types typescript --local > "$output_file"; then
        log_error "Failed to generate TypeScript types"
        return 1
    fi
    
    validate_file "$output_file" "TypeScript types"
}

# Function to generate API types from Pydantic to TypeScript
generate_api_types() {
    log_info "Generating API TypeScript types from Pydantic API schemas..."
    
    local output_dir="$PROJECT_ROOT/apps/web/app/types"
    local output_file="$output_dir/api.ts"
    
    mkdir -p "$output_dir"
    
    cd "$PROJECT_ROOT/apps/core"
    
    # Use our custom API type generation script
    if ! uv run python bin/generate_api_types.py; then
        log_error "Failed to generate API TypeScript types"
        return 1
    fi
    
    validate_file "$output_file" "API TypeScript types"
}

# Function to run all type generation steps
generate_all_types() {
    log_info "Starting complete type generation process..."
    
    # Check if required services are running
    check_service "Supabase Database" "$DATABASE_URL" || {
        log_error "Database is not available. Please start Supabase first."
        exit 1
    }
    
    check_service "Supabase API" "$SUPABASE_URL/health" || {
        log_warning "Supabase API health check failed, but continuing..."
    }
    
    # Generate types in dependency order
    local failed_steps=()
    
    if ! generate_orm_models; then
        failed_steps+=("SQLAlchemy ORM models")
    fi
    
    if ! generate_pydantic_models; then
        failed_steps+=("Pydantic models")
    fi
    
    if ! generate_typescript_types; then
        failed_steps+=("TypeScript types")
    fi
    
    if ! generate_api_types; then
        failed_steps+=("API TypeScript types")
    fi
    
    # Report results
    if [ ${#failed_steps[@]} -eq 0 ]; then
        log_success "All type generation completed successfully!"
        log_info "Generated files:"
        log_info "  - SQLAlchemy models: apps/core/app/db/models.py"
        log_info "  - Pydantic models: apps/core/app/db_pydantic_models/supabase_models.py"
        log_info "  - TypeScript types: packages/supabase/types/generated.ts"
        log_info "  - API types: apps/web/app/types/api.ts"
    else
        log_error "Type generation failed for: ${failed_steps[*]}"
        exit 1
    fi
}

# Main execution
case "${1:-all}" in
    "orm")
        generate_orm_models
        ;;
    "pydantic")
        generate_pydantic_models
        ;;
    "typescript")
        generate_typescript_types
        ;;
    "api")
        generate_api_types
        ;;
    "all")
        generate_all_types
        ;;
    *)
        echo "Usage: $0 [orm|pydantic|typescript|api|all]"
        echo "  orm        - Generate SQLAlchemy ORM models"
        echo "  pydantic   - Generate Pydantic models from Supabase"
        echo "  typescript - Generate TypeScript types from Supabase"
        echo "  api        - Generate API TypeScript types from Pydantic"
        echo "  all        - Generate all types (default)"
        exit 1
        ;;
esac 