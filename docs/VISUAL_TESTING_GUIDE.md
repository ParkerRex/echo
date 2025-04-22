# Visual Testing Guide

This guide provides visual examples of what to expect when testing the Video Processor application.

## Local Testing with Python Script

### Step 1: Run the test script

Run this command in your terminal:
```bash
python scripts/test_locally.py --file test-video.mp4 --run-server
```

### Step 2: Expected output

You should see output similar to this:

```
2025-04-21 20:50:44,704 - __main__ - INFO - Starting Flask application...
 * Serving Flask app 'video_processor.main'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://10.0.0.74:8080
 * Restarting with watchdog (fsevents)
 * Debugger is active!
 * Debugger PIN: 313-277-782

2025-04-21 20:50:50,526 - root - INFO - Received CloudEvent: ID=test-event-id, Type=google.cloud.storage.object.v1.finalized, Source=//storage.googleapis.com/projects/_/buckets/automations-videos, Subject=objects/test-video.mp4
2025-04-21 20:50:50,526 - root - INFO - Processing gs://automations-videos/test-video.mp4
2025-04-21 20:50:50,526 - root - INFO - Processing video event for gs://automations-videos/test-video.mp4
2025-04-21 20:50:50,526 - root - INFO - Successfully processed gs://automations-videos/test-video.mp4
2025-04-21 20:50:50,526 - werkzeug - INFO - 127.0.0.1 - - [21/Apr/2025 20:50:50] "POST / HTTP/1.1" 204 -
```

### Step 3: What to look for

✅ **Success indicators:**
- The Flask app starts successfully
- You see "Received CloudEvent" in the logs
- You see "Processing gs://automations-videos/test-video.mp4"
- You see "Successfully processed" in the logs
- You see "204" status code (indicates success)

❌ **Failure indicators:**
- Error messages
- 400 or 500 status codes
- Missing "Successfully processed" message

## Dry Run Deployment

### Step 1: Run the dry deployment

Run this command:
```bash
./deploy.sh --dry-run --skip-tests
```

### Step 2: Expected output

You should see output similar to this:

```
=== DRY RUN MODE - No actual deployment will occur ===
2025-04-21 20:51:00 - Checking if gcloud CLI is installed...
2025-04-21 20:51:00 - ✓ gcloud CLI is installed
2025-04-21 20:51:00 - Checking if Docker is installed...
2025-04-21 20:51:00 - ✓ Docker is installed
2025-04-21 20:51:00 - Checking GCP authentication...
2025-04-21 20:51:02 - ✓ Authenticated to GCP as me@example.com
2025-04-21 20:51:02 - Setting GCP project to automations-457120...
2025-04-21 20:51:03 - ✓ GCP project set to automations-457120
2025-04-21 20:51:03 - Validating project configuration...
2025-04-21 20:51:03 - ✓ Project number: 598863037291
2025-04-21 20:51:03 - Checking if service account video-processor-sa@automations-457120.iam.gserviceaccount.com exists...
2025-04-21 20:51:04 - ✓ Service account exists
2025-04-21 20:51:04 - Skipping tests as requested
2025-04-21 20:51:04 - Building Docker image locally for testing...
2025-04-21 20:51:04 - [DRY RUN] Would build and test Docker image video-processor-local:20250421-205100
2025-04-21 20:51:04 - Deploying to Cloud Run from source...
2025-04-21 20:51:04 - [DRY RUN] Would deploy to Cloud Run with the following command:
2025-04-21 20:51:04 - gcloud run deploy video-processor --source . --platform managed --region us-central1 ...
2025-04-21 20:51:04 - Checking if Eventarc trigger exists...
2025-04-21 20:51:05 - Creating Eventarc trigger...
2025-04-21 20:51:05 - [DRY RUN] Would create Eventarc trigger
2025-04-21 20:51:05 - Fetching recent logs from Cloud Run service...
2025-04-21 20:51:05 - [DRY RUN] Would fetch logs from Cloud Run service

====== DEPLOYMENT SUMMARY ======
✓ Deployment completed successfully!
This was a dry run. No actual deployment was performed.
==============================
```

### Step 3: What to look for

✅ **Success indicators:**
- "DRY RUN MODE" message at the top
- Checkmarks (✓) next to each validation step
- "Deployment completed successfully!" message
- "This was a dry run" message

❌ **Failure indicators:**
- Error messages
- Missing checkmarks
- Script exits early

## Testing with Real API Calls

### Step 1: Run the real API test script

Run this command in your terminal:
```bash
python scripts/real_api_test.py --clean
```

### Step 2: Expected output

You should see output similar to this:

