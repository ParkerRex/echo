import functions_framework
import os
import json
import logging
import time  # Add time for sleep
import random  # Add random for jitter
from google.cloud import secretmanager
from google.cloud import storage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow  # Might be needed for refresh token logic
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Configuration (Fetch from Secrets/Env Vars) ---
PROJECT_ID = "automations-457120"  # TODO: Consider fetching from env var

# Secret Manager IDs (Assumed names, need to be created)
DAILY_SECRETS = {
    "client_id": "youtube-daily-client-id",
    "client_secret": "youtube-daily-client-secret",
    "refresh_token": "youtube-daily-refresh-token",
}
MAIN_SECRETS = {
    "client_id": "youtube-main-client-id",
    "client_secret": "youtube-main-client-secret",
    "refresh_token": "youtube-refresh-token",
}

# YouTube API details
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# --- Helper Functions ---


def get_secret(secret_id, project_id, version_id="latest"):
    """Retrieves a secret version from Google Cloud Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.error(f"Failed to retrieve secret {secret_id}: {e}")
        raise


def get_youtube_credentials(secret_config):
    """Builds credentials object from stored refresh token."""
    try:
        client_id = get_secret(secret_config["client_id"], PROJECT_ID)
        client_secret = get_secret(secret_config["client_secret"], PROJECT_ID)
        refresh_token = get_secret(secret_config["refresh_token"], PROJECT_ID)

        credentials = Credentials(
            None,  # No access token initially
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )

        # Refresh the credentials to get an access token
        # This requires the google.auth.transport.requests library
        try:
            credentials.refresh(Request())
        except Exception as e:
            logging.error(f"Failed to refresh YouTube credentials: {e}")
            # Potentially indicates an expired/revoked refresh token
            # This requires manual re-authentication outside the function
            raise RuntimeError(
                "Could not refresh YouTube credentials. Refresh token might be invalid."
            )

        return credentials

    except Exception as e:
        logging.error(f"Error building YouTube credentials: {e}")
        raise


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        logging.info(
            f"Downloading gs://{bucket_name}/{source_blob_name} to {destination_file_name}"
        )
        blob.download_to_filename(destination_file_name)
        logging.info("Download complete.")
        return destination_file_name
    except Exception as e:
        logging.error(f"Failed to download blob {source_blob_name}: {e}")
        raise


def read_blob_content(bucket_name, source_blob_name):
    """Reads the content of a text blob from the bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        logging.info(f"Reading content from gs://{bucket_name}/{source_blob_name}")
        content = blob.download_as_text()
        logging.info(f"Read {len(content)} bytes.")
        return content
    except Exception as e:
        # Might fail if file doesn't exist, handle gracefully
        logging.warning(f"Could not read blob {source_blob_name}: {e}")
        return None


def upload_video(
    youtube,
    local_file_path,  # Now expects a local path
    title,
    description,
    privacy_status="private",
    category_id="22",  # Default: People & Blogs
    tags=[],
    max_retries=5,  # Max retries for 5xx errors
    initial_backoff=1,  # Initial wait time in seconds
    max_backoff=16,  # Max wait time
    backoff_factor=2,  # Factor to increase wait time
):
    """Uploads a video from a local file path to YouTube with retries."""
    logging.info(f"Starting upload for local file: {local_file_path}")

    body = dict(
        snippet=dict(
            title=title, description=description, tags=tags, categoryId=category_id
        ),
        status=dict(privacyStatus=privacy_status),
    )

    # Perform the upload
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(local_file_path, chunksize=-1, resumable=True),
    )

    response = None
    retries = 0
    backoff = initial_backoff
    while response is None:
        try:
            status, response = insert_request.next_chunk()
            if status:
                logging.info(f"Uploaded {int(status.progress() * 100)}%")
            # Reset retry count on successful chunk
            retries = 0
            backoff = initial_backoff
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                retries += 1
                if retries > max_retries:
                    logging.error(
                        f"An HTTP error {e.resp.status} occurred and max retries reached: {e.content}"
                    )
                    raise  # Max retries exceeded
                else:
                    # Exponential backoff with jitter
                    sleep_time = min(backoff + (random.random() * 0.5), max_backoff)
                    logging.warning(
                        f"HTTP error {e.resp.status} occurred (Attempt {retries}/{max_retries}). Retrying in {sleep_time:.2f}s..."
                    )
                    time.sleep(sleep_time)
                    backoff = min(backoff * backoff_factor, max_backoff)
                    # Continue loop to call next_chunk() again
            elif e.resp.status == 404:
                logging.error(
                    f"HTTP error 404 occurred: {e.content}. Upload session lost, requires restart."
                )
                raise  # Indicate restart needed
            else:
                # Non-retryable HTTP error
                logging.error(
                    f"An non-retryable HTTP error {e.resp.status} occurred: {e.content}"
                )
                raise  # Fail immediately
        except Exception as e:
            logging.error(f"An unexpected error occurred during upload chunk: {e}")
            raise  # Fail immediately for other errors

    logging.info(f"Upload successful! Video ID: {response.get('id')}")
    return response


