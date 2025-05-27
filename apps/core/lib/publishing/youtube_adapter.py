"""
YouTubeAdapter: Modular publishing adapter for YouTube integration.

Implements the publishing interface for uploading, updating, and managing videos on YouTube.
Ported from legacy video_processor/adapters/publishing/youtube.py.
"""

import http.client
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

# Google API client imports
import google.oauth2.credentials
import httplib2
from core.exceptions import PublishingError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from apps.core.lib.publishing.publishing_interface import PublishingInterface

logger = logging.getLogger(__name__)

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


class YouTubeAdapter(PublishingInterface):
    """
    YouTube adapter for publishing videos and managing metadata.
    """

    def __init__(
        self,
        client_secrets_file: str,
        oauth_token_file: str,
        scopes: Optional[List[str]] = None,
        api_service_name: str = "youtube",
        api_version: str = "v3",
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
            "https://www.googleapis.com/auth/youtube.force-ssl",
        ]
        self._api_service_name = api_service_name
        self._api_version = api_version
        self._youtube = None  # Will be set by tests or real API client in production
        self._initialize_youtube_client()

    def upload_video(self, video_file: str, metadata: Dict[str, Any]) -> str:
        """
        Upload a video to YouTube with metadata.
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not self._youtube:
            raise PublishingError("YouTube API client not initialized")

        if not video_file or not os.path.isfile(video_file):
            raise PublishingError(f"Video file does not exist: {video_file}")

        try:
            body = {
                "snippet": {
                    "title": metadata.get("title", "Untitled Video"),
                    "description": metadata.get("description", ""),
                    "tags": metadata.get("tags", []),
                    "categoryId": metadata.get("category_id", "22"),
                },
                "status": {
                    "privacyStatus": metadata.get("privacy_status", "private"),
                    "selfDeclaredMadeForKids": metadata.get("made_for_kids", False),
                },
            }

            media = MediaFileUpload(
                video_file,
                mimetype="video/*",
                resumable=True,
                chunksize=1024 * 1024 * 5,
            )

            insert_request = self._youtube.videos().insert(
                part=",".join(body.keys()), body=body, media_body=media
            )

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

    def _initialize_youtube_client(self) -> None:
        """
        Initialize the YouTube API client.
        """
        try:
            if not os.path.exists(self._oauth_token_file):
                raise PublishingError(
                    f"OAuth token file not found: {self._oauth_token_file}. "
                    "Please run the authentication flow first."
                )

            with open(self._oauth_token_file, "r") as token_file:
                token_data = json.load(token_file)

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

    def _execute_upload_with_retries(self, request):
        """
        Execute an upload request with retries for transient errors.
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

                max_sleep = 2**retry
                sleep_seconds = min(max_sleep, 60)
                logger.info(f"Sleeping {sleep_seconds} seconds before retrying...")
                time.sleep(sleep_seconds)

    def update_metadata(self, video_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an existing YouTube video.
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not self._youtube:
            raise PublishingError("YouTube API client not initialized")

        try:
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

            update_request = self._youtube.videos().update(
                part="snippet,status",
                body={"id": video_id, "snippet": snippet, "status": status},
            )

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
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not self._youtube:
            raise PublishingError("YouTube API client not initialized")

        try:
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
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not self._youtube:
            raise PublishingError("YouTube API client not initialized")

        try:
            self._youtube.videos().delete(id=video_id).execute()
            logger.info(f"Video with ID {video_id} deleted successfully")
            return True

        except HttpError as e:
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

    def get_video_url(self, video_id: str) -> str:
        """
        Get the public URL for a video on the publishing platform.
        """
        if not video_id:
            raise PublishingError("Invalid video_id for YouTube URL.")
        return f"https://www.youtube.com/watch?v={video_id}"

    def upload_caption(
        self, video_id: str, caption_file: str, language: str = "en"
    ) -> bool:
        """
        Upload a caption file for a video on the publishing platform.
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not self._youtube:
            raise PublishingError("YouTube API client not initialized")

        if not os.path.exists(caption_file):
            raise PublishingError(f"Caption file not found: {caption_file}")

        try:
            name, extension = os.path.splitext(caption_file)
            extension = extension.lower().strip(".")

            format_mapping = {
                "srt": "srt",
                "vtt": "webvtt",
                "sbv": "sbv",
                "sub": "sub",
                "ttml": "ttml",
            }

            if extension not in format_mapping:
                raise PublishingError(
                    f"Unsupported caption format: {extension}. "
                    f"Supported formats: {', '.join(format_mapping.keys())}"
                )

            caption_format = format_mapping[extension]

            caption_insert = self._youtube.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": language,
                        "name": f"{language.upper()} - {os.path.basename(name)}",
                    }
                },
                media_body=MediaFileUpload(
                    caption_file, mimetype=f"text/{extension}", resumable=True
                ),
            )

            caption_response = caption_insert.execute()
            logger.info(
                f"Caption uploaded successfully for video ID {video_id} in language {language}"
            )
            return True

        except HttpError as e:
            error_content = json.loads(e.content.decode("utf-8"))
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(f"HTTP error during caption upload: {error_message}")
            raise PublishingError(f"YouTube caption upload failed: {error_message}")

        except Exception as e:
            logger.error(f"Failed to upload caption: {str(e)}")
            raise PublishingError(f"YouTube caption upload failed: {str(e)}")

    def set_publishing_time(
        self, video_id: str, publish_at: Optional[str] = None
    ) -> bool:
        """
        Set the publishing time for a video on the platform.
        """
        if not self._youtube:
            self._initialize_youtube_client()

        if not self._youtube:
            raise PublishingError("YouTube API client not initialized")

        try:
            video_response = (
                self._youtube.videos().list(part="status", id=video_id).execute()
            )

            if not video_response.get("items"):
                raise PublishingError(f"Video with ID {video_id} not found")

            video_item = video_response["items"][0]
            status = video_item["status"]

            if publish_at is None:
                if "publishAt" in status:
                    del status["publishAt"]
                status["privacyStatus"] = "public"
            else:
                status["privacyStatus"] = "private"
                status["publishAt"] = publish_at

            update_request = self._youtube.videos().update(
                part="status", body={"id": video_id, "status": status}
            )

            update_response = update_request.execute()

            logger.info(
                f"Publishing time for video ID {video_id} set to: {publish_at or 'immediate'}"
            )
            return True

        except HttpError as e:
            error_content = json.loads(e.content.decode("utf-8"))
            error_message = error_content.get("error", {}).get("message", str(e))
            logger.error(f"HTTP error during publishing time update: {error_message}")
            raise PublishingError(
                f"YouTube publishing time update failed: {error_message}"
            )

        except Exception as e:
            logger.error(f"Failed to set publishing time: {str(e)}")
            raise PublishingError(f"YouTube publishing time update failed: {str(e)}")


# TODO: Add dependency injection registration and configuration as needed for modular backend.
