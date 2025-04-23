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
REFRESH_INTERVAL=10 # seconds
LOG_LINES=10

# Function to clear screen and position cursor at top
clear_screen() {
  clear
  tput cup 0 0
}

# Function to display a header
display_header() {
  echo -e "${BOLD}${UNDERLINE}Cloud Run Service Monitor - Project: ${PROJECT_ID}${NC}"
  echo -e "${BOLD}Press Ctrl+C to exit${NC}"
  echo ""
}

# Function to display service status
display_service_status() {
  echo -e "${BOLD}${UNDERLINE}Cloud Run Services:${NC}"
  
  # Get all services
  services=$(gcloud run services list --project=${PROJECT_ID} --format="csv[no-heading](name,region,status.url,status.conditions[0].type,status.conditions[0].status)")
  
  echo -e "${BOLD}NAME                     REGION       STATUS    REQUESTS    ERRORS    CPU    MEMORY    URL${NC}"
  
  # Process each service
  while IFS=, read -r name region url condition status; do
    # Get metrics for the service
    requests=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${name} AND severity>=DEFAULT" --limit=1000 --format="value(timestamp)" --project=${PROJECT_ID} 2>/dev/null | wc -l)
    errors=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${name} AND severity>=ERROR" --limit=1000 --format="value(timestamp)" --project=${PROJECT_ID} 2>/dev/null | wc -l)
    
    # Format status color
    if [[ "$condition" == "Ready" && "$status" == "True" ]]; then
      status_color="${GREEN}HEALTHY${NC}"
    else
      status_color="${RED}ERROR  ${NC}"
    fi
    
    # Display service info
    printf "%-25s %-12s %b %-10s %-9s N/A    N/A      %s\n" "$name" "$region" "$status_color" "$requests" "$errors" "$url"
  done <<< "$services"
  
  echo ""
}

# Function to display recent logs
display_recent_logs() {
  local service=$1
  local region=$2
  
  echo -e "${BOLD}${UNDERLINE}Recent Logs for ${service} (${region}):${NC}"
  
  logs=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=${service}" --limit=${LOG_LINES} --format="table(timestamp.date('%Y-%m-%d %H:%M:%S'), severity, textPayload)" --project=${PROJECT_ID} 2>/dev/null)
  
  if [[ -z "$logs" ]]; then
    echo "No logs found for this service."
  else
    echo "$logs"
  fi
  
  echo ""
}

# Function to display bucket information
display_bucket_info() {
  echo -e "${BOLD}${UNDERLINE}GCS Buckets:${NC}"
  
  buckets=$(gsutil ls -p ${PROJECT_ID})
  
  for bucket in $buckets; do
    echo -e "${BOLD}$bucket${NC}"
    gsutil ls -l $bucket | head -n 5
    echo ""
  done
}

# Function to display Eventarc triggers
display_eventarc_triggers() {
  echo -e "${BOLD}${UNDERLINE}Eventarc Triggers:${NC}"
  
  triggers=$(gcloud eventarc triggers list --project=${PROJECT_ID} --format="csv[no-heading](name,transport.pubsub.topic,destination.run.service,location)")
  
  echo -e "${BOLD}NAME                     DESTINATION SERVICE       LOCATION${NC}"
  
  while IFS=, read -r name topic service location; do
    printf "%-25s %-25s %-12s\n" "$name" "$service" "$location"
  done <<< "$triggers"
  
  echo ""
}

# Main monitoring loop
while true; do
  clear_screen
  display_header
  display_service_status
  
  # Get the first service to show logs for
  first_service=$(gcloud run services list --project=${PROJECT_ID} --format="csv[no-heading](name,region)" | head -n 1)
  if [[ -n "$first_service" ]]; then
    IFS=, read -r service_name service_region <<< "$first_service"
    display_recent_logs "$service_name" "$service_region"
  fi
  
  display_eventarc_triggers
  
  echo -e "${BOLD}Last updated: $(date)${NC}"
  echo -e "${BOLD}Next update in ${REFRESH_INTERVAL} seconds...${NC}"
  
  sleep ${REFRESH_INTERVAL}
done
