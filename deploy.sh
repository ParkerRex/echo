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
NC='\033[0m' # No Color

# Print with color
print_green() { echo -e "${GREEN}$1${NC}"; }
print_yellow() { echo -e "${YELLOW}$1${NC}"; }
print_red() { echo -e "${RED}$1${NC}"; }

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_red "gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_red "Docker is not installed. Please install it first."
    exit 1
fi

# Ensure we're authenticated to GCP
print_yellow "Checking GCP authentication..."
gcloud auth list --filter=status:ACTIVE --format="value(account)" || {
    print_red "Not authenticated to GCP. Please run 'gcloud auth login' first."
    exit 1
}

# Set the GCP project
print_yellow "Setting GCP project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Run tests before deployment
print_yellow "Running tests..."
cd video_processor
python -m pytest tests/test_youtube_uploader.py tests/test_generate_youtube_token.py tests/test_main.py -v || {
    print_red "Tests failed. Aborting deployment."
    exit 1
}
cd ..

# Deploy directly to Cloud Run using source code
print_yellow "Deploying to Cloud Run from source..."
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --concurrency 10

# Set up Eventarc trigger (if it doesn't exist)
print_yellow "Checking if Eventarc trigger exists..."
if ! gcloud eventarc triggers describe video-processor-trigger --location=${REGION} &> /dev/null; then
    print_yellow "Creating Eventarc trigger..."
    gcloud eventarc triggers create video-processor-trigger \
        --location=${REGION} \
        --destination-run-service=${SERVICE_NAME} \
        --destination-run-region=${REGION} \
        --event-filters="type=google.cloud.storage.object.v1.finalized" \
        --event-filters="bucket=automations-videos" \
        --service-account="${SERVICE_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
else
    print_green "Eventarc trigger already exists."
fi

print_green "Deployment completed successfully!"
print_green "Service URL: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')"
