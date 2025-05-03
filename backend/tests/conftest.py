"""
Pytest configuration file with common fixtures for testing.
"""

import os
import subprocess
import tempfile
from unittest.mock import MagicMock

import pytest
from flask import Flask
from google.cloud.storage import Client as StorageClient

from video_processor.config import Settings
from video_processor.core.processors.audio import AudioProcessor
from video_processor.services.storage import (
    LocalStorageService,
    StorageService,
)


@pytest.fixture
def test_settings():
    """Create test settings with testing mode enabled."""
    return Settings(
        project_id="test-project",
        region="test-region",
        testing_mode=True,
        real_api_test=False,
        local_output=True,
        gcs_upload_bucket="test-bucket",
        ai_model="test-model",
        default_privacy_status="unlisted",
        port=8080,
        debug=True,
    )


@pytest.fixture
def mock_storage_client():
    """Mock for Google Cloud Storage client."""
    mock_client = MagicMock(spec=StorageClient)
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Set up the chain of mocks
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_bucket.copy_blob.return_value = mock_blob
    mock_blob.exists.return_value = True

    return mock_client, mock_bucket, mock_blob


@pytest.fixture
def mock_storage_service(mock_storage_client):
    """Mock for the StorageService interface."""
    mock_client, _, _ = mock_storage_client
    mock_service = MagicMock(spec=StorageService)

    # Configure methods to return appropriate values
    mock_service.download_file.return_value = "/tmp/test_video.mp4"
    mock_service.upload_file.return_value = "processed-daily/test_video/test_video.mp4"
    mock_service.upload_from_string.return_value = (
        "processed-daily/test_video/test_file.txt"
    )
    mock_service.read_file.return_value = b"test content"
    mock_service.read_text.return_value = "test content"
    mock_service.list_files.return_value = ["file1.txt", "file2.txt"]
    mock_service.file_exists.return_value = True
    mock_service.delete_file.return_value = True
    mock_service.move_file.return_value = True
    mock_service.get_signed_url.return_value = "https://test-signed-url.com"
    mock_service.get_metadata.return_value = {"name": "test_file", "size": 1000}

    return mock_service


@pytest.fixture
def mock_local_storage_service():
    """Create a local storage service for testing."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = LocalStorageService(base_path=tmp_dir)
        yield service


@pytest.fixture
def mock_generative_model():
    """Mock for Vertex AI GenerativeModel."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a mock response from Gemini API"
    mock_model.generate_content.return_value = mock_response

    return mock_model


@pytest.fixture
def sample_audio_file():
    """Create a temporary WAV file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Generate a simple test tone using ffmpeg
        subprocess.run(
            [
                "ffmpeg",
                "-y",  # Overwrite output files without asking
                "-f",
                "lavfi",  # Use libavfilter
                "-i",
                "sine=frequency=440:duration=1",  # Generate a 1-second 440Hz tone
                "-ar",
                "16000",  # Audio sample rate
                "-ac",
                "1",  # Mono audio
                temp_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        yield temp_path
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.fixture
def sample_video_file():
    """Create a temporary MP4 file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Generate a simple test video using ffmpeg
        subprocess.run(
            [
                "ffmpeg",
                "-y",  # Overwrite output files without asking
                "-f",
                "lavfi",  # Use libavfilter
                "-i",
                "sine=frequency=440:duration=1",  # Generate a 1-second 440Hz tone
                "-f",
                "lavfi",  # Use libavfilter for video
                "-i",
                "color=c=blue:s=320x240:d=1",  # Generate a 1-second blue screen
                "-c:a",
                "aac",  # Audio codec
                "-c:v",
                "h264",  # Video codec
                temp_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        yield temp_path
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.fixture
def audio_processor():
    """Create an AudioProcessor instance for testing."""
    return AudioProcessor(testing_mode=True)


@pytest.fixture
def mock_part():
    """Mock for Vertex AI Part object."""
    mock = MagicMock()
    mock.from_data.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_flask_app():
    """Create a test Flask app."""
    app = Flask(__name__)
    app.testing = True
    return app


@pytest.fixture
def mock_cloud_event():
    """Create a mock Cloud Event for testing."""
    event = MagicMock()
    event.data = {
        "bucket": "test-bucket",
        "name": "daily-raw/test_video.mp4",
        "contentType": "video/mp4",
        "size": "1000000",
    }
    return event


@pytest.fixture
def mock_youtube_credentials():
    """Mock for YouTube API credentials."""
    mock_creds = MagicMock()
    mock_creds.refresh.return_value = None
    return mock_creds


@pytest.fixture
def mock_youtube_service():
    """Mock for YouTube API service."""
    mock_service = MagicMock()
    mock_videos = MagicMock()
    mock_captions = MagicMock()

    # Set up the chain of mocks
    mock_service.videos.return_value = mock_videos
    mock_service.captions.return_value = mock_captions

    # Mock the insert methods
    mock_insert_request = MagicMock()
    mock_insert_request.next_chunk.return_value = (None, {"id": "test_video_id"})
    mock_videos.insert.return_value = mock_insert_request

    mock_caption_request = MagicMock()
    mock_caption_request.execute.return_value = {"id": "test_caption_id"}
    mock_captions.insert.return_value = mock_caption_request

    return mock_service


@pytest.fixture
def mock_secretmanager_client():
    """Mock for Secret Manager client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.payload.data.decode.return_value = "test_secret_value"
    mock_client.access_secret_version.return_value = mock_response
    return mock_client
