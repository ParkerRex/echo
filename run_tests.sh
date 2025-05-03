#!/bin/bash

# Video Processor Test Runner Script
# Usage: ./run_tests.sh [unit|integration|e2e|all]

set -e

# Check if Python virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "Activating existing virtual environment..."
    source backend/venv/bin/activate
fi

# Default to running all tests if no argument provided
TEST_TYPE=${1:-all}

cd backend

case $TEST_TYPE in
    unit)
        echo "Running unit tests..."
        python -m pytest tests/unit/ -v
        ;;
    integration)
        echo "Running integration tests..."
        python -m pytest tests/integration/ -v
        ;;
    e2e)
        echo "Running end-to-end tests..."
        python -m pytest tests/e2e/ -v
        ;;
    coverage)
        echo "Running tests with coverage..."
        python -m pytest --cov=video_processor --cov-report=term --cov-report=html
        echo "Coverage report generated in htmlcov/ directory"
        ;;
    all)
        echo "Running all tests..."
        python -m pytest
        ;;
    *)
        echo "Invalid test type: $TEST_TYPE"
        echo "Usage: ./run_tests.sh [unit|integration|e2e|coverage|all]"
        exit 1
        ;;
esac

# Return to the original directory
cd ..

echo "Tests completed." 