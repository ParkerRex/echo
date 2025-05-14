"""
Tests for the VTT subtitles generation functionality.
"""

import os

# Import the functions to test
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from process_uploaded_video import generate_vtt

# Import Part for mocking
from vertexai.preview.generative_models import Part


@pytest.mark.parametrize(
    "mock_response_text,expected_result",
    [
        (
            "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nHello world",
            "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nHello world",
        ),
        (
            "00:00:00.000 --> 00:00:05.000\nMissing WEBVTT header",
            "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nMissing WEBVTT header".replace(
                "\\n", "\n"
            ),
        ),
        ("  WEBVTT  ", "WEBVTT"),
    ],
)
def test_generate_vtt(
    mock_generative_model, mock_part, mock_response_text, expected_result
):
    """Test the generate_vtt function with various inputs."""
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
        result = generate_vtt(mock_audio_part)

        # Verify the result - normalize newlines for comparison
        assert result.replace("\\n", "\n") == expected_result

        # Verify the model was called
        mock_generative_model.generate_content.assert_called_once()


def test_generate_vtt_webvtt_correction():
    """Test that the VTT generator adds WEBVTT header if missing."""
    # Create a mock response without WEBVTT header
    mock_response = MagicMock()
    mock_response.text = "00:00:00.000 --> 00:00:05.000\nThis is a test subtitle"

    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    # Create a mock audio part that is a proper Part instance
    mock_audio_part = MagicMock(spec=Part)

    # Patch the necessary classes and functions
    with patch(
        "process_uploaded_video.GenerativeModel",
        return_value=mock_model,
    ):
        # Call the function
        result = generate_vtt(mock_audio_part)

        # Verify the result has WEBVTT header added
        assert result.replace("\\n", "\n").startswith("WEBVTT\n\n")
        assert "00:00:00.000 --> 00:00:05.000" in result
        assert "This is a test subtitle" in result


def test_generate_vtt_error_handling(mock_generative_model):
    """Test error handling in the generate_vtt function."""
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
            generate_vtt(mock_audio_part)

        # Verify the exception message
        assert "API error" in str(excinfo.value)
