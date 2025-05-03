"""
YouTube adapter for publishing videos.

This module provides an implementation of the PublishingInterface using
the YouTube Data API for uploading videos and managing metadata.
"""

import http.client
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import google.oauth2.credentials
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.domain.exceptions import PublishingError

# Configure logger
logger = logging.getLogger(__name__)

# YouTube API constants
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
RETRIABLE_EXCEPTIONS = (
    httplib2.HttpLib2Error,
    IOError,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)


class YouTubeAdapter(PublishingInterface):
    """YouTube adapter for publishing videos and managing metadata."""

    def __init__(
        self,
        client_secrets_file: str,
        oauth_token_file: str,
        scopes: Optional[List[str]] = None,
        api_service_name: str = YOUTUBE_API_SERVICE_NAME,
        api_version: str = YOUTUBE_API_VERSION,
    ):
        """
        Initialize the YouTube adapter.

        Args:
            client_secrets_file: Path to the client secrets file
            oauth_token_file: Path to the OAuth token file
            scopes: List of OAuth scopes (default: upload and read)
            api_service_name: YouTube API service name
            api_version: YouTube API version
        """
        self._client_secrets_file = client_secrets_file
        self._oauth_token_file = oauth_token_file
        self._scopes = scopes or [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ]
        self._api_service_name = api_service_name
        self._api_version = api_version
        self._youtube = None

        logger.info("Initializing YouTube adapter")
        self._initialize_youtube_client()

    def _initialize_youtube_client(self) -> None:
        """
        Initialize the YouTube API client.

        Raises:
            PublishingError: If client initialization fails
        """
        try:
            # Check if OAuth token file exists
            if not os.path.exists(self._oauth_token_file):
                raise PublishingError(
                    f"OAuth token file not found: {self._oauth_token_file}. "
                    "Please run the authentication flow first."
                )

            # Load credentials from token file
            with open(self._oauth_token_file, "r") as token_file:
                token_data = json.load(token_file)

            # Create credentials object
            credentials = google.oauth2.credentials.Credentials(
                token=token_data.get("token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri=token_data.get(
                    "token_uri", "https://oauth2.googleapis.com/token"
                ),
                client_id=token_data.get("client_id"),
                client_secret=token_data.get("client_secret"),
                scopes=self._scopes,
            )

            # Build YouTube API client
            self._youtube = build(
                self._api_service_name,
                self._api_version,
                credentials=credentials,
                cache_discovery=False,
            )

            logger.info("YouTube API client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {str(e)}")
            raise PublishingError(f"Failed to initialize YouTube API client: {str(e)}")

    def upload_video(self, video_file: str, metadata: Dict[str, Any]) -> str:
        """
        Upload a video to YouTube with metadata.

        Args:
            video_file: Path to the video file
            metadata: Dictionary containing video metadata:
                      - title: Video title
                      - description: Video description
                      - tags: List of tags
                      - category_id: YouTube category ID (default: 22 for People & Blogs)
                      - privacy_status: Privacy status (default: private)

        Returns:
            YouTube video ID of the uploaded video

        Raises:
            PublishingError: If the upload fails
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not os.path.exists(video_file):
            raise PublishingError(f"Video file not found: {video_file}")

        try:
            # Prepare video metadata
            body = {
                "snippet": {
                    "title": metadata.get("title", "Untitled Video"),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "categoryId": metadata.get(
                        "category_id", "22"
                    ),  # 22 = People & Blogs
                },
                "status": {
                    "privacyStatus": metadata.get("privacy_status", "private"),
                    "selfDeclaredMadeForKids": metadata.get("made_for_kids", False),
                },
            }

            # Configure media file upload
            media = MediaFileUpload(
                video_file,
                mimetype="video/*",
                resumable=True,
                chunksize=1024 * 1024 * 5,  # 5MB chunks
            )

            # Create upload request
            insert_request = self._youtube.videos().insert(
                part=",".join(body.keys()), body=body, media_body=media
            )

            # Execute the upload with progress tracking and retries
            video_id = self._execute_upload_with_retries(insert_request)

            logger.info(f"Video uploaded successfully with ID: {video_id}")
            return video_id

        except HttpError as e:
            error_content = json.loads(e.content.decode("utf-8"))
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(f"HTTP error during upload: {error_message}")
            raise PublishingError(f"YouTube upload failed: {error_message}")

        except Exception as e:
            logger.error(f"Failed to upload video: {str(e)}")
            raise PublishingError(f"YouTube upload failed: {str(e)}")

    def _execute_upload_with_retries(self, request):
        """
        Execute an upload request with retries for transient errors.

        Args:
            request: The YouTube API request object

        Returns:
            YouTube video ID

        Raises:
            PublishingError: If the upload fails after all retries
        """
        response = None
        error = None
        retry = 0
        video_id = None

        while response is None:
            try:
                logger.info(f"Uploading video (attempt {retry + 1}/{MAX_RETRIES})")
                status, response = request.next_chunk()

                if response is not None:
                    if "id" in response:
                        video_id = response["id"]
                        return video_id
                    else:
                        raise PublishingError(
                            f"YouTube upload failed, no video ID in response: {response}"
                        )

                # If status is available, log the progress
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")

            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = (
                        f"A retriable HTTP error {e.resp.status} occurred: {e.content}"
                    )
                else:
                    raise

            except RETRIABLE_EXCEPTIONS as e:
                error = f"A retriable error occurred: {e}"

            if error is not None:
                logger.warning(error)
                retry += 1

                if retry > MAX_RETRIES:
                    logger.error("Maximum retries exceeded")
                    raise PublishingError(
                        f"YouTube upload failed after {MAX_RETRIES} retries: {error}"
                    )

                # Exponential backoff: wait 2^retry seconds before retrying
                max_sleep = 2**retry
                sleep_seconds = min(max_sleep, 60)  # Cap at 60 seconds
                logger.info(f"Sleeping {sleep_seconds} seconds before retrying...")
                time.sleep(sleep_seconds)

    def update_metadata(self, video_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an existing YouTube video.

        Args:
            video_id: YouTube video ID
            metadata: Dictionary containing video metadata to update

        Returns:
            True if successful, False otherwise

        Raises:
            PublishingError: If the update fails
        """
        if not self._youtube:
            self._initialize_youtube_client()

        try:
            # Get current video data to merge with updates
            video_response = (
                self._youtube.videos()
                .list(part="snippet,status", id=video_id)
                .execute()
            )

            if not video_response.get("items"):
                raise PublishingError(f"Video with ID {video_id} not found")

            video_item = video_response["items"][0]
            snippet = video_item["snippet"]
            status = video_item["status"]

            # Update snippet fields if provided
            if "title" in metadata:
                snippet["title"] = metadata["title"]

            if "description" in metadata:
                snippet["description"] = metadata["description"]

            if "tags" in metadata:
                snippet["tags"] = metadata["tags"]

            if "category_id" in metadata:
                snippet["categoryId"] = metadata["category_id"]

            # Update status fields if provided
            if "privacy_status" in metadata:
                status["privacyStatus"] = metadata["privacy_status"]

            if "made_for_kids" in metadata:
                status["selfDeclaredMadeForKids"] = metadata["made_for_kids"]

            # Prepare update request
            update_request = self._youtube.videos().update(
                part="snippet,status",
                body={"id": video_id, "snippet": snippet, "status": status},
            )

            # Execute update request
            update_response = update_request.execute()

            logger.info(f"Video metadata updated successfully for ID: {video_id}")
            return True

        except HttpError as e:
            error_content = json.loads(e.content.decode("utf-8"))
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(f"HTTP error during metadata update: {error_message}")
            raise PublishingError(f"YouTube metadata update failed: {error_message}")

        except Exception as e:
            logger.error(f"Failed to update video metadata: {str(e)}")
            raise PublishingError(f"YouTube metadata update failed: {str(e)}")

    def get_upload_status(self, video_id: str) -> str:
        """
        Get the upload/processing status of a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Status string (e.g., "processing", "ready", "failed")

        Raises:
            PublishingError: If the status check fails
        """
        if not self._youtube:
            self._initialize_youtube_client()

        try:
            # Get video processing details
            processing_response = (
                self._youtube.videos()
                .list(part="processingDetails,status", id=video_id)
                .execute()
            )

            if not processing_response.get("items"):
                raise PublishingError(f"Video with ID {video_id} not found")

            video_item = processing_response["items"][0]
            processing_details = video_item.get("processingDetails", {})
            status = video_item.get("status", {})

            # Check if video is being processed
            if processing_details.get("processingStatus") == "processing":
                return "processing"

            # Check if video processing failed
            if processing_details.get("processingStatus") == "failed":
                return "failed"

            # Check upload status
            upload_status = status.get("uploadStatus")
            if upload_status == "uploaded" or upload_status == "processed":
                return "ready"
            elif upload_status == "failed":
                return "failed"

            # If we can't determine status, return the raw processing status
            return processing_details.get("processingStatus", "unknown")

        except HttpError as e:
            error_content = json.loads(e.content.decode("utf-8"))
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(f"HTTP error during status check: {error_message}")
            raise PublishingError(f"YouTube status check failed: {error_message}")

        except Exception as e:
            logger.error(f"Failed to get video status: {str(e)}")
            raise PublishingError(f"YouTube status check failed: {str(e)}")

    def delete_video(self, video_id: str) -> bool:
        """
        Delete a YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            True if successful, False otherwise

        Raises:
            PublishingError: If the deletion fails
        """
        if not self._youtube:
            self._initialize_youtube_client()

        try:
            # Delete the video
            self._youtube.videos().delete(id=video_id).execute()

            logger.info(f"Video with ID {video_id} deleted successfully")
            return True

        except HttpError as e:
            # Check if the video doesn't exist (404)
            if e.resp.status == 404:
                logger.warning(
                    f"Video with ID {video_id} not found, considering deletion successful"
                )
                return True

            error_content = json.loads(e.content.decode("utf-8"))
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(f"HTTP error during video deletion: {error_message}")
            raise PublishingError(f"YouTube video deletion failed: {error_message}")

        except Exception as e:
            logger.error(f"Failed to delete video: {str(e)}")
            raise PublishingError(f"YouTube video deletion failed: {str(e)}")
