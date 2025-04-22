#!/bin/bash
# Deployment script for the Video Processor application

# Exit on any error
set -e

# Configuration
PROJECT_ID="automations-457120"
REGION="us-central1"
SERVICE_NAME="video-processor"
ARTIFACT_REGISTRY="us-central1-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy"
IMAGE_NAME="${ARTIFACT_REGISTRY}/${SERVICE_NAME}"
IMAGE_TAG=$(date +%Y%m%d-%H%M%S)

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

# Log file for deployment
LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/deploy-$(date +%Y%m%d-%H%M%S).log"

# Create logs directory if it doesn't exist
mkdir -p ${LOG_DIR}

# Function to log messages to both console and log file
log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "${LOG_FILE}"
}

# Function to handle errors
handle_error() {
    print_red "\n====== ERROR ======"
    print_red "An error occurred during deployment at step: $1"
    print_red "Check the log file for details: ${LOG_FILE}"
    print_red "==================\n"
    exit 1
}

# Trap errors
trap 'handle_error "${BASH_COMMAND}"' ERR

# Parse command line arguments
DRY_RUN=false
SKIP_TESTS=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            print_red "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--skip-tests] [--verbose]"
            exit 1
            ;;
    esac
done

if [ "$DRY_RUN" = true ]; then
    print_blue "=== DRY RUN MODE - No actual deployment will occur ==="
fi

# Check if gcloud is installed
log "Checking if gcloud CLI is installed..."
if ! command -v gcloud &> /dev/null; then
    print_red "gcloud CLI is not installed. Please install it first."
    exit 1
fi
log "✓ gcloud CLI is installed"

# Check if docker is installed
log "Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
    print_red "Docker is not installed. Please install it first."
    exit 1
fi
log "✓ Docker is installed"

# Ensure we're authenticated to GCP
log "Checking GCP authentication..."
GCP_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
if [ -z "$GCP_ACCOUNT" ]; then
    print_red "Not authenticated to GCP. Please run 'gcloud auth login' first."
    exit 1
fi
log "✓ Authenticated to GCP as $GCP_ACCOUNT"

# Set the GCP project
log "Setting GCP project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}
log "✓ GCP project set to ${PROJECT_ID}"

# Validate project configuration
log "Validating project configuration..."
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
if [ -z "$PROJECT_NUMBER" ]; then
    print_red "Failed to get project number. Check if the project ID is correct."
    exit 1
fi
log "✓ Project number: ${PROJECT_NUMBER}"

# Check if the service account exists
SA_EMAIL="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
log "Checking if service account ${SA_EMAIL} exists..."
if ! gcloud iam service-accounts describe ${SA_EMAIL} &> /dev/null; then
    log "Service account does not exist. Creating it..."
    if [ "$DRY_RUN" = false ]; then
        gcloud iam service-accounts create "${SERVICE_NAME}-sa" \
            --display-name="${SERVICE_NAME} Service Account"
        log "✓ Service account created"
    else
        log "[DRY RUN] Would create service account ${SA_EMAIL}"
    fi
else
    log "✓ Service account exists"
fi

# Run tests before deployment
if [ "$SKIP_TESTS" = false ]; then
    log "Running tests..."
    cd video_processor
    python -m pytest tests/test_youtube_uploader.py tests/test_generate_youtube_token.py tests/test_main.py -v | tee -a "../${LOG_FILE}" || {
        print_red "Tests failed. Aborting deployment."
        cd ..
        exit 1
    }
    cd ..
    log "✓ All tests passed"
else
    log "Skipping tests as requested"
fi

