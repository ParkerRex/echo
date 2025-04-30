#!/bin/bash
# Script to run local tests for the Video Processor application

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

# Create test data directory if it doesn't exist
mkdir -p test_data

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    print_red "Docker is not installed. Please install it first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_red "Docker Compose is not installed. Please install it first."
    exit 1
fi

# Parse command line arguments
REBUILD=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD=true
            shift
            ;;
        --clean)
            CLEAN=true
            shift
            ;;
        *)
            print_red "Unknown option: $1"
            echo "Usage: $0 [--rebuild] [--clean]"
            exit 1
            ;;
    esac
done

# Clean up if requested
if [ "$CLEAN" = true ]; then
    print_yellow "Cleaning up Docker containers and volumes..."
    docker-compose down -v
    exit 0
fi

# Build and start the services
if [ "$REBUILD" = true ]; then
    print_yellow "Rebuilding and starting services..."
    docker-compose up --build -d
else
    print_yellow "Starting services..."
    docker-compose up -d
fi

# Wait for services to start
print_yellow "Waiting for services to start..."
sleep 5

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    print_red "Services failed to start. Check the logs with 'docker-compose logs'."
    exit 1
fi

print_green "Services are running!"
print_green "Video Processor: http://localhost:8080"
print_green "Mock GCS Service: http://localhost:8081"

# Show how to trigger a test event
print_blue "\nTo trigger a test event, run:"
print_blue "curl -X POST http://localhost:8081/trigger -H \"Content-Type: application/json\" -d '{\"bucket\":\"automations-videos\",\"name\":\"test-video.mp4\"}'"

# Show how to view logs
print_blue "\nTo view logs, run:"
print_blue "docker-compose logs -f"

print_green "\nPress Ctrl+C to exit..."
# Keep the script running to make it easy to stop with Ctrl+C
docker-compose logs -f
