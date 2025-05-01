# Local Testing Guide

> **Note:** For more comprehensive testing instructions, see the new [Testing Guide](TESTING_GUIDE.md) or the [Quick Test Guide](QUICK_TEST_GUIDE.md) for junior developers.

This guide explains how to test the Video Processor application locally before deploying to Cloud Run.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11 or later
- Google Cloud SDK (gcloud) installed and configured

## Testing Options

There are several ways to test the application locally:

1. **Docker Compose**: Run the full application stack with a mock GCS service
2. **Python Script**: Test specific GCS events with a Python script
3. **Dry Run Deployment**: Test the deployment process without actually deploying

## 1. Docker Compose Testing

The Docker Compose setup includes:
- The Video Processor application
- A mock GCS service that can send simulated events

### Running with Docker Compose

```bash
# Start the services
./scripts/local_test.sh

# Rebuild containers if needed
./scripts/local_test.sh --rebuild

# Clean up when done
./scripts/local_test.sh --clean
```

### Triggering Test Events

Once the services are running, you can trigger test events:

```bash
# Using curl
curl -X POST http://localhost:8081/trigger \
  -H "Content-Type: application/json" \
  -d '{"bucket":"automations-videos","name":"test-video.mp4"}'

# List available test files
curl http://localhost:8081/list-test-files
```

## 2. Python Script Testing

For more targeted testing, use the Python script:

```bash
# Make sure the Flask app is running
python -m video_processor.main

# In another terminal, send a test event
python scripts/test_locally.py --file test-video.mp4

# Or run both in one command
python scripts/test_locally.py --file test-video.mp4 --run-server
```

## 3. Dry Run Deployment

Test the deployment process without actually deploying:

```bash
# Run a dry deployment
./deploy.sh --dry-run

# Skip tests if needed
./deploy.sh --dry-run --skip-tests

# Get verbose output
./deploy.sh --dry-run --verbose
```

## Viewing Logs

### Local Logs

When running with Docker Compose:
```bash
docker-compose logs -f
```

When running the Python script:
```bash
# Logs are printed to the console
```

### Cloud Run Logs

After deployment, view logs with:
```bash
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor' \
  --limit=50 \
  --format='table(timestamp, severity, textPayload)' \
  --follow
```

## Troubleshooting

### Common Issues

1. **Container fails to start**
   - Check Docker logs: `docker-compose logs video-processor`
   - Verify port 8080 is not in use by another application

2. **Mock service can't connect to video processor**
   - Ensure both containers are running: `docker-compose ps`
   - Check network configuration in docker-compose.yml

3. **Deployment fails**
   - Check the logs in the `logs` directory
   - Run with `--verbose` flag for more detailed output

### Getting Help

If you encounter issues not covered here:
1. Check the deployment logs in the `logs` directory
2. Run the deployment with `--verbose` flag
3. Check Cloud Run logs for any errors after deployment
