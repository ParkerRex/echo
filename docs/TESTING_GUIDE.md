# 🧪 Video Processor Testing Guide

This guide provides step-by-step instructions for testing the Video Processor application. It covers the new Docker-based development workflow and testing methods.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
   - [Starting Services](#starting-services)
   - [Stopping Services](#stopping-services)
   - [Viewing Logs](#viewing-logs)
3. [Testing Methods](#testing-methods)
   - [Method 1: Docker-based Testing](#method-1-docker-based-testing) (Recommended)
   - [Method 2: Local Python Testing](#method-2-local-python-testing)
   - [Method 3: Real API Testing](#method-3-real-api-testing)
4. [Deployment Testing](#deployment-testing)
   - [Dry Run Deployment](#dry-run-deployment)
   - [Full Deployment](#full-deployment)
5. [Monitoring](#monitoring)
   - [Local Monitoring](#local-monitoring)
   - [Cloud Monitoring](#cloud-monitoring)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin testing, make sure you have:

- Docker and Docker Compose installed
- Python 3.11+ installed (for non-Docker testing)
- Google Cloud SDK (gcloud) installed and configured
- Access to the project's Google Cloud resources

To check if you have the required tools:

```bash
# Check Docker version
docker --version
docker compose version

# Check Python version (for non-Docker testing)
python --version

# Check gcloud configuration
gcloud --version
gcloud auth list
```

## Development Setup

Our new Docker-based workflow simplifies development and testing.

### Starting Services

To start both frontend and backend services:

```bash
# Start services with default settings
./docker-start.sh

# Rebuild containers if you've made changes to dependencies
./docker-start.sh --rebuild

# Include the mock GCS service for testing
./docker-start.sh --with-mock
```

When started successfully, you can access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8080
- Mock GCS (if enabled): http://localhost:8081

### Stopping Services

To stop all services:

```bash
# Stop but keep containers
./docker-stop.sh

# Stop and remove containers
./docker-stop.sh --remove
```

### Viewing Logs

To view logs from all services:

```bash
# View all logs
./docker-logs.sh

# View logs for a specific service
./docker-logs.sh --service backend
./docker-logs.sh --service frontend

# View logs without following (just display and exit)
./docker-logs.sh --no-follow
```

## Testing Methods

### Method 1: Docker-based Testing

This is the recommended method for comprehensive testing using our new Docker setup.

```bash
# Run the automated Docker test
./docker-test.sh

# Clean test directories before running
./docker-test.sh --clean

# Use a specific video file
./docker-test.sh --video "my-test-video.mp4"
```

This script will:
1. Set up the test environment
2. Start the Docker containers (backend, frontend, and mock GCS)
3. Send a test event
4. Verify that all outputs are generated correctly
5. Clean up the containers automatically

Success indicators:
- "✅ Test passed! All outputs were generated correctly."
- "Test completed successfully!"
- No error messages

### Method 2: Local Python Testing

For backend-only testing without Docker:

```bash
# Activate the virtual environment
source backend/venv/bin/activate  # On Windows: backend\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run the local test script
cd backend
python scripts/test_locally.py --file test-video.mp4 --run-server
```

This method is useful for quick backend testing without starting the full Docker environment.

### Method 3: Real API Testing

To test with real API calls and see actual AI-generated outputs:

```bash
# Activate the virtual environment
source backend/venv/bin/activate

# Run the real API test
cd backend
python scripts/real_api_test.py --clean
```

This script will use actual Gemini API calls to process the video and display the real outputs.

> **Note:** This method requires proper Google Cloud authentication and will use actual API credits.

## Deployment Testing

Before deploying to production, test the deployment process.

### Dry Run Deployment

```bash
# Run a dry deployment
./deploy.sh --dry-run

# Skip tests if needed
./deploy.sh --dry-run --skip-tests
```

This simulates the deployment process without making any actual changes.

### Full Deployment

When you're ready for actual deployment:

```bash
# Deploy to Cloud Run
./deploy.sh

# Skip tests if you've already tested
./deploy.sh --skip-tests
```

## Monitoring

### Local Monitoring

For local development, use the Docker logs commands:

```bash
# View all container logs
./docker-logs.sh

# View backend logs only
./docker-logs.sh --service backend
```

### Cloud Monitoring

After deployment, monitor your Cloud Run services:

```bash
# Use our custom monitoring script
./monitor-services.sh

# Or view logs directly with gcloud
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor' \
  --limit=50 \
  --format='table(timestamp, severity, textPayload)'
```

The `monitor-services.sh` script provides an interactive dashboard showing:
- Service status across all regions
- Recent logs
- Eventarc triggers
- GCS bucket contents

For more details on monitoring, see [Monitoring Guide](MONITORING_GUIDE.md).

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker container fails to start

```bash
# Check for port conflicts
lsof -i :3000  # Frontend port
lsof -i :8080  # Backend port

# Check Docker logs
./docker-logs.sh --service backend
```

#### 2. Missing service account credentials

```bash
# Ensure credentials exist
ls -la ./@credentials/service_account.json

# Create credentials directory if needed
mkdir -p ./@credentials
```

The `docker-start.sh` script will offer to create mock credentials for testing if needed.

#### 3. Frontend can't reach backend API

The frontend development server is configured to proxy API requests to the backend. Make sure both services are running.

#### 4. Firestore connection issues

Check that your Firebase configuration is correct in `frontend/firebase.ts`.

#### 5. GCP authentication issues

```bash
# Login to GCP
gcloud auth login

# Set the project
gcloud config set project automations-457120
```

### Getting Help

If you encounter issues not covered here:

1. Check the Docker logs for detailed error messages
2. Review the service status using `./monitor-services.sh`
3. Ask a senior developer for assistance
4. Document the issue and solution for future reference
