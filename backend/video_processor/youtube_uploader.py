import json
import logging
import os
import random  # Add random for jitter
import tempfile
import time  # Add time for sleep
import traceback

import functions_framework
from google.auth.transport.requests import Request
from google.cloud import secretmanager, storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Configuration (Fetch from Secrets/Env Vars) ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "automations-457120")

# Default privacy status for uploaded videos
DEFAULT_PRIVACY_STATUS = os.environ.get("DEFAULT_PRIVACY_STATUS", "unlisted")

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
            ) from e

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
            "Downloading gs://{}/{} to {}".format(
                bucket_name, source_blob_name, destination_file_name
            )
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


def check_upload_marker(bucket_name, folder_path):
    """Checks if a video has already been uploaded by looking for a marker file.

    Args:
        bucket_name: The GCS bucket name
        folder_path: The folder path in the bucket

    Returns:
        bool: True if the marker exists (video already uploaded), False otherwise
    """
    marker_path = folder_path + "uploaded.marker"
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(marker_path)
        exists = blob.exists()
        if exists:
            logging.info(f"Upload marker found at gs://{bucket_name}/{marker_path}")
        return exists
    except Exception as e:
        logging.warning(f"Error checking upload marker: {e}")
        return False


def create_upload_marker(bucket_name, folder_path, video_id):
    """Creates a marker file after successful upload to prevent duplicate uploads.

    Args:
        bucket_name: The GCS bucket name
        folder_path: The folder path in the bucket
        video_id: The YouTube video ID of the uploaded video

    Returns:
        bool: True if marker was created successfully, False otherwise
    """
    marker_path = folder_path + "uploaded.marker"
    marker_content = json.dumps(
        {
            "video_id": video_id,
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "uploaded",
        }
    )

    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(marker_path)
        blob.upload_from_string(marker_content)
        logging.info(f"Created upload marker at gs://{bucket_name}/{marker_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create upload marker: {e}")
        return False


def upload_video(
    youtube,
    local_file_path,  # Now expects a local path
    title,
    description,
    privacy_status=None,  # Will use DEFAULT_PRIVACY_STATUS if None
    category_id="22",  # Default: People & Blogs
    tags=None,
    max_retries=5,  # Max retries for 5xx errors
    initial_backoff=1,  # Initial wait time in seconds
    max_backoff=16,  # Max wait time
    backoff_factor=2,  # Factor to increase wait time
):
    """Uploads a video from a local file path to YouTube with retries."""
    if tags is None:
        tags = []
    logging.info(f"Starting upload for local file: {local_file_path}")

    # Use DEFAULT_PRIVACY_STATUS if privacy_status is None
    if privacy_status is None:
        privacy_status = DEFAULT_PRIVACY_STATUS

    logging.info(f"Setting video privacy status to: {privacy_status}")

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
                        "An HTTP error {} occurred and max retries reached: {}".format(
                            e.resp.status, e.content
                        )
                    )
                    raise  # Max retries exceeded
                else:
                    # Exponential backoff with jitter
                    sleep_time = min(backoff + (random.random() * 0.5), max_backoff)
                    logging.warning(
                        "HTTP error {} occurred (Attempt {}/{}). "
                        "Retrying in {:.2f}s...".format(
                            e.resp.status, retries, max_retries, sleep_time
                        )
                    )
                    time.sleep(sleep_time)
                    backoff = min(backoff * backoff_factor, max_backoff)
                    # Continue loop to call next_chunk() again
            elif e.resp.status == 404:
                logging.error(
                    "HTTP error 404 occurred: {}. "
                    "Upload session lost, requires restart.".format(e.content)
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
                    "Error on caption upload (Attempt {}/{}). "
                    "Retrying in {:.2f}s...".format(retries, max_retries, sleep_time)
                )
                time.sleep(sleep_time)
                backoff = min(backoff * backoff_factor, max_backoff)
                # Continue loop to retry execute()
            else:
                # Max retries reached or non-retryable HTTP error
                logging.error(
                    "Failed uploading captions: {}. "
                    "Max retries ({}) reached or error non-retryable.".format(
                        e.content, max_retries
                    )
                )
                return None  # Fail gracefully for captions
        except Exception as e:
            logging.error(f"An unexpected error occurred during caption upload: {e}")
            return None  # Fail gracefully

    # Should not be reached if logic is correct, but as a fallback:
    logging.error(f"Caption upload failed after {max_retries} retries.")
    return None


def get_video_folder_path(bucket_name, blob_name):
    """
    Get the folder path for the video files.

    Args:
        bucket_name: Name of the bucket
        blob_name: Name of the blob that triggered the event

    Returns:
        str: Folder path for the video files
    """
    # If the trigger was for a video file, get the folder it's in
    folder_path = "/".join(blob_name.split("/")[:-1])
    logging.info(f"Folder path: {folder_path}")
    return folder_path


