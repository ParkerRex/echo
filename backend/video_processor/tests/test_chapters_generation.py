"""
Tests for the chapters generation functionality.
"""

import json
import os

# Import the functions to test
import sys
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from process_uploaded_video import generate_chapters


def test_generate_chapters_valid_json(mock_generative_model, mock_part):
    """Test the generate_chapters function with valid JSON response."""
    # Create a valid JSON response
    valid_chapters = [
        {"timecode": "00:00", "chapterSummary": "Introduction"},
        {"timecode": "02:30", "chapterSummary": "Main topic"},
        {"timecode": "05:45", "chapterSummary": "Conclusion"},
    ]

    # Set up the mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps(valid_chapters)
    mock_generative_model.generate_content.return_value = mock_response

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function
        result = generate_chapters(mock_audio_part)

        # Verify the result
        assert len(result) == 3
        assert result[0]["timecode"] == "00:00"
        assert result[0]["chapterSummary"] == "Introduction"
        assert result[1]["timecode"] == "02:30"
        assert result[2]["chapterSummary"] == "Conclusion"

        # Verify the model was called with the correct parameters
        mock_generative_model.generate_content.assert_called_once()
        args, kwargs = mock_generative_model.generate_content.call_args

        # Check that the prompt and audio part were passed correctly
        assert len(args[0]) == 2
        assert "Chapterize the video content" in args[0][0]  # Check part of the prompt
        assert args[0][1] == mock_audio_part  # Check the audio part

        # Check the generation config
        assert "temperature" in kwargs.get("generation_config", {})
        assert kwargs["generation_config"]["temperature"] == 0.6
        assert kwargs["generation_config"]["response_mime_type"] == "application/json"


def test_generate_chapters_invalid_json(mock_generative_model, mock_part):
    """Test the generate_chapters function with invalid JSON response."""
    # Set up the mock response with invalid JSON
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON"
    mock_generative_model.generate_content.return_value = mock_response

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function
        result = generate_chapters(mock_audio_part)

        # Verify the result is an empty list for invalid JSON
        assert result == []


def test_generate_chapters_missing_keys(mock_generative_model, mock_part):
    """Test the generate_chapters function with JSON missing required keys."""
    # Create JSON with missing keys
    invalid_chapters = [
        {"timecode": "00:00", "summary": "Introduction"},  # Missing chapterSummary
        {"time": "02:30", "chapterSummary": "Main topic"},  # Missing timecode
        {"other": "field"},  # Missing both required keys
    ]

    # Set up the mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps(invalid_chapters)
    mock_generative_model.generate_content.return_value = mock_response

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function
        result = generate_chapters(mock_audio_part)

        # Verify the result is an empty list for invalid structure
        assert result == []


def test_generate_chapters_error_handling(mock_generative_model, mock_part):
    """Test error handling in the generate_chapters function."""
    # Set up the mock to raise an exception
    mock_generative_model.generate_content.side_effect = Exception("API error")

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function - it should handle the exception and return an empty list
        result = generate_chapters(mock_audio_part)

        # Verify the result is an empty list when an exception occurs
        assert result == []
