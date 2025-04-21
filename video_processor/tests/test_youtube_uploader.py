"""
Tests for the youtube_uploader.py module.
"""

import sys
import os
import json
import pytest
import tempfile
from unittest.mock import patch, MagicMock, mock_open

# Add the root directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from video_processor import youtube_uploader


def test_get_secret(mock_secretmanager_client):
    """Test retrieving a secret from Secret Manager."""
    with patch(
        "video_processor.youtube_uploader.secretmanager.SecretManagerServiceClient",
        return_value=mock_secretmanager_client,
    ):
        # Call the function
        result = youtube_uploader.get_secret("test-secret", "test-project")

        # Verify the result
        assert result == "test_secret_value"

        # Verify the correct API call was made
        mock_secretmanager_client.access_secret_version.assert_called_once_with(
            request={
                "name": "projects/test-project/secrets/test-secret/versions/latest"
            }
        )


def test_get_youtube_credentials(mock_secretmanager_client, mock_youtube_credentials):
    """Test building YouTube credentials from stored secrets."""
    with patch(
        "video_processor.youtube_uploader.secretmanager.SecretManagerServiceClient",
        return_value=mock_secretmanager_client,
    ):
        with patch(
            "video_processor.youtube_uploader.Credentials", return_value=mock_youtube_credentials
        ):
            with patch("video_processor.youtube_uploader.Request") as mock_request:
                # Call the function
                result = youtube_uploader.get_youtube_credentials(
                    {
                        "client_id": "test-client-id",
                        "client_secret": "test-client-secret",
                        "refresh_token": "test-refresh-token",
                    }
                )

                # Verify the result
                assert result == mock_youtube_credentials

                # Verify the refresh method was called
                mock_youtube_credentials.refresh.assert_called_once()


def test_download_blob(mock_storage_client):
    """Test downloading a blob from GCS."""
    mock_client, mock_bucket, mock_blob = mock_storage_client

    with patch(
        "video_processor.youtube_uploader.storage.Client", return_value=mock_client
    ):
        # Call the function
        result = youtube_uploader.download_blob(
            "test-bucket", "test-blob", "/tmp/test-file"
        )

        # Verify the result
        assert result == "/tmp/test-file"

        # Verify the correct API calls were made
        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.download_to_filename.assert_called_once_with("/tmp/test-file")


def test_read_blob_content(mock_storage_client):
    """Test reading content from a blob in GCS."""
    mock_client, mock_bucket, mock_blob = mock_storage_client
    mock_blob.download_as_text.return_value = "test content"

    with patch(
        "video_processor.youtube_uploader.storage.Client", return_value=mock_client
    ):
        # Call the function
        result = youtube_uploader.read_blob_content("test-bucket", "test-blob")

        # Verify the result
        assert result == "test content"

        # Verify the correct API calls were made
        mock_client.bucket.assert_called_once_with("test-bucket")
        mock_bucket.blob.assert_called_once_with("test-blob")
        mock_blob.download_as_text.assert_called_once()


def test_upload_video(mock_youtube_service):
    """Test uploading a video to YouTube."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".mp4") as temp_file:
        with patch(
            "video_processor.youtube_uploader.MediaFileUpload"
        ) as mock_media_upload:
            # Call the function
            result = youtube_uploader.upload_video(
                mock_youtube_service, temp_file.name, "Test Title", "Test Description"
            )

            # Verify the result
            assert result == {"id": "test_video_id"}

            # Verify the correct API calls were made
            mock_youtube_service.videos.assert_called_once()
            mock_youtube_service.videos().insert.assert_called_once()
            mock_media_upload.assert_called_once_with(
                temp_file.name, chunksize=-1, resumable=True
            )


def test_upload_captions(mock_youtube_service):
    """Test uploading captions to YouTube."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".vtt") as temp_file:
        with patch(
            "video_processor.youtube_uploader.MediaFileUpload"
        ) as mock_media_upload:
            # Call the function
            result = youtube_uploader.upload_captions(
                mock_youtube_service, "test_video_id", temp_file.name
            )

            # Verify the result
            assert result == {"id": "test_caption_id"}

            # Verify the correct API calls were made
            mock_youtube_service.captions.assert_called_once()
            mock_youtube_service.captions().insert.assert_called_once()
            mock_media_upload.assert_called_once_with(temp_file.name)


