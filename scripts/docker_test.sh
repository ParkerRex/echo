#!/bin/bash
# Script to test the video processor using Docker

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color
print_green() { echo -e "${GREEN}$1${NC}"; }
print_yellow() { echo -e "${YELLOW}$1${NC}"; }
print_red() { echo -e "${RED}$1${NC}"; }
print_blue() { echo -e "${BLUE}$1${NC}"; }

# Default values
VIDEO_FILE="Satya Nadella on Vibe Coding.mp4"
CLEAN=false

# Parse command line arguments
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
        *)
            print_red "Unknown option: $1"
            echo "Usage: $0 [--video VIDEO_FILE] [--clean]"
            exit 1
            ;;
    esac
done

# Create test directories
mkdir -p test_data/daily-raw test_data/processed-daily

# Clean test directories if requested
if [ "$CLEAN" = true ]; then
    print_yellow "Cleaning test directories..."
    rm -f test_data/daily-raw/*
    rm -rf test_data/processed-daily/*
fi

# Copy the test video file to the daily-raw directory
if [ -f "test_data/$VIDEO_FILE" ]; then
    cp "test_data/$VIDEO_FILE" "test_data/daily-raw/"
    print_green "Copied $VIDEO_FILE to test_data/daily-raw/"
else
    print_red "Test video file test_data/$VIDEO_FILE does not exist!"
    exit 1
fi

# Stop any running containers
print_yellow "Stopping any running containers..."
docker-compose down

# Start the containers
print_yellow "Starting containers..."

# Check if service account file exists
mkdir -p credentials
if [ -f "credentials/service_account.json" ]; then
    print_green "Found service account credentials at credentials/service_account.json"
else
    print_red "Service account credentials not found at credentials/service_account.json"
    print_yellow "Creating a mock service account file for testing..."
    # Create a minimal mock service account file
    echo '{"type":"service_account","project_id":"automations-457120"}' > credentials/service_account.json
fi

docker-compose up -d

# Wait for the containers to start
print_yellow "Waiting for containers to start..."
sleep 5

# Send a test event to the mock GCS service
print_yellow "Sending test event..."
curl -X POST http://localhost:8081/trigger \
  -H "Content-Type: application/json" \
  -d "{\"bucket\":\"automations-videos\",\"name\":\"daily-raw/$VIDEO_FILE\"}"

# Wait for the video processor to process the event
print_yellow "Waiting for the video processor to process the event..."
sleep 10

# Check the test_data directory structure
print_yellow "Checking test_data directory structure:"
find test_data -type d | sort
echo ""
print_yellow "Files in test_data/processed-daily:"
find test_data/processed-daily -type f | sort

# Check if the processed directory exists
PROCESSED_DIR=$(find test_data/processed-daily -type d -depth 1 | head -1)
if [ -n "$PROCESSED_DIR" ]; then
    print_green "Found processed directory: $PROCESSED_DIR"

    # Check if the expected output files exist
    EXPECTED_FILES=(
        "transcript.txt"
        "subtitles.vtt"
        "shownotes.txt"
        "chapters.txt"
        "title.txt"
    )

    ALL_FILES_EXIST=true
    for FILE in "${EXPECTED_FILES[@]}"; do
        if [ -f "$PROCESSED_DIR/$FILE" ]; then
            print_green "Found output file: $FILE"
            # Print the first few lines of the file
            echo "Content preview:"
            head -n 5 "$PROCESSED_DIR/$FILE"
            echo ""
        else
            print_red "Expected output file $FILE does not exist!"
            ALL_FILES_EXIST=false
        fi
    done

    if [ "$ALL_FILES_EXIST" = true ]; then
        print_green "✅ Test passed! All outputs were generated correctly."
    else
        print_red "❌ Test failed! Some outputs were not generated correctly."
        exit 1
    fi
else
    print_red "❌ Test failed! No processed directory found."
    exit 1
fi

# Stop the containers
print_yellow "Stopping containers..."
docker-compose down

print_green "Test completed successfully!"
