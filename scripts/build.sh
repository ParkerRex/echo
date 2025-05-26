#!/bin/bash

# Echo Build Script
# This script builds all applications in the correct order

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[ECHO BUILD]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ECHO BUILD]${NC} $1"
}

print_error() {
    echo -e "${RED}[ECHO BUILD]${NC} $1"
}

print_status "🏗️  Starting Echo build process..."

# Generate types first
print_status "📝 Generating types..."
./scripts/generate-supabase-types.sh
print_success "Types generated successfully"

# Build frontend
print_status "⚛️  Building frontend..."
cd apps/web
pnpm build
cd ../..
print_success "Frontend built successfully"

# Python doesn't need a build step, but we can run checks
print_status "🐍 Checking Python backend..."
cd apps/core
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run type checking and linting
./bin/typecheck.sh
./bin/lint.sh
cd ../..
print_success "Python backend checks passed"

print_success "🎉 Build completed successfully!"
echo ""
echo -e "${GREEN}Built applications:${NC}"
echo -e "  ${GREEN}•${NC} Frontend: apps/web/dist/"
echo -e "  ${GREEN}•${NC} Backend: Ready for deployment" 