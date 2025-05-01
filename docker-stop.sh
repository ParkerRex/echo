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
print_blue "   Stopping Automations Services"
print_blue "================================================"

# Parse command line arguments
REMOVE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --remove)
            REMOVE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--remove] [--help]"
            echo ""
            echo "Options:"
            echo "  --remove    Remove containers after stopping them"
            echo "  --help      Show this help message"
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

print_blue "Using command: $DOCKER_COMPOSE"

# Stop the services
if [ "$REMOVE" = true ]; then
    print_yellow "Stopping and removing containers..."
    $DOCKER_COMPOSE down
else
    print_yellow "Stopping containers..."
    $DOCKER_COMPOSE stop
fi

# Check if services stopped successfully
if [ $? -eq 0 ]; then
    print_green "✅ Services stopped successfully!"
else
    print_red "❌ Failed to stop services. Check the output above for errors."
    
    # Try to stop containers directly if docker-compose fails
    print_yellow "Attempting to stop containers directly..."
    
    # Get container IDs of our services
    backend_container=$(docker ps -q --filter "name=automations-backend")
    frontend_container=$(docker ps -q --filter "name=automations-frontend")
    mock_container=$(docker ps -q --filter "name=automations-mock-gcs")
    
    # Stop containers if they exist
    if [ ! -z "$backend_container" ]; then
        docker stop $backend_container
        print_green "Stopped backend container"
    fi
    
    if [ ! -z "$frontend_container" ]; then
        docker stop $frontend_container
        print_green "Stopped frontend container"
    fi
    
    if [ ! -z "$mock_container" ]; then
        docker stop $mock_container
        print_green "Stopped mock-gcs container"
    fi
fi

# Remind users how to start services again
print_blue "To start services again: ./docker-start.sh"