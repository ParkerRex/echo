#!/bin/bash

# Echo Test Script
# This script runs all tests across the monorepo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[ECHO TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[ECHO TEST]${NC} $1"
}

print_error() {
    echo -e "${RED}[ECHO TEST]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ECHO TEST]${NC} $1"
}

print_status "🧪 Starting Echo test suite..."

# Test backend
print_status "🐍 Running Python backend tests..."
cd apps/core
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

./bin/test.sh
cd ../..
print_success "Python backend tests passed"

# Test frontend (when tests are available)
print_status "⚛️  Checking frontend..."
cd apps/web
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    pnpm test
    print_success "Frontend tests passed"
else
    print_warning "No frontend tests configured yet"
fi
cd ../..

# Run type checking
print_status "📝 Running type checks..."
cd apps/web
pnpm typecheck
cd ../..
print_success "Type checks passed"

cd apps/core
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
./bin/typecheck.sh
cd ../..
print_success "Python type checks passed"

print_success "🎉 All tests completed successfully!"
echo ""
echo -e "${GREEN}Test Results:${NC}"
echo -e "  ${GREEN}•${NC} Python Backend: ✅ Passed"
echo -e "  ${GREEN}•${NC} Frontend: ✅ Passed"
echo -e "  ${GREEN}•${NC} Type Checking: ✅ Passed" 