def upload_captions(
    youtube,
    video_id,
    caption_file_path,
    language="en",
    max_retries=2,  # Fewer retries for captions
    initial_backoff=1,
    max_backoff=8,
    backoff_factor=2,
):
    """Uploads captions/subtitles with retries for transient errors."""
    logging.info(f"Uploading captions from {caption_file_path} for video ID {video_id}")

    insert_request = youtube.captions().insert(
        part="snippet",
        body={
            "snippet": {
                "videoId": video_id,
                "language": language,
                "name": f"{language} Captions",
                "isDraft": False,
            }
        },
        media_body=MediaFileUpload(caption_file_path),
        # Note: Resumable upload is default for media uploads
        # but explicit retry logic is needed for robustness.
    )

    response = None
    retries = 0
    backoff = initial_backoff
    while retries <= max_retries:
        try:
            response = insert_request.execute()
            logging.info(f"Caption upload successful! Caption ID: {response.get('id')}")
            return response  # Success
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504] and retries < max_retries:
                retries += 1
                sleep_time = min(backoff + (random.random() * 0.5), max_backoff)
                logging.warning(
                    f"HTTP error {e.resp.status} on caption upload (Attempt {retries}/{max_retries}). Retrying in {sleep_time:.2f}s..."
                )
                time.sleep(sleep_time)
                backoff = min(backoff * backoff_factor, max_backoff)
                # Continue loop to retry execute()
            else:
                # Max retries reached or non-retryable HTTP error
                logging.error(
                    f"An HTTP error {e.resp.status} occurred uploading captions: {e.content}. Max retries ({max_retries}) reached or error non-retryable."
                )
                return None  # Fail gracefully for captions
        except Exception as e:
            logging.error(f"An unexpected error occurred during caption upload: {e}")
            return None  # Fail gracefully

    # Should not be reached if logic is correct, but as a fallback:
    logging.error(f"Caption upload failed after {max_retries} retries.")
    return None


# --- Cloud Functions ---


@functions_framework.cloud_event
def upload_to_youtube_daily(cloud_event):
    """Triggers YouTube upload for the Daily channel based on GCS events."""
    try:
        data = cloud_event.data
        bucket_name = data.get("bucket")
        triggered_file_name = data.get(
            "name"
        )  # e.g., processed-daily/video_title/video.mp4 or description.txt

        logging.info(
            f"Received trigger for file: gs://{bucket_name}/{triggered_file_name}"
        )

        if not triggered_file_name or not triggered_file_name.startswith(
            "processed-daily/"
        ):
            logging.info("File is not in processed-daily/, skipping.")
            return

        # Determine the folder path from the triggered file
        folder_path = os.path.dirname(triggered_file_name) + "/"
        video_title = os.path.basename(
            folder_path.strip("/")
        )  # Extract title from folder name
        logging.info(f"Processing folder: {folder_path} for video title: {video_title}")

        # List files in the folder to find video and metadata
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket_name, prefix=folder_path)

        video_blob_name = None
        description_content = (
            f"Processed video: {video_title}\nUploaded via automation."  # Default
        )
        caption_blob_name = None
        chapters_content = None  # Placeholder for chapters

        for blob in blobs:
            blob_basename = os.path.basename(blob.name)
            if (
                blob_basename.lower().endswith((".mp4", ".mov", ".avi"))
                and video_blob_name is None
            ):
                video_blob_name = blob.name
                logging.info(f"Found video file: {video_blob_name}")
            elif blob_basename.lower() == "description.txt":
                desc = read_blob_content(bucket_name, blob.name)
                if desc:
                    description_content = desc
            elif (
                blob_basename.lower().endswith((".vtt", ".srt"))
                and caption_blob_name is None
            ):
                caption_blob_name = blob.name
                logging.info(f"Found caption file: {caption_blob_name}")
            elif blob_basename.lower() == "chapters.txt":
                chapters_content = read_blob_content(bucket_name, blob.name)
                # TODO: Add logic to format chapters_content into description

        # --- Validation: Proceed only if video file is found ---
        if video_blob_name is None:
            logging.warning(f"No video file found in folder {folder_path}. Exiting.")
            # If the trigger was for a metadata file, another trigger might come for the video.
            # If the trigger was for the video, but it's not found (??), something is wrong.
            return  # Stop processing

        # TODO: Add logic here to prevent multiple uploads if triggered by different files
        # e.g., check if video already uploaded via a marker file or API check?

        # --- Download Video File ---
        temp_video_path = f"/tmp/{os.path.basename(video_blob_name)}"
        download_blob(bucket_name, video_blob_name, temp_video_path)

        # --- Download Caption File (if exists) ---
        temp_caption_path = None
        if caption_blob_name:
            temp_caption_path = f"/tmp/{os.path.basename(caption_blob_name)}"
            download_blob(bucket_name, caption_blob_name, temp_caption_path)

        # --- Get Credentials & Build YouTube Service ---
        credentials = get_youtube_credentials(DAILY_SECRETS)
        youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

        # --- Perform Upload ---
        youtube_response = upload_video(
            youtube,
            temp_video_path,  # Use downloaded path
            video_title,
            description_content,  # Use content from description.txt
            privacy_status="private",  # Or 'public', 'unlisted'
        )

        # --- Upload Captions (if video upload succeeded and captions exist) ---
        if youtube_response and temp_caption_path:
            video_id = youtube_response.get("id")
            if video_id:
                upload_captions(youtube, video_id, temp_caption_path)
            else:
                logging.error(
                    "Could not get video ID from upload response to upload captions."
                )

        # --- Cleanup Temporary Files ---
        try:
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                logging.info(f"Cleaned up {temp_video_path}")
            if temp_caption_path and os.path.exists(temp_caption_path):
                os.remove(temp_caption_path)
                logging.info(f"Cleaned up {temp_caption_path}")
        except Exception as e:
            logging.warning(f"Error during temp file cleanup: {e}")

        logging.info("YouTube Daily upload function finished processing folder.")

    except Exception as e:
        logging.error(f"Error in upload_to_youtube_daily: {e}")
        # Depending on the error, might want to retry or send alert
        raise  # Re-raise to potentially trigger Cloud Functions retry mechanisms


