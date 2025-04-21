"""
Pytest configuration file with common fixtures for testing.

import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""

import os
import tempfile
import pytest
import subprocess
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_storage_client():
    """Mock for Google Cloud Storage client."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Set up the chain of mocks
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    return mock_client, mock_bucket, mock_blob


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
def mock_part():
    """Mock for Vertex AI Part object."""
    mock = MagicMock()
    mock.from_data.return_value = MagicMock()
    return mock
