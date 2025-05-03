"""
Pytest configuration file with common fixtures for testing.
"""

import os
import subprocess
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from google.cloud.storage import Client as StorageClient
from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.publishing import PublishingInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.models.enums import ProcessingStage, ProcessingStatus
from video_processor.domain.models.job import VideoJob
from video_processor.domain.models.metadata import VideoMetadata
from video_processor.domain.models.video import Video

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
    """Create a sample video for testing."""
    return Video(
        id="test123",
        file_path="/path/to/sample.mp4",
        file_name="sample.mp4",
        file_size=1024000,
        file_format="mp4",
        duration=60.0,
        width=1920,
        height=1080,
        bucket_name="test-bucket",
    )


@pytest.fixture
def test_metadata():
    """Create sample metadata for testing."""
    return VideoMetadata(
        title="Test Video Title",
        description="This is a test video description.",
        keywords="test, video, sample",
        category_id="22",  # People & Blogs
        duration_seconds=60,
        width=1920,
        height=1080,
        channel="daily",
        tags=["test", "video", "sample"],
        show_notes="These are test show notes.",
        thumbnail_url="https://example.com/thumbnail.jpg",
        transcript="This is a test transcript.",
        chapters=[
            {"time": "00:00", "title": "Introduction"},
            {"time": "00:30", "title": "Main Content"},
        ],
    )


@pytest.fixture
def test_job(test_video, test_metadata):
    """Create a sample job for testing."""
    return VideoJob(
        job_id="job123",
        video=test_video,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata=test_metadata,
        status=ProcessingStatus.IN_PROGRESS,
        current_stage=ProcessingStage.GENERATE_TRANSCRIPT,
        completed_stages=[ProcessingStage.DOWNLOAD, ProcessingStage.EXTRACT_AUDIO],
        error_message=None,
        processed_path="/processed/sample.mp4",
        output_files={
            "transcript": "/path/to/transcript.txt",
            "subtitles": "/path/to/subtitles.vtt",
        },
        youtube_video_id=None,
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


@pytest.fixture
def mock_storage_adapter():
    """Create a mock storage adapter for testing."""
    mock_storage = MagicMock(spec=StorageInterface)

    # Configure default return values
    mock_storage.upload_file.return_value = "gs://test-bucket/uploaded/file.mp4"
    mock_storage.download_file.return_value = "/tmp/downloaded/file.mp4"
    mock_storage.delete_file.return_value = True
    mock_storage.get_public_url.return_value = (
        "https://storage.googleapis.com/test-bucket/file.mp4"
    )
    mock_storage.get_signed_url.return_value = (
        "https://storage.googleapis.com/test-bucket/file.mp4?token=abc123"
    )

    return mock_storage


@pytest.fixture
def mock_ai_adapter():
    """Create a mock AI adapter for testing."""
    mock_ai = MagicMock(spec=AIServiceInterface)

    # Configure default return values
    mock_ai.generate_transcript.return_value = "This is a test transcript."
    mock_ai.generate_metadata.return_value = {
        "title": "Generated Title",
        "description": "Generated description",
        "tags": ["ai", "generated", "tags"],
        "show_notes": "Generated show notes",
    }
    mock_ai.generate_thumbnail_description.return_value = (
        "A person explaining video processing"
    )
    mock_ai.summarize_content.return_value = "This is a summary of the video content."

    return mock_ai


@pytest.fixture
def mock_publishing_adapter():
    """Create a mock publishing adapter for testing."""
    mock_pub = MagicMock(spec=PublishingInterface)

    # Configure default return values
    mock_pub.upload_video.return_value = "yt12345"
    mock_pub.update_metadata.return_value = True
    mock_pub.get_upload_status.return_value = "published"
    mock_pub.delete_video.return_value = True

    return mock_pub
