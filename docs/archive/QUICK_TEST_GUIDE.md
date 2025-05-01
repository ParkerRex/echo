# Quick Testing Guide for Video Processor

This guide provides the simplest way to test the Video Processor application locally and verify deployments.

## Local Testing (Quick Method)

### Option 1: Using Python Script

```bash
# Make sure you're in the project root directory
cd /path/to/Automations

# Activate the virtual environment (if you have one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Make the script executable (only needed once)
chmod +x scripts/test_locally.py

# Run the Flask app and send a test event in one command
python scripts/test_locally.py --file test-video.mp4 --run-server
```

Look for these messages in the output:
- "Response status code: 204" (indicates success)
- "Successfully processed gs://automations-videos/test-video.mp4"

### Option 2: Using Docker (Recommended for Quick Tests)

```bash
# Make the script executable (only needed once)
chmod +x scripts/docker_test.sh

# Run the automated Docker test
./scripts/docker_test.sh --clean
```

This will:
1. Set up the test environment
2. Run the Docker containers
3. Process a test video
4. Verify the outputs
5. Clean up automatically

Look for this message at the end:
- "✅ Test passed! All outputs were generated correctly."

### Option 3: Using Real API Calls (For Seeing Actual Outputs)

```bash
# Make the script executable (only needed once)
chmod +x scripts/real_api_test.py

# Run the test with real API calls
python scripts/real_api_test.py --clean
```

This will:
1. Process a test video with real API calls
2. Display the actual outputs (transcript, subtitles, etc.)
3. Save the outputs to the test_data directory

> **Note:** This uses actual API credits and requires Google Cloud authentication.

## Deployment Testing (Quick Method)

### Step 1: Run a dry deployment

```bash
# Make the script executable (only needed once)
chmod +x deploy.sh

# Run a dry deployment (no actual changes made)
./deploy.sh --dry-run --skip-tests
```

### Step 2: Check for any errors

The output should end with:
```
====== DEPLOYMENT SUMMARY ======
✓ Deployment completed successfully!
This was a dry run. No actual deployment was performed.
==============================
```

### Step 3: Deploy (when ready)

```bash
# Deploy to Cloud Run
./deploy.sh
```

## Checking Deployment Logs

After deployment, check the logs:

```bash
# View recent logs
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor' \
  --limit=10 \
  --format='table(timestamp, severity, textPayload)'
```

## Need More Help?

For more detailed instructions, see the full [Testing Guide](TESTING_GUIDE.md).
