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
pnpm gen:types:supabase
print_success "Types generated successfully"

# Build all applications using Turbo
print_status "🚀 Building all applications with Turbo..."
pnpm build
print_success "All applications built successfully"

# Run additional checks
print_status "🔍 Running quality checks..."
pnpm typecheck
pnpm lint
print_success "Quality checks passed"

print_success "🎉 Build completed successfully!"
echo ""
echo -e "${GREEN}Built applications:${NC}"
echo -e "  ${GREEN}•${NC} Frontend: apps/web/dist/"
echo -e "  ${GREEN}•${NC} Backend: Ready for deployment" 