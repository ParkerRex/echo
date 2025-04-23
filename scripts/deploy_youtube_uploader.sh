#!/bin/bash
# Script to deploy the YouTube uploader Cloud Functions

set -e  # Exit on error

# Configuration
PROJECT_ID="automations-457120"
REGION="us-east1"
BUCKET_NAME="automations-videos"
SERVICE_ACCOUNT="vps-automations@automations-457120.iam.gserviceaccount.com"
DEFAULT_PRIVACY_STATUS="unlisted"  # Options: private, unlisted, public

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Deploying YouTube Uploader Cloud Functions...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with gcloud. Please run 'gcloud auth login' first.${NC}"
    exit 1
fi

# Check if the project is set
CURRENT_PROJECT=$(gcloud config get-value project)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Setting project to $PROJECT_ID...${NC}"
    gcloud config set project $PROJECT_ID
fi

# Deploy the Daily channel uploader
echo -e "${YELLOW}Deploying upload-to-youtube-daily function...${NC}"
gcloud functions deploy upload-to-youtube-daily \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=upload_to_youtube_daily \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=$BUCKET_NAME" \
    --service-account=$SERVICE_ACCOUNT \
    --memory=512MB \
    --timeout=540s \
    --set-env-vars="DEFAULT_PRIVACY_STATUS=$DEFAULT_PRIVACY_STATUS"

# Deploy the Main channel uploader
echo -e "${YELLOW}Deploying upload-to-youtube-main function...${NC}"
gcloud functions deploy upload-to-youtube-main \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=upload_to_youtube_main \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=$BUCKET_NAME" \
    --service-account=$SERVICE_ACCOUNT \
    --memory=512MB \
    --timeout=540s \
    --set-env-vars="DEFAULT_PRIVACY_STATUS=$DEFAULT_PRIVACY_STATUS"

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${YELLOW}Note: Make sure the service account has the necessary permissions:${NC}"
echo "  - Secret Manager Secret Accessor"
echo "  - Storage Object Admin"
echo "  - YouTube Data API access"

echo -e "${GREEN}YouTube uploader functions are now deployed and will be triggered automatically when videos are processed.${NC}"