def test_upload_to_youtube_daily(
    mock_cloud_event,
    mock_storage_client,
    mock_youtube_credentials,
    mock_youtube_service,
):
    """Test the Cloud Function for uploading to YouTube Daily channel."""
    mock_client, mock_bucket, mock_blob = mock_storage_client

    # Mock the list_blobs method to return a list of blobs
    mock_blobs = [
        MagicMock(name="processed-daily/test_video/video.mp4"),
        MagicMock(name="processed-daily/test_video/description.txt"),
        MagicMock(name="processed-daily/test_video/subtitles.vtt"),
    ]
    mock_blobs[0].name = "processed-daily/test_video/video.mp4"
    mock_blobs[1].name = "processed-daily/test_video/description.txt"
    mock_blobs[2].name = "processed-daily/test_video/subtitles.vtt"

    mock_client.list_blobs.return_value = mock_blobs

    # Set up the cloud event data
    mock_cloud_event.data = {
        "bucket": "test-bucket",
        "name": "processed-daily/test_video/video.mp4",
    }

    with patch(
        "video_processor.youtube_uploader.storage.Client", return_value=mock_client
    ):
        with patch(
            "video_processor.youtube_uploader.get_youtube_credentials",
            return_value=mock_youtube_credentials,
        ):
            with patch(
                "video_processor.youtube_uploader.build",
                return_value=mock_youtube_service,
            ):
                with patch(
                    "video_processor.youtube_uploader.download_blob"
                ) as mock_download:
                    with patch(
                        "video_processor.youtube_uploader.upload_video",
                        return_value={"id": "test_video_id"},
                    ):
                        with patch("video_processor.youtube_uploader.upload_captions"):
                            with patch(
                                "video_processor.youtube_uploader.os.path.exists", return_value=True
                            ):
                                with patch(
                                    "video_processor.youtube_uploader.os.remove"
                                ):
                                    # Call the function
                                    youtube_uploader.upload_to_youtube_daily(
                                        mock_cloud_event
                                    )

                                    # Verify the correct API calls were made
                                    mock_client.list_blobs.assert_called_once_with(
                                        "test-bucket",
                                        prefix="processed-daily/test_video/",
                                    )


def test_upload_to_youtube_main(
    mock_cloud_event,
    mock_storage_client,
    mock_youtube_credentials,
    mock_youtube_service,
):
    """Test the Cloud Function for uploading to YouTube Main channel."""
    mock_client, mock_bucket, mock_blob = mock_storage_client

    # Mock the list_blobs method to return a list of blobs
    mock_blobs = [
        MagicMock(name="processed-main/test_video/video.mp4"),
        MagicMock(name="processed-main/test_video/description.txt"),
        MagicMock(name="processed-main/test_video/subtitles.vtt"),
    ]
    mock_blobs[0].name = "processed-main/test_video/video.mp4"
    mock_blobs[1].name = "processed-main/test_video/description.txt"
    mock_blobs[2].name = "processed-main/test_video/subtitles.vtt"

    mock_client.list_blobs.return_value = mock_blobs

    # Set up the cloud event data
    mock_cloud_event.data = {
        "bucket": "test-bucket",
        "name": "processed-main/test_video/video.mp4",
    }

    with patch(
        "video_processor.youtube_uploader.storage.Client", return_value=mock_client
    ):
        with patch(
            "video_processor.youtube_uploader.get_youtube_credentials",
            return_value=mock_youtube_credentials,
        ):
            with patch(
                "video_processor.youtube_uploader.build",
                return_value=mock_youtube_service,
            ):
                with patch(
                    "video_processor.youtube_uploader.download_blob"
                ) as mock_download:
                    with patch(
                        "video_processor.youtube_uploader.upload_video",
                        return_value={"id": "test_video_id"},
                    ):
                        with patch("video_processor.youtube_uploader.upload_captions"):
                            with patch(
                                "video_processor.youtube_uploader.os.path.exists", return_value=True
                            ):
                                with patch(
                                    "video_processor.youtube_uploader.os.remove"
                                ):
                                    # Call the function
                                    youtube_uploader.upload_to_youtube_main(
                                        mock_cloud_event
                                    )

                                    # Verify the correct API calls were made
                                    mock_client.list_blobs.assert_called_once_with(
                                        "test-bucket",
                                        prefix="processed-main/test_video/",
                                    )
