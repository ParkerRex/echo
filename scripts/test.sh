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

# Run all tests using Turbo
print_status "🚀 Running all tests with Turbo..."
pnpm test
print_success "All tests completed via Turbo"

# Run type checking
print_status "📝 Running type checks..."
pnpm typecheck
print_success "Type checks passed"

# Run linting
print_status "🔍 Running linting..."
pnpm lint
print_success "Linting passed"

print_success "🎉 All tests and checks completed successfully!"
echo ""
echo -e "${GREEN}Test Results:${NC}"
echo -e "  ${GREEN}•${NC} All Tests: ✅ Passed"
echo -e "  ${GREEN}•${NC} Type Checking: ✅ Passed"
echo -e "  ${GREEN}•${NC} Linting: ✅ Passed" 