def find_folder_files(storage_client, bucket_name, folder_path, expected_extensions):
    """
    Find files in a folder with specific extensions.

    Args:
        storage_client: Storage client
        bucket_name: Name of the bucket
        folder_path: Path to the folder
        expected_extensions: Dict mapping file types to extensions

    Returns:
        dict: Mapping of file types to blob names
    """
    # List all blobs in the folder
    blobs = storage_client.list_blobs(bucket_name, prefix=folder_path)

    # Find the necessary files
    found_files = {}
    for blob in blobs:
        for file_type, extension in expected_extensions.items():
            if blob.name.endswith(extension):
                found_files[file_type] = blob.name
                logging.info(f"Found {file_type}: {blob.name}")

    return found_files


def process_youtube_upload(cloud_event, channel_type):
    """
    Process YouTube upload for a specific channel type.

    Args:
        cloud_event: Cloud event that triggered the function
        channel_type: Type of channel ("daily" or "main")

    Returns:
        None
    """
    try:
        # Get the bucket and blob name from the cloud event
        bucket_name = cloud_event.data["bucket"]
        blob_name = cloud_event.data["name"]
        logging.info(
            f"Processing {channel_type} channel upload: gs://{bucket_name}/{blob_name}"
        )

        # Skip if this is not a video file
        if not blob_name.endswith(".mp4"):
            logging.info(f"Skipping non-video file: {blob_name}")
            return

        # Make sure it's in the correct folder
        prefix = f"processed-{channel_type}/"
        if not blob_name.startswith(prefix):
            logging.info(f"Skipping file not in {prefix} folder: {blob_name}")
            return

        # Get the folder path for the video files
        folder_path = get_video_folder_path(bucket_name, blob_name)

        # Create a storage client
        storage_client = storage.Client()

        # Find video, description, and subtitles files
        expected_extensions = {
            "video": "video.mp4",
            "description": "description.txt",
            "subtitles": "subtitles.vtt",
        }

        found_files = find_folder_files(
            storage_client, bucket_name, folder_path, expected_extensions
        )

        # Make sure we have the video file
        video_blob_name = found_files.get("video")
        if video_blob_name is None:
            logging.warning(f"No video file found in folder {folder_path}. Exiting.")
            # If the trigger was for a metadata file, another trigger might
            # come for the video.
            # If the trigger was for the video, but it's not found (??),
            # something is wrong.
            return  # Stop processing

        # We need at minimum a video file and description
        description_blob_name = found_files.get("description")
        if description_blob_name is None:
            logging.warning(
                f"No description file found in folder {folder_path}. Exiting."
            )
            return  # Stop processing

        # Get the description text
        description_text = read_blob_content(bucket_name, description_blob_name)

        # Parse the description - first line is the title, rest is description
        lines = description_text.strip().split("\n")
        video_title = lines[0]
        video_description = "\n".join(lines[1:]) if len(lines) > 1 else ""

        # Get YouTube credentials
        secret_prefix = f"youtube-{channel_type}"
        youtube_creds = {
            "client_id": get_secret(f"{secret_prefix}-client-id", PROJECT_ID),
            "client_secret": get_secret(f"{secret_prefix}-client-secret", PROJECT_ID),
            "refresh_token": get_secret(f"{secret_prefix}-refresh-token", PROJECT_ID),
        }

        credentials = get_youtube_credentials(youtube_creds)

        # Create a YouTube API client
        youtube = build("youtube", "v3", credentials=credentials)

        # Download the video file
        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, "video.mp4")
            download_blob(bucket_name, video_blob_name, video_path)

            # Upload the video to YouTube
            upload_response = upload_video(
                youtube, video_path, video_title, video_description
            )

            # Get the video ID from the response
            if "id" in upload_response:
                video_id = upload_response["id"]
                logging.info(
                    "Uploaded video to YouTube {} channel. Video ID: {}".format(
                        channel_type, video_id
                    )
                )

                # Upload captions if available
                subtitles_blob_name = found_files.get("subtitles")
                if subtitles_blob_name:
                    subtitles_path = os.path.join(temp_dir, "subtitles.vtt")
                    download_blob(bucket_name, subtitles_blob_name, subtitles_path)

                    # Upload captions to YouTube
                    captions_response = upload_captions(
                        youtube, video_id, subtitles_path
                    )
                    logging.info(
                        "Uploaded captions to YouTube. Caption ID: {}".format(
                            captions_response.get("id")
                        )
                    )
                else:
                    logging.info("No subtitles file found. Skipping captions upload.")

                # Clean up temporary files
                if os.path.exists(video_path):
                    os.remove(video_path)
                if subtitles_blob_name and os.path.exists(subtitles_path):
                    os.remove(subtitles_path)
            else:
                logging.error(
                    "Could not get video ID from upload response. "
                    "Upload may have failed."
                )

    except Exception as e:
        logging.error(f"Error in upload_to_youtube_{channel_type}: {e}")
        traceback.print_exc()
        raise


@functions_framework.cloud_event
def upload_to_youtube_daily(cloud_event):
    """Triggers YouTube upload for the Daily channel based on GCS events."""
    process_youtube_upload(cloud_event, "daily")


@functions_framework.cloud_event
def upload_to_youtube_main(cloud_event):
    """Triggers YouTube upload for the Main channel based on GCS events."""
    process_youtube_upload(cloud_event, "main")
