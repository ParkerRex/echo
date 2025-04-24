# Testing the YouTube Uploader

This document provides instructions for testing the YouTube uploader functionality.

## Prerequisites

Before testing, make sure you have:

1. Set up the OAuth credentials and obtained refresh tokens
2. Stored the credentials in Secret Manager
3. Deployed the YouTube uploader Cloud Functions

## Testing Locally

### 1. Set Up Test Environment

```bash
# Create test directories if they don't exist
mkdir -p test_data/processed-daily/test-video
mkdir -p test_data/processed-main/test-video

# Set environment variables
export TESTING_MODE=true
export GOOGLE_APPLICATION_CREDENTIALS=./@credentials/service_account.json
```

### 2. Create Test Files

Create the necessary test files in the test directories:

```bash
# Create a test video file
echo "Test video content" > test_data/processed-daily/test-video/video.mp4

# Create a test description file
echo "Test video description" > test_data/processed-daily/test-video/description.txt

# Create a test chapters file
echo "00:00 - Introduction\n00:30 - Main Content\n01:00 - Conclusion" > test_data/processed-daily/test-video/chapters.txt

# Create a test subtitles file
echo "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nThis is a test subtitle." > test_data/processed-daily/test-video/subtitles.vtt
```

### 3. Run the YouTube Uploader Locally

```bash
# For the Daily channel
python -c "from video_processor.youtube_uploader import upload_to_youtube_daily; upload_to_youtube_daily({'data': {'bucket': 'test-bucket', 'name': 'processed-daily/test-video/video.mp4'}})"

# For the Main channel
python -c "from video_processor.youtube_uploader import upload_to_youtube_main; upload_to_youtube_main({'data': {'bucket': 'test-bucket', 'name': 'processed-main/test-video/video.mp4'}})"
```

## Testing in Production

### 1. Upload a Test Video

Upload a test video to the GCS bucket:

```bash
# For the Daily channel
gsutil cp test_video.mp4 gs://automations-videos/daily-raw/

# For the Main channel
gsutil cp test_video.mp4 gs://automations-videos/main-raw/
```

### 2. Monitor the Processing

1. The video processor will process the video and generate metadata
2. The processed files will be stored in the `processed-daily/` or `processed-main/` folder
3. The YouTube uploader will be triggered and upload the video to the appropriate channel

### 3. Check the Logs

```bash
# For the video processor
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=video-processor"

# For the YouTube uploader (Daily channel)
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=upload-to-youtube-daily"

# For the YouTube uploader (Main channel)
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=upload-to-youtube-main"
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Check that the OAuth credentials are correctly stored in Secret Manager.
2. **Missing Files**: Ensure that the video file and metadata files are correctly named and stored in the GCS bucket.
3. **Duplicate Uploads**: The uploader creates a marker file to prevent duplicate uploads. If you need to force a re-upload, delete the `uploaded.marker` file in the processed folder.

### Debugging Tips

1. Check the logs for detailed error messages
2. Verify that the service account has the necessary permissions
3. Test with the `TESTING_MODE=true` environment variable to use mock clients
4. Use the `--save` flag with the token generator to automatically save tokens to Secret Manager
