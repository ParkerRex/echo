# Video Processor Testing Guide

This guide provides step-by-step instructions for testing the Video Processor application. It's designed for developers of all experience levels, with a focus on clarity for junior developers.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Testing](#local-testing)
   - [Method 1: Using the Python Script](#method-1-using-the-python-script)
   - [Method 2: Using Docker](#method-2-using-docker)
3. [Deployment Testing](#deployment-testing)
   - [Dry Run Deployment](#dry-run-deployment)
   - [Full Deployment](#full-deployment)
4. [Monitoring and Debugging](#monitoring-and-debugging)
   - [Viewing Local Logs](#viewing-local-logs)
   - [Viewing Cloud Run Logs](#viewing-cloud-run-logs)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin testing, make sure you have:

- Python 3.11 or later installed
- Docker installed (optional, for Docker-based testing)
- Google Cloud SDK (gcloud) installed and configured
- Access to the project's Google Cloud resources

To check if you have the required tools:

```bash
# Check Python version
python --version

# Check if Docker is installed
docker --version

# Check if gcloud is installed and configured
gcloud --version
gcloud auth list
```

## Local Testing

There are two main ways to test the application locally:

### Method 1: Using the Python Script

This is the simplest method and doesn't require Docker.

#### Step 1: Prepare your environment

```bash
# Make sure you're in the project root directory
cd /path/to/Automations

# Activate the virtual environment (if you have one)
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Run the local test script

```bash
# Make the script executable (only needed once)
chmod +x scripts/test_locally.py

# Run the Flask app and send a test event
python scripts/test_locally.py --file test-video.mp4 --run-server
```

This command:
1. Starts the Flask application
2. Creates a mock GCS event for "test-video.mp4"
3. Sends the event to the application
4. Shows the application's response

#### Step 3: Interpret the results

Look for these indicators of success:
- A 204 status code in the response
- Log messages showing "Successfully processed"
- No error messages

Example of successful output:
```
INFO - Sending request to http://localhost:8080/
INFO - Response status code: 204
INFO - Successfully processed gs://automations-videos/test-video.mp4
```

### Method 2: Using Docker

If you have Docker installed, you can test using Docker Compose.

#### Step 1: Prepare your environment

```bash
# Make sure you're in the project root directory
cd /path/to/Automations

# Make the script executable (only needed once)
chmod +x scripts/local_test.sh
```

#### Step 2: Start the Docker containers

```bash
# Start the services (first time or after changes)
./scripts/local_test.sh --rebuild

# For subsequent runs (no rebuild needed)
./scripts/local_test.sh
```

This command:
1. Builds and starts the Video Processor container
2. Starts a mock GCS service container
3. Shows logs from both services

#### Step 3: Send a test event

In a new terminal window:

```bash
# Send a test event to the mock GCS service
curl -X POST http://localhost:8081/trigger \
  -H "Content-Type: application/json" \
  -d '{"bucket":"automations-videos","name":"test-video.mp4"}'
```

#### Step 4: Clean up when done

```bash
# Stop and remove the containers
./scripts/local_test.sh --clean
```

### Method 3: Automated Docker Testing

For a fully automated test that verifies the entire workflow, use the Docker test script:

```bash
# Run the Docker test with default settings
./scripts/docker_test.sh

# Clean test directories before running
./scripts/docker_test.sh --clean

# Use a specific video file
./scripts/docker_test.sh --video "my-test-video.mp4"
```

This script will:
1. Set up the test environment
2. Start the Docker containers
3. Send a test event
4. Verify that the outputs are generated correctly
5. Clean up the containers

The test will pass if all expected output files are generated correctly.

### Method 4: Testing with Real API Calls

To test with real API calls and see the actual outputs, use the real API test script:

```bash
# Make the script executable (only needed once)
chmod +x scripts/real_api_test.py

# Run the test with default settings
python scripts/real_api_test.py

# Clean test directories before running
python scripts/real_api_test.py --clean

# Use a specific video file
python scripts/real_api_test.py --video "my-test-video.mp4"

# Only display outputs from a previous run
python scripts/real_api_test.py --display-only
```

This script will:
1. Set up the test environment
2. Process the video with real API calls (Gemini, GCS, etc.)
3. Display the actual outputs (transcript, subtitles, chapters, etc.)

> **Note:** This method requires proper Google Cloud authentication and will use actual API credits.

## Deployment Testing

Before deploying to production, you should test the deployment process.

### Dry Run Deployment

A dry run tests the deployment process without actually deploying.

```bash
# Run a dry deployment
./deploy.sh --dry-run

# If you want to skip running tests
./deploy.sh --dry-run --skip-tests
```

This command:
1. Checks all prerequisites
2. Validates your GCP configuration
3. Simulates building and testing the Docker image
4. Simulates deploying to Cloud Run
5. Shows what would happen during a real deployment

### Full Deployment

When you're ready to deploy:

```bash
# Deploy to Cloud Run
./deploy.sh

# If you want to skip running tests
./deploy.sh --skip-tests
```

This command:
1. Runs all tests (unless skipped)
2. Builds and tests the Docker image locally
3. Deploys to Cloud Run
4. Sets up the Eventarc trigger (if needed)
5. Shows the deployment logs and service URL

## Monitoring and Debugging

### Viewing Local Logs

When testing locally:

```bash
# If using the Python script
# Logs are printed directly to the console

# If using Docker
docker-compose logs -f
```

### Viewing Cloud Run Logs

After deployment:

```bash
# View recent logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor' \
  --limit=50 \
  --format='table(timestamp, severity, textPayload)'

# View logs in real-time
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor' \
  --limit=50 \
  --format='table(timestamp, severity, textPayload)' \
  --follow
```

You can also view logs in the Google Cloud Console:
1. Go to [Cloud Run](https://console.cloud.google.com/run)
2. Click on the "video-processor" service
3. Click on "Logs" tab

### Deployment Logs

Deployment logs are saved in the `logs` directory:

```bash
# List all deployment logs
ls -la logs/

# View the most recent deployment log
cat logs/deploy-*.log | less
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Module not found" errors

```bash
# Make sure you're in the project root directory
cd /path/to/Automations

# Install required packages
pip install -r requirements.txt
```

#### 2. Permission denied when running scripts

```bash
# Make scripts executable
chmod +x scripts/test_locally.py
chmod +x scripts/local_test.sh
chmod +x deploy.sh
```

#### 3. Docker container fails to start

```bash
# Check Docker logs
docker logs $(docker ps -q --filter "name=video-processor")

# Make sure port 8080 is not in use
lsof -i :8080
```

#### 4. Deployment fails

```bash
# Check the deployment logs
cat logs/deploy-*.log | grep ERROR

# Run with verbose flag
./deploy.sh --verbose
```

#### 5. GCP authentication issues

```bash
# Login to GCP
gcloud auth login

# Set the project
gcloud config set project automations-457120
```

### Getting Help

If you encounter issues not covered here:

1. Check the logs in the `logs` directory
2. Run commands with verbose flags
3. Ask a senior developer for assistance
4. Document the issue and solution for future reference