# Build and test Docker image locally before deployment
log "Building Docker image locally for testing..."
LOCAL_IMAGE_NAME="${SERVICE_NAME}-local:${IMAGE_TAG}"
if [ "$DRY_RUN" = false ]; then
    docker build -t ${LOCAL_IMAGE_NAME} . | tee -a "${LOG_FILE}"
    log "✓ Docker image built successfully"

    # Run the Docker image locally for a quick test
    log "Running Docker image locally for a quick test..."
    CONTAINER_ID=$(docker run -d -p 8080:8080 ${LOCAL_IMAGE_NAME})
    sleep 5  # Give the container time to start

    # Check if the container is running
    if docker ps -q --filter "id=${CONTAINER_ID}" | grep -q .; then
        log "✓ Container is running"

        # Send a simple request to check if the app is responding
        log "Sending a test request to the container..."
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -q "200\|204\|404"; then
            log "✓ Container is responding to requests"
        else
            print_yellow "Warning: Container is not responding to requests. This might be expected if the app only accepts POST requests."
        fi

        # Stop and remove the container
        docker stop ${CONTAINER_ID} > /dev/null
        docker rm ${CONTAINER_ID} > /dev/null
        log "Stopped and removed test container"
    else
        print_red "Container failed to start. Check the Docker logs."
        docker logs ${CONTAINER_ID} | tee -a "${LOG_FILE}"
        exit 1
    fi
else
    log "[DRY RUN] Would build and test Docker image ${LOCAL_IMAGE_NAME}"
fi

# Deploy to Cloud Run
log "Deploying to Cloud Run from source..."
if [ "$DRY_RUN" = false ]; then
    # Use a deployment ID to track this deployment
    DEPLOY_ID=$(date +%Y%m%d-%H%M%S)
    log "Deployment ID: ${DEPLOY_ID}"

    # Deploy to Cloud Run
    gcloud run deploy ${SERVICE_NAME} \
        --source . \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600 \
        --concurrency 10 \
        --labels="deploy-id=${DEPLOY_ID}" | tee -a "${LOG_FILE}"

    log "✓ Deployment to Cloud Run completed"

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')
    log "✓ Service URL: ${SERVICE_URL}"

    # Check if the service is responding
    log "Checking if the service is responding..."
    if curl -s -o /dev/null -w "%{http_code}" ${SERVICE_URL} | grep -q "200\|204\|404"; then
        log "✓ Service is responding to requests"
    else
        print_yellow "Warning: Service is not responding to requests. This might be expected if the app only accepts POST requests."
    fi
else
    log "[DRY RUN] Would deploy to Cloud Run with the following command:"
    log "gcloud run deploy ${SERVICE_NAME} --source . --platform managed --region ${REGION} ..."
fi

# Set up Eventarc trigger (if it doesn't exist)
log "Checking if Eventarc trigger exists..."
if ! gcloud eventarc triggers describe video-processor-trigger --location=${REGION} &> /dev/null; then
    log "Creating Eventarc trigger..."
    if [ "$DRY_RUN" = false ]; then
        gcloud eventarc triggers create video-processor-trigger \
            --location=${REGION} \
            --destination-run-service=${SERVICE_NAME} \
            --destination-run-region=${REGION} \
            --event-filters="type=google.cloud.storage.object.v1.finalized" \
            --event-filters="bucket=automations-videos" \
            --service-account="${SA_EMAIL}" | tee -a "${LOG_FILE}"
        log "✓ Eventarc trigger created"
    else
        log "[DRY RUN] Would create Eventarc trigger"
    fi
else
    log "✓ Eventarc trigger already exists"
fi

# Check deployment logs
log "Fetching recent logs from Cloud Run service..."
if [ "$DRY_RUN" = false ]; then
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}" \
        --limit=10 \
        --format="table(timestamp, severity, textPayload)" | tee -a "${LOG_FILE}"
else
    log "[DRY RUN] Would fetch logs from Cloud Run service"
fi

print_green "\n====== DEPLOYMENT SUMMARY ======"
print_green "✓ Deployment completed successfully!"
if [ "$DRY_RUN" = false ]; then
    print_green "✓ Service URL: ${SERVICE_URL}"
    print_green "✓ Log file: ${LOG_FILE}"
    print_green "To view logs in real-time, run:"
    print_blue "  gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}' --limit=50 --format='table(timestamp, severity, textPayload)' --follow"
else
    print_blue "This was a dry run. No actual deployment was performed."
fi
print_green "==============================\n"
