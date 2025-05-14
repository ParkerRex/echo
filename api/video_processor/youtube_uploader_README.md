# YouTube Uploader

This component handles uploading processed videos to YouTube channels. It supports uploading to both a "Daily" channel and a "Main" channel.

## Overview

The YouTube uploader is implemented as a Cloud Function that is triggered by Cloud Storage events when a processed video is ready. It handles:

1. Detecting when a processed video is available
2. Downloading the video and associated metadata (description, captions, etc.)
3. Authenticating with the YouTube API
4. Uploading the video to the appropriate YouTube channel
5. Adding captions if available
6. Creating a marker file to prevent duplicate uploads

## Setup Instructions

### 1. Create OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create an OAuth 2.0 Client ID (Web application type)
3. Add `http://localhost:8080` as an authorized redirect URI
4. Download the JSON file and save it as `credentials/client_secret.json`

### 2. Generate OAuth Tokens

Run the token generator script for each channel:

```bash
# For the Daily channel
python -m video_processor.generate_youtube_token --channel daily

# For the Main channel
python -m video_processor.generate_youtube_token --channel main
```

Follow the prompts to authorize the application and obtain refresh tokens.

### 3. Set Up Secret Manager

Store the OAuth credentials in Secret Manager:

```bash
# Using the setup script
python -m video_processor.setup_youtube_secrets --client-secrets-file credentials/client_secret.json --refresh-token YOUR_REFRESH_TOKEN

# Or manually via the Google Cloud Console
# Go to: https://console.cloud.google.com/security/secret-manager
```

The following secrets need to be created:
- `youtube-daily-client-id`
- `youtube-daily-client-secret`
- `youtube-daily-refresh-token`
- `youtube-main-client-id`
- `youtube-main-client-secret`
- `youtube-refresh-token`

### 4. Deploy the Cloud Functions

The YouTube uploader is deployed as two separate Cloud Functions:

1. `upload-to-youtube-daily`: Triggered by files in the `processed-daily/` folder
2. `upload-to-youtube-main`: Triggered by files in the `processed-main/` folder

## Usage

The YouTube uploader is automatically triggered when a processed video is available. The workflow is:

1. Upload a raw video to the `daily-raw/` or `main-raw/` folder in the GCS bucket
2. The video processor processes the video and generates metadata
3. The processed files are stored in `processed-daily/` or `processed-main/`
4. The YouTube uploader is triggered and uploads the video to the appropriate channel

### Configuration Options

The YouTube uploader can be configured using environment variables:

- `DEFAULT_PRIVACY_STATUS`: Sets the default privacy status for uploaded videos (default: "unlisted")
  - Options: "private", "unlisted", "public"
  - Example: `DEFAULT_PRIVACY_STATUS=unlisted`

## File Structure

- `video_processor/youtube_uploader.py`: Main implementation of the YouTube uploader
- `video_processor/generate_youtube_token.py`: Script to generate OAuth tokens
- `video_processor/setup_youtube_secrets.py`: Script to set up Secret Manager secrets

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Check that the OAuth credentials are correctly stored in Secret Manager.
2. **Missing Files**: Ensure that the video file and metadata files are correctly named and stored in the GCS bucket.
3. **Duplicate Uploads**: The uploader creates a marker file to prevent duplicate uploads. If you need to force a re-upload, delete the `uploaded.marker` file in the processed folder.

### Logs

Check the Cloud Functions logs for detailed error messages:

```bash
gcloud functions logs read upload-to-youtube-daily
gcloud functions logs read upload-to-youtube-main
```

## Testing

Run the unit tests:

```bash
cd video_processor
python -m pytest tests/test_youtube_uploader.py -v
```
