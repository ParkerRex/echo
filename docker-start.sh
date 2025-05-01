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
print_blue "   Starting Automations Services with Docker"
print_blue "================================================"

# Parse command line arguments
REBUILD=false
MOCK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)
            REBUILD=true
            shift
            ;;
        --with-mock)
            MOCK=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--rebuild] [--with-mock] [--help]"
            echo ""
            echo "Options:"
            echo "  --rebuild     Rebuild all Docker images"
            echo "  --with-mock   Include mock GCS service for testing"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            print_red "Unknown option: $1"
            echo "Use --help to see available options."
            exit 1
            ;;
    esac
done

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    print_red "Docker is not installed. Please install it first."
    exit 1
fi

# Determine the docker compose command (could be 'docker-compose' or 'docker compose')
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

print_blue "Using command: $DOCKER_COMPOSE"

# Check for credentials
if [ ! -f "./credentials/service_account.json" ]; then
    print_yellow "Warning: Service account credentials not found at ./credentials/service_account.json"
    
    # Create credentials directory if it doesn't exist
    mkdir -p ./credentials
    
    # Ask if the user wants to continue with a mock credential file
    read -p "Do you want to continue with a mock credentials file? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_yellow "Creating mock credentials file for testing purposes..."
        echo '{"type":"service_account","project_id":"automations-457120"}' > ./credentials/service_account.json
    else
        print_red "Please add credentials to ./credentials/service_account.json and try again."
        exit 1
    fi
fi

# Determine services to start
if [ "$MOCK" = true ]; then
    print_blue "Starting services: backend, frontend, and mock-gcs"
    SERVICES="backend frontend mock-gcs"
else
    print_blue "Starting services: backend and frontend"
    SERVICES="backend frontend"
fi

# Start the services
if [ "$REBUILD" = true ]; then
    print_yellow "Rebuilding and starting services..."
    $DOCKER_COMPOSE up --build -d $SERVICES
else
    print_yellow "Starting services..."
    $DOCKER_COMPOSE up -d $SERVICES
fi

# Check if services started successfully
if [ $? -eq 0 ]; then
    print_green "✅ Services started successfully!"
    print_green "Frontend: http://localhost:3000"
    print_green "Backend:  http://localhost:8080"
    
    if [ "$MOCK" = true ]; then
        print_green "Mock GCS: http://localhost:8081"
        print_yellow "To trigger a test event, run:"
        print_yellow "curl -X POST http://localhost:8081/trigger \\"
        print_yellow "  -H \"Content-Type: application/json\" \\"
        print_yellow "  -d '{\"bucket\":\"automations-videos\",\"name\":\"test-video.mp4\"}'"
    fi
    
    print_blue "To view logs: ./docker-logs.sh"
    print_blue "To stop services: ./docker-stop.sh"
else
    print_red "❌ Failed to start services. Check the output above for errors."
    exit 1
fi