@functions_framework.cloud_event
def upload_to_youtube_main(cloud_event):
    """Triggers YouTube upload for the Main channel based on GCS events."""
    try:
        data = cloud_event.data
        bucket_name = data.get("bucket")
        triggered_file_name = data.get("name")

        logging.info(
            f"Received trigger for Main channel: gs://{bucket_name}/{triggered_file_name}"
        )

        if not triggered_file_name or not triggered_file_name.startswith(
            "processed-main/"  # Check for main channel path
        ):
            logging.info("File is not in processed-main/, skipping.")
            return

        # Determine the folder path from the triggered file
        folder_path = os.path.dirname(triggered_file_name) + "/"
        video_title = os.path.basename(
            folder_path.strip("/")
        )  # Extract title from folder name
        logging.info(
            f"Processing folder (Main): {folder_path} for video title: {video_title}"
        )

        # List files in the folder to find video and metadata
        storage_client = storage.Client()
        blobs = storage_client.list_blobs(bucket_name, prefix=folder_path)

        video_blob_name = None
        description_content = (
            f"Processed video: {video_title}\nUploaded via automation."  # Default
        )
        caption_blob_name = None
        chapters_content = None  # Placeholder for chapters

        for blob in blobs:
            blob_basename = os.path.basename(blob.name)
            if (
                blob_basename.lower().endswith((".mp4", ".mov", ".avi"))
                and video_blob_name is None
            ):
                video_blob_name = blob.name
                logging.info(f"Found video file: {video_blob_name}")
            elif blob_basename.lower() == "description.txt":
                desc = read_blob_content(bucket_name, blob.name)
                if desc:
                    description_content = desc
            elif (
                blob_basename.lower().endswith((".vtt", ".srt"))
                and caption_blob_name is None
            ):
                caption_blob_name = blob.name
                logging.info(f"Found caption file: {caption_blob_name}")
            elif blob_basename.lower() == "chapters.txt":
                chapters_content = read_blob_content(bucket_name, blob.name)
                # TODO: Add logic to format chapters_content into description

        # --- Validation: Proceed only if video file is found ---
        if video_blob_name is None:
            logging.warning(f"No video file found in folder {folder_path}. Exiting.")
            return  # Stop processing

        # TODO: Add logic here to prevent multiple uploads if triggered by different files

        # --- Download Video File ---
        temp_video_path = f"/tmp/{os.path.basename(video_blob_name)}"
        download_blob(bucket_name, video_blob_name, temp_video_path)

        # --- Download Caption File (if exists) ---
        temp_caption_path = None
        if caption_blob_name:
            temp_caption_path = f"/tmp/{os.path.basename(caption_blob_name)}"
            download_blob(bucket_name, caption_blob_name, temp_caption_path)

        # --- Get Credentials & Build YouTube Service ---
        # Use MAIN_SECRETS for the main channel
        credentials = get_youtube_credentials(MAIN_SECRETS)
        youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

        # --- Perform Upload ---
        youtube_response = upload_video(
            youtube,
            temp_video_path,
            video_title,
            description_content,
            privacy_status="private",  # Or 'public', 'unlisted'
        )

        # --- Upload Captions (if video upload succeeded and captions exist) ---
        if youtube_response and temp_caption_path:
            video_id = youtube_response.get("id")
            if video_id:
                upload_captions(youtube, video_id, temp_caption_path)
            else:
                logging.error(
                    "Could not get video ID from upload response to upload captions."
                )

        # --- Cleanup Temporary Files ---
        try:
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                logging.info(f"Cleaned up {temp_video_path}")
            if temp_caption_path and os.path.exists(temp_caption_path):
                os.remove(temp_caption_path)
                logging.info(f"Cleaned up {temp_caption_path}")
        except Exception as e:
            logging.warning(f"Error during temp file cleanup: {e}")

        logging.info("YouTube Main upload function finished processing folder.")

    except Exception as e:
        logging.error(f"Error in upload_to_youtube_main: {e}")
        # Depending on the error, might want to retry or send alert
        raise  # Re-raise to potentially trigger Cloud Functions retry mechanisms
