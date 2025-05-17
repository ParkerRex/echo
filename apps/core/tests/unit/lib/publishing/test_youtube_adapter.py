"""
Unit tests for the YouTube adapter.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from core.exceptions import PublishingError
from googleapiclient.http import MediaFileUpload

from apps.core.lib.publishing.youtube_adapter import YouTubeAdapter


@pytest.fixture
def mock_credentials():
    """Create a mock OAuth credentials file for testing."""
    # Create a temporary file with mock credentials
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        credentials = {
            "token": "mock_token",
            "refresh_token": "mock_refresh_token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
        }
        json.dump(credentials, temp_file)
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up the temporary file
    os.unlink(temp_file_path)


@pytest.fixture
def mock_video_file():
    """Create a mock video file for testing."""
    # Create a temporary file as a mock video
    with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_file:
        temp_file.write(b"mock video content")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up the temporary file
    os.unlink(temp_file_path)


@pytest.fixture
def mock_youtube_api():
    """Mock the YouTube API client."""
    with patch("googleapiclient.discovery.build") as mock_build:
        # Create mock YouTube API
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Set up video responses
        mock_videos = MagicMock()
        mock_youtube.videos.return_value = mock_videos

        # Set up insert operation
        mock_insert = MagicMock()
        mock_videos.insert.return_value = mock_insert

        # Set up list operation
        mock_list = MagicMock()
        mock_videos.list.return_value = mock_list
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": "test_video_id",
                    "snippet": {
                        "title": "Test Video",
                        "description": "Test Description",
                        "tags": ["test", "video"],
                        "categoryId": "22",
                    },
                    "status": {
                        "privacyStatus": "private",
                        "selfDeclaredMadeForKids": False,
                    },
                    "processingDetails": {
                        "processingStatus": "processing",
                    },
                }
            ]
        }

        # Set up update operation
        mock_update = MagicMock()
        mock_videos.update.return_value = mock_update
        mock_update.execute.return_value = {"id": "test_video_id"}

        # Set up delete operation
        mock_delete = MagicMock()
        mock_videos.delete.return_value = mock_delete

        # Set up captions
        mock_captions = MagicMock()
        mock_youtube.captions.return_value = mock_captions

        # Set up caption insert
        mock_caption_insert = MagicMock()
        mock_captions.insert.return_value = mock_caption_insert
        mock_caption_insert.execute.return_value = {"id": "test_caption_id"}

        yield mock_youtube


@pytest.fixture
def youtube_adapter(mock_credentials, mock_youtube_api):
    """Create a YouTubeAdapter instance for testing."""
    # Mock the client_secrets_file which isn't used in our tests
    mock_client_secrets = "/path/to/client_secrets.json"

    # Create the adapter
    adapter = YouTubeAdapter(
        client_secrets_file=mock_client_secrets,
        oauth_token_file=mock_credentials,
    )

    # Ensure the YouTube API is initialized
    adapter._youtube = mock_youtube_api

    return adapter


class TestYouTubeAdapter:
    """Test cases for the YouTubeAdapter class."""

    def test_initialization(self, mock_credentials, mock_youtube_api):
        """Test adapter initialization."""
        # Mock the client_secrets_file which isn't used in our tests
        mock_client_secrets = "/path/to/client_secrets.json"

        # Create the adapter
        adapter = YouTubeAdapter(
            client_secrets_file=mock_client_secrets,
            oauth_token_file=mock_credentials,
        )

        # Check that the adapter was initialized correctly
        assert adapter._client_secrets_file == mock_client_secrets
        assert adapter._oauth_token_file == mock_credentials
        assert adapter._youtube is not None

    def test_upload_video(self, youtube_adapter, mock_video_file):
        """Test uploading a video."""
        # Set up the mock response for the video upload
        mock_insert_request = youtube_adapter._youtube.videos().insert()
        mock_insert_request.next_chunk.side_effect = [
            (None, None),  # First chunk (progress)
            (None, {"id": "test_video_id"}),  # Final chunk (completion)
        ]

        # Call the method
        video_id = youtube_adapter.upload_video(
            video_file=mock_video_file,
            metadata={
                "title": "Test Video",
                "description": "Test Description",
                "tags": ["test", "video"],
                "privacy_status": "private",
            },
        )

        # Check the result
        assert video_id == "test_video_id"

        # Verify the insert method was called
        youtube_adapter._youtube.videos().insert.assert_called()

        # Verify part and body parameters were passed as expected
        # This is less strict than assert_called_once_with but still verifies parameters
        args, kwargs = youtube_adapter._youtube.videos().insert.call_args
        assert "part" in kwargs
        assert "body" in kwargs
        assert "media_body" in kwargs

        # Check that the body contains expected metadata
        body = kwargs["body"]
        assert body["snippet"]["title"] == "Test Video"
        assert body["snippet"]["description"] == "Test Description"
        assert body["status"]["privacyStatus"] == "private"

    def test_update_metadata(self, youtube_adapter):
        """Test updating video metadata."""
        # Call the method
        result = youtube_adapter.update_metadata(
            video_id="test_video_id",
            metadata={
                "title": "Updated Title",
                "description": "Updated Description",
                "tags": ["updated", "tags"],
                "privacy_status": "public",
            },
        )

        # Check the result
        assert result is True

        # Verify the right methods were called
        youtube_adapter._youtube.videos().list.assert_called_once_with(
            part="snippet,status", id="test_video_id"
        )
        youtube_adapter._youtube.videos().update.assert_called_once()

    def test_get_upload_status(self, youtube_adapter):
        """Test getting upload status."""
        # Call the method
        status = youtube_adapter.get_upload_status(video_id="test_video_id")

        # Check the result
        assert status == "processing"

        # Verify the right methods were called
        youtube_adapter._youtube.videos().list.assert_called_once_with(
            part="processingDetails,status", id="test_video_id"
        )

    def test_delete_video(self, youtube_adapter):
        """Test deleting a video."""
        # Call the method
        result = youtube_adapter.delete_video(video_id="test_video_id")

        # Check the result
        assert result is True

        # Verify the right methods were called
        youtube_adapter._youtube.videos().delete.assert_called_once_with(
            id="test_video_id"
        )

    def test_get_video_url(self, youtube_adapter):
        """Test getting a video URL."""
        # Call the method
        url = youtube_adapter.get_video_url(video_id="test_video_id")

        # Check the result
        assert url == "https://www.youtube.com/watch?v=test_video_id"

    def test_upload_caption(self, youtube_adapter, mock_video_file):
        """Test uploading captions."""
        # Create a temporary caption file
        with tempfile.NamedTemporaryFile(
            suffix=".vtt", delete=False, mode="w"
        ) as temp_file:
            temp_file.write("WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest caption")
            caption_file = temp_file.name

        try:
            # Call the method
            result = youtube_adapter.upload_caption(
                video_id="test_video_id",
                caption_file=caption_file,
                language="en",
            )

            # Check the result
            assert result is True

            # Verify the right methods were called
            youtube_adapter._youtube.captions().insert.assert_called_once()
        finally:
            # Clean up
            os.unlink(caption_file)

    def test_set_publishing_time(self, youtube_adapter):
        """Test setting publishing time."""
        # Test immediate publishing
        result1 = youtube_adapter.set_publishing_time(
            video_id="test_video_id",
            publish_at=None,
        )
        assert result1 is True

        # Test scheduled publishing
        result2 = youtube_adapter.set_publishing_time(
            video_id="test_video_id",
            publish_at="2025-12-31T23:59:59Z",
        )
        assert result2 is True

        # Verify the right methods were called
        assert youtube_adapter._youtube.videos().list.call_count == 2
        assert youtube_adapter._youtube.videos().update.call_count == 2

    def test_error_handling(self, youtube_adapter):
        """Test error handling."""
        # Test missing video ID
        with pytest.raises(PublishingError):
            youtube_adapter.get_video_url(video_id=None)

        # Test file not found error
        with pytest.raises(PublishingError):
            youtube_adapter.upload_video(
                video_file="/nonexistent/file.mp4",
                metadata={},
            )
