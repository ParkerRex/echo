"""
Pytest configuration file with common fixtures for testing.
"""

import os
import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from google.cloud.storage import Client as StorageClient

# Set environment variables for testing
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"


# Mock Google auth for all tests
@pytest.fixture(autouse=True, scope="session")
def mock_google_auth():
    """Mock Google Cloud authentication for all tests."""
    with patch("google.auth.default", return_value=(None, "test-project")):
        yield


@pytest.fixture
def test_settings():
    """Create test settings with testing mode enabled."""
    from video_processor.infrastructure.config.settings import Settings

    return Settings(
        project_id="test-project",
        region="test-region",
        testing_mode=True,
        gcs_upload_bucket="test-bucket",
        ai_model="test-model",
        default_privacy_status="unlisted",
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
def storage_adapter():
    """Mock for the StorageAdapter interface."""
    from video_processor.application.interfaces.storage import StorageInterface

    mock_adapter = MagicMock(spec=StorageInterface)

    # Configure methods to return appropriate values
    mock_adapter.upload_file.return_value = "processed/test_video.mp4"
    mock_adapter.download_file.return_value = "/tmp/test_video.mp4"
    mock_adapter.delete_file.return_value = True
    mock_adapter.get_public_url.return_value = (
        "https://storage.googleapis.com/test-bucket/test_video.mp4"
    )
    mock_adapter.get_signed_url.return_value = (
        "https://storage.googleapis.com/test-bucket/test_video.mp4?token=abc123"
    )

    return mock_adapter


@pytest.fixture
def ai_adapter():
    """Mock for AIServiceInterface."""
    from video_processor.application.interfaces.ai import AIServiceInterface

    mock_ai = MagicMock(spec=AIServiceInterface)

    # Configure methods to return appropriate values
    mock_ai.generate_transcript.return_value = "This is a test transcript."
    mock_ai.generate_metadata.return_value = {
        "title": "Test Video Title",
        "description": "This is a test video description.",
        "tags": ["test", "video", "example"],
    }
    mock_ai.generate_thumbnail_description.return_value = (
        "A person explaining a concept with a whiteboard"
    )
    mock_ai.summarize_content.return_value = "This is a summary of the video content."

    return mock_ai


@pytest.fixture
def publishing_adapter():
    """Mock for PublishingInterface."""
    from video_processor.application.interfaces.publishing import PublishingInterface

    mock_publishing = MagicMock(spec=PublishingInterface)

    # Configure methods to return appropriate values
    mock_publishing.upload_video.return_value = "test_video_id"
    mock_publishing.update_metadata.return_value = True
    mock_publishing.get_upload_status.return_value = "complete"
    mock_publishing.delete_video.return_value = True

    return mock_publishing


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
def test_video():
    """Create a test Video domain entity."""
    from video_processor.domain.models.video import Video

    return Video(
        id="test_video_123",
        file_path="/path/to/test_video.mp4",
        duration=120.5,
        format="mp4",
        resolution=(1920, 1080),
        created_at="2023-01-01T12:00:00Z",
    )


@pytest.fixture
def test_metadata():
    """Create a test VideoMetadata domain entity."""
    from video_processor.domain.models.metadata import VideoMetadata

    return VideoMetadata(
        title="Test Video Title",
        description="This is a test video description.",
        tags=["test", "video", "example"],
        show_notes="These are the show notes for the test video.",
        thumbnail_url="https://example.com/test_thumbnail.jpg",
        transcript="This is the transcript text for the test video.",
    )


@pytest.fixture
def test_job():
    """Create a test VideoJob domain entity."""
    from video_processor.domain.models.job import JobStatus, VideoJob

    return VideoJob(
        id="job_123",
        video_id="test_video_123",
        metadata_id="metadata_123",
        status=JobStatus.PENDING,
        created_at="2023-01-01T12:00:00Z",
        updated_at="2023-01-01T12:01:00Z",
        error=None,
    )


@pytest.fixture
def mock_job_repository():
    """Mock for JobRepositoryInterface."""
    from video_processor.application.interfaces.repositories import (
        JobRepositoryInterface,
    )

    mock_repo = MagicMock(spec=JobRepositoryInterface)

    # Configure methods to return appropriate values
    mock_repo.get_by_id.return_value = test_job()
    mock_repo.save.return_value = "job_123"
    mock_repo.update.return_value = True
    mock_repo.delete.return_value = True

    return mock_repo


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
