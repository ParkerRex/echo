#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'
UNDERLINE='\033[4m'

# Configuration
PROJECT_ID="automations-457120"
REGION="us-east1"
SERVICE_NAME="video-processor"
BUCKET_NAME="automations-youtube-videos-2025"
REFRESH_INTERVAL=10 # seconds

# Function to clear screen and position cursor at top
clear_screen() {
  clear
  tput cup 0 0
}

# Function to display a header
display_header() {
  echo -e "${BOLD}${UNDERLINE}Cloud Run Service Monitor - Project: ${PROJECT_ID}${NC}"
  echo -e "${BOLD}Region: ${REGION} | Service: ${SERVICE_NAME} | Bucket: ${BUCKET_NAME}${NC}"
  echo -e "${BOLD}Press Ctrl+C to exit${NC}"
  echo ""
}

# Function to display service status
display_service_status() {
  echo -e "${BOLD}${UNDERLINE}Cloud Run Services:${NC}"

  # Get all services in the region
  services=$(gcloud run services list --region=${REGION} --project=${PROJECT_ID} --format="csv[no-heading](name,status.url,status.conditions[0].type,status.conditions[0].status)")

  echo -e "${BOLD}NAME                     STATUS    REQUESTS    ERRORS    URL${NC}"

  # Process each service
  while IFS=, read -r name url condition status; do
    # Get metrics for the service
    requests=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${name} AND resource.labels.location=${REGION} AND severity>=DEFAULT AND timestamp > '-10m'" --limit=1000 --format="value(timestamp)" --project=${PROJECT_ID} 2>/dev/null | wc -l)
    errors=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${name} AND resource.labels.location=${REGION} AND severity>=ERROR AND timestamp > '-10m'" --limit=1000 --format="value(timestamp)" --project=${PROJECT_ID} 2>/dev/null | wc -l)

    # Format status color
    if [[ "$condition" == "Ready" && "$status" == "True" ]]; then
      status_color="${GREEN}HEALTHY${NC}"
    else
      status_color="${RED}ERROR  ${NC}"
    fi

    # Display service info
    printf "%-25s %b %-10s %-9s %s\n" "$name" "$status_color" "$requests" "$errors" "$url"
  done <<< "$services"

  echo ""
}

# Function to display recent logs
display_recent_logs() {
  echo -e "${BOLD}${UNDERLINE}Recent Logs for ${SERVICE_NAME}:${NC}"

  logs=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME} AND resource.labels.location=${REGION} AND timestamp > '-10m'" --limit=10 --format="table(timestamp.date('%Y-%m-%d %H:%M:%S'), severity, textPayload)" --project=${PROJECT_ID} 2>/dev/null)

  if [[ -z "$logs" ]]; then
    echo "No logs found for this service in the last 10 minutes."
  else
    echo "$logs"
  fi

  echo ""
}

# Function to display Eventarc triggers
display_eventarc_triggers() {
  echo -e "${BOLD}${UNDERLINE}Eventarc Triggers:${NC}"

  triggers=$(gcloud eventarc triggers list --location=${REGION} --project=${PROJECT_ID} --format="csv[no-heading](name,destination.cloudRun.service,eventFilters[0].value,eventFilters[1].value)")

  echo -e "${BOLD}NAME                     SERVICE                  EVENT TYPE                  BUCKET${NC}"

  while IFS=, read -r name service event_type bucket; do
    printf "%-25s %-25s %-28s %s\n" "$name" "$service" "$event_type" "$bucket"
  done <<< "$triggers"

  echo ""
}

# Function to display bucket information
display_bucket_info() {
  echo -e "${BOLD}${UNDERLINE}GCS Bucket Contents:${NC}"

  echo -e "${BOLD}Daily Raw Files:${NC}"
  gsutil ls -l gs://${BUCKET_NAME}/daily-raw/ 2>/dev/null | head -n 5

  echo -e "\n${BOLD}Processed Daily Files:${NC}"
  gsutil ls -l gs://${BUCKET_NAME}/processed-daily/ 2>/dev/null | head -n 5

  echo ""
}

# Function to test the service by uploading a file
test_service() {
  echo -e "${BOLD}${UNDERLINE}Testing Service:${NC}"

  # Create a test file if it doesn't exist
  if [[ ! -f "test_data/daily-raw/test-video.mp4" ]]; then
    mkdir -p test_data/daily-raw
    # Download a sample MP4 file instead of creating random data
    echo "Downloading a sample MP4 file..."
    curl -s -o "test_data/daily-raw/test-video.mp4" "https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4"
    if [[ $? -eq 0 ]]; then
      echo "Created test file: test_data/daily-raw/test-video.mp4"
    else
      echo "Failed to download sample MP4. Creating a dummy file instead."
      # Create a minimal valid MP4 header
      echo -n -e '\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41\x00\x00\x00\x01moov' > "test_data/daily-raw/test-video.mp4"
    fi
  fi

  # Generate a unique filename
  timestamp=$(date +%Y%m%d-%H%M%S)
  test_filename="test-video-${timestamp}.mp4"

  echo "Uploading test file to gs://${BUCKET_NAME}/daily-raw/${test_filename}..."
  gsutil cp test_data/daily-raw/test-video.mp4 gs://${BUCKET_NAME}/daily-raw/${test_filename} 2>/dev/null

  if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}Test file uploaded successfully.${NC}"
    echo "Check logs in a few moments to see if the service processes the file."
  else
    echo -e "${RED}Failed to upload test file.${NC}"
  fi

  echo ""
}

# Main monitoring loop
while true; do
  clear_screen
  display_header
  display_service_status
  display_recent_logs
  display_eventarc_triggers
  display_bucket_info

  echo -e "${BOLD}Actions:${NC}"
  echo "1. Refresh (automatic in ${REFRESH_INTERVAL} seconds)"
  echo "2. Test service by uploading a file"
  echo "3. View detailed logs"
  echo "4. Exit"
  echo ""
  echo -e "${BOLD}Last updated: $(date)${NC}"

  # Non-blocking read with timeout
  read -t ${REFRESH_INTERVAL} -p "Enter option (1-4): " option

  case $option in
    2)
      test_service
      sleep 3
      ;;
    3)
      clear
      echo -e "${BOLD}Detailed logs for ${SERVICE_NAME}:${NC}"
      gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME} AND resource.labels.location=${REGION}" --limit=50 --format="table(timestamp.date('%Y-%m-%d %H:%M:%S'), severity, textPayload)" --project=${PROJECT_ID}
      echo ""
      read -p "Press Enter to continue..."
      ;;
    4)
      echo "Exiting..."
      exit 0
      ;;
    *)
      # Just refresh
      ;;
  esac
done
