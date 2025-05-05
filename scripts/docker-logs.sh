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
print_blue "   Viewing Automations Services Logs"
print_blue "================================================"

# Parse command line arguments
SERVICE=""
FOLLOW=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --no-follow)
            FOLLOW=false
            shift
            ;;
        --help)
            echo "Usage: $0 [--service SERVICE] [--no-follow] [--help]"
            echo ""
            echo "Options:"
            echo "  --service SERVICE   View logs for a specific service (backend, frontend, or mock-gcs)"
            echo "  --no-follow         Show logs without following (display and exit)"
            echo "  --help              Show this help message"
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

# View logs based on parameters
if [ -z "$SERVICE" ]; then
    # View all logs
    if [ "$FOLLOW" = true ]; then
        print_yellow "Viewing logs for all services (press Ctrl+C to exit)..."
        $DOCKER_COMPOSE logs -f
    else
        print_yellow "Viewing recent logs for all services..."
        $DOCKER_COMPOSE logs
    fi
else
    # View logs for specific service
    if [ "$FOLLOW" = true ]; then
        print_yellow "Viewing logs for $SERVICE service (press Ctrl+C to exit)..."
        $DOCKER_COMPOSE logs -f "$SERVICE"
    else
        print_yellow "Viewing recent logs for $SERVICE service..."
        $DOCKER_COMPOSE logs "$SERVICE"
    fi
fi