```
2025-04-21 21:30:00,000 - __main__ - INFO - Cleaning test environment...
2025-04-21 21:30:00,100 - __main__ - INFO - Copied test video file to test_data/daily-raw/Satya Nadella on Vibe Coding.mp4
2025-04-21 21:30:00,200 - __main__ - INFO - Processing video daily-raw/Satya Nadella on Vibe Coding.mp4 in bucket automations-videos with real API calls...
2025-04-21 21:30:00,300 - root - INFO - Processing video event for gs://automations-videos/daily-raw/Satya Nadella on Vibe Coding.mp4
2025-04-21 21:30:00,400 - root - INFO - Original base name: Satya Nadella on Vibe Coding
2025-04-21 21:30:00,500 - root - INFO - Normalized base name: Satya-Nadella-on-Vibe-Coding
2025-04-21 21:30:00,600 - root - INFO - Processed path: processed-daily/Satya-Nadella-on-Vibe-Coding/

... [processing logs] ...

2025-04-21 21:30:20,000 - root - INFO - Successfully processed gs://automations-videos/daily-raw/Satya Nadella on Vibe Coding.mp4
2025-04-21 21:30:20,100 - __main__ - INFO - Video processing completed successfully!
2025-04-21 21:30:20,200 - __main__ - INFO - Displaying outputs from test_data/processed-daily/Satya-Nadella-on-Vibe-Coding:

========================================
TRANSCRIPT.TXT
========================================
[Actual transcript content will appear here]

========================================
SUBTITLES.VTT
========================================
[Actual subtitles content will appear here]

... [other outputs] ...
```

### Step 3: What to look for

✅ **Success indicators:**
- "Video processing completed successfully!" message
- Actual content in the transcript, subtitles, and other outputs
- No error messages

❌ **Failure indicators:**
- Error messages
- Missing output files
- Empty or incomplete content in the output files

### Step 4: Examining the outputs

After running the test, you can find the output files in the `test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/` directory. These files contain the actual outputs from the Gemini API, not mock data.

## Docker-based Testing

### Step 1: Run the Docker test script

Run this command in your terminal:
```bash
./scripts/docker_test.sh --clean
```

### Step 2: Expected output

You should see output similar to this:

```
Cleaning test directories...
Copied Satya Nadella on Vibe Coding.mp4 to test_data/daily-raw/
Stopping any running containers...
Starting containers...
Waiting for containers to start...
Sending test event...
{
  "message": "Event sent for gs://automations-videos/daily-raw/Satya Nadella on Vibe Coding.mp4",
  "processor_response": "",
  "processor_status_code": 204,
  "success": true
}
Waiting for the video processor to process the event...
Checking test_data directory structure:
test_data
test_data/daily-raw
test_data/processed-daily
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding

Files in test_data/processed-daily:
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/chapters.txt
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/Satya Nadella on Vibe Coding.mp4
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/shownotes.txt
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/subtitles.vtt
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/title.txt
test_data/processed-daily/Satya-Nadella-on-Vibe-Coding/transcript.txt
Found processed directory: test_data/processed-daily/Satya-Nadella-on-Vibe-Coding
Found output file: transcript.txt
Content preview:
This is a mock transcript for testing purposes. It simulates what would be returned by the Gemini API in production.

... [other output files] ...

✅ Test passed! All outputs were generated correctly.
Stopping containers...
Test completed successfully!
```

### Step 3: What to look for

✅ **Success indicators:**
- "Test passed! All outputs were generated correctly." message
- Content previews for each output file
- "Test completed successfully!" message

❌ **Failure indicators:**
- Error messages
- Missing output files
- "Test failed!" message

## Viewing Cloud Run Logs

### Step 1: Run the logs command

```bash
gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=video-processor' \
  --limit=10 \
  --format='table(timestamp, severity, textPayload)'
```

### Step 2: Expected output

You should see a table of logs similar to this:

```
TIMESTAMP                  SEVERITY  TEXTPAYLOAD
2025-04-21T20:30:00.000Z  INFO      Starting server...
2025-04-21T20:30:01.000Z  INFO      Server started successfully
2025-04-21T20:35:10.000Z  INFO      Received CloudEvent: ID=123, Type=google.cloud.storage.object.v1.finalized
2025-04-21T20:35:10.100Z  INFO      Processing gs://automations-videos/example.mp4
2025-04-21T20:35:15.000Z  INFO      Successfully processed gs://automations-videos/example.mp4
```

### Step 3: What to look for

✅ **Success indicators:**
- "INFO" severity (not ERROR)
- "Received CloudEvent" messages
- "Successfully processed" messages

❌ **Failure indicators:**
- "ERROR" severity messages
- Stack traces
- Timeout messages

## Need Help?

If you're having trouble, refer to the [Testing Guide](TESTING_GUIDE.md) for more detailed instructions or ask a senior developer for assistance.
