#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colorful messages
print_green() { echo -e "${GREEN}$1${NC}"; }
print_blue() { echo -e "${BLUE}$1${NC}"; }
print_red() { echo -e "${RED}$1${NC}"; }
print_yellow() { echo -e "${YELLOW}$1${NC}"; }

# Show script banner
print_blue "================================================"
print_blue "   Running Automations Integration Tests"
print_blue "================================================"

# Parse command line arguments
VIDEO_FILE="Satya Nadella on Vibe Coding.mp4"
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --video)
            VIDEO_FILE="$2"
            shift 2
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--video VIDEO_FILE] [--clean] [--help]"
            echo ""
            echo "Options:"
            echo "  --video VIDEO_FILE   Use a specific video file for testing"
            echo "  --clean              Clean test directories before running"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            print_red "Unknown option: $1"
            echo "Use --help to see available options."
            exit 1
            ;;
    esac
done

# Determine the docker compose command (could be 'docker-compose' or 'docker compose')
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Create test directories
mkdir -p backend/test_data/daily-raw backend/test_data/processed-daily

# Clean test directories if requested
if [ "$CLEAN" = true ]; then
    print_yellow "Cleaning test directories..."
    rm -f backend/test_data/daily-raw/*
    rm -rf backend/test_data/processed-daily/*
fi

# Check if test video exists
if [ -f "backend/test_data/$VIDEO_FILE" ]; then
    print_green "Found test video: backend/test_data/$VIDEO_FILE"
    cp "backend/test_data/$VIDEO_FILE" "backend/test_data/daily-raw/"
else
    print_red "Test video file not found: backend/test_data/$VIDEO_FILE"
    exit 1
fi

# Start services with mock-gcs
print_yellow "Starting services with mock GCS for testing..."
$DOCKER_COMPOSE up -d backend frontend mock-gcs

# Wait for services to start
print_yellow "Waiting for services to start..."
sleep 5

# Send a test event
print_yellow "Sending test event for video: $VIDEO_FILE"
curl -X POST http://localhost:8081/trigger \
  -H "Content-Type: application/json" \
  -d "{\"bucket\":\"automations-videos\",\"name\":\"daily-raw/$VIDEO_FILE\"}"

# Wait for processing
print_yellow "Processing video... this may take a while"
sleep 20

# Check results
print_yellow "Checking for processed output files..."
processed_dir=$(find backend/test_data/processed-daily -mindepth 1 -maxdepth 1 -type d | head -1)

if [ -n "$processed_dir" ]; then
    print_green "Found processed directory: $processed_dir"
    
    # Define expected output files
    expected_files=("transcript.txt" "subtitles.vtt" "chapters.txt" "title.txt")
    
    # Check for each expected file
    all_found=true
    for file in "${expected_files[@]}"; do
        if [ -f "$processed_dir/$file" ]; then
            print_green "✅ Found output file: $file"
        else
            print_red "❌ Missing output file: $file"
            all_found=false
        fi
    done
    
    # Report test results
    if [ "$all_found" = true ]; then
        print_green "================================================"
        print_green "   ✅ All tests passed successfully!"
        print_green "================================================"
    else
        print_red "================================================"
        print_red "   ❌ Some tests failed"
        print_red "================================================"
    fi
else
    print_red "❌ No processed directory found after running the test"
    print_red "Test failed!"
fi

# Ask if user wants to stop services
read -p "Do you want to stop the services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_yellow "Stopping services..."
    $DOCKER_COMPOSE down
    print_green "Services stopped"
else
    print_yellow "Services left running."
    print_yellow "You can stop them later with: ./docker-stop.sh"
fi