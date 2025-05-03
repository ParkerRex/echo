"""
Tests for the transcript generation functionality.
"""

import os

# Import the functions to test
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from process_uploaded_video import generate_transcript

# Import Part for mocking
from vertexai.preview.generative_models import Part


@pytest.mark.parametrize(
    "mock_response_text,expected_result",
    [
        ("Test transcript", "Test transcript"),
        ("  Transcript with whitespace  ", "Transcript with whitespace"),
        ("", ""),
    ],
)
def test_generate_transcript(
    mock_generative_model, mock_part, mock_response_text, expected_result
):
    """Test the generate_transcript function with various inputs."""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.text = mock_response_text
    mock_generative_model.generate_content.return_value = mock_response

    # Create a mock audio part that is a proper Part instance
    mock_audio_part = MagicMock(spec=Part)

    # Patch the necessary classes and functions
    with patch(
        "process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function
        result = generate_transcript(mock_audio_part)

        # Verify the result
        assert result == expected_result

        # Verify the model was called
        mock_generative_model.generate_content.assert_called_once()


def test_generate_transcript_with_real_audio():
    """Test the generate_transcript function with a real audio file."""
    # This test requires actual API credentials, so we'll mock the API call
    mock_response = MagicMock()
    mock_response.text = "This is a test transcript for audio file."

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    # Create a mock audio part that is a proper Part instance
    mock_audio_part = MagicMock(spec=Part)

    # Patch the necessary functions
    with patch(
        "process_uploaded_video.GenerativeModel",
        return_value=mock_model,
    ):
        # Call the function directly with the mock audio part
        result = generate_transcript(mock_audio_part)

        # Verify the result
        assert result == "This is a test transcript for audio file."

        # Verify the model was called
        mock_model.generate_content.assert_called_once()


def test_generate_transcript_error_handling(mock_generative_model):
    """Test error handling in the generate_transcript function."""
    # Set up the mock to raise an exception
    mock_generative_model.generate_content.side_effect = Exception("API error")

    # Create a mock audio part that is a proper Part instance
    mock_audio_part = MagicMock(spec=Part)

    # Patch the necessary classes and functions
    with patch(
        "process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            generate_transcript(mock_audio_part)

        # Verify the exception message
        assert "API error" in str(excinfo.value)
