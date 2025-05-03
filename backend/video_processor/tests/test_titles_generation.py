"""
Tests for the titles and keywords generation functionality.
"""

import json
import os

# Import the functions to test
import sys
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from process_uploaded_video import generate_titles


def test_generate_titles_valid_json(mock_generative_model, mock_part):
    """Test the generate_titles function with valid JSON response."""
    # Create a valid JSON response
    valid_title_dict = {
        "Description": "Exciting Video Title",
        "Keywords": "keyword1,keyword2,keyword3,keyword4",
    }

    # Set up the mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps(valid_title_dict)
    mock_generative_model.generate_content.return_value = mock_response

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function
        result = generate_titles(mock_audio_part)

        # Verify the result
        assert result["Description"] == "Exciting Video Title"
        assert result["Keywords"] == "keyword1,keyword2,keyword3,keyword4"

        # Verify the model was called with the correct parameters
        mock_generative_model.generate_content.assert_called_once()
        args, kwargs = mock_generative_model.generate_content.call_args

        # Check that the prompt and audio part were passed correctly
        assert len(args[0]) == 2
        assert (
            "Please write a 40-character long intriguing title" in args[0][0]
        )  # Check part of the prompt
        assert args[0][1] == mock_audio_part  # Check the audio part

        # Check the generation config
        assert "temperature" in kwargs.get("generation_config", {})
        assert kwargs["generation_config"]["temperature"] == 0.8
        assert kwargs["generation_config"]["response_mime_type"] == "application/json"


def test_generate_titles_invalid_json(mock_generative_model, mock_part):
    """Test the generate_titles function with invalid JSON response."""
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
        result = generate_titles(mock_audio_part)

        # Verify the result is the default dictionary for invalid JSON
        assert result["Description"] == "Default Title"
        assert result["Keywords"] == "default,keywords"


def test_generate_titles_missing_keys(mock_generative_model, mock_part):
    """Test the generate_titles function with JSON missing required keys."""
    # Create JSON with missing keys
    invalid_title_dict = {
        "Title": "Wrong Key Name",  # Missing Description
        "Tags": "tag1,tag2,tag3",  # Missing Keywords
    }

    # Set up the mock response
    mock_response = MagicMock()
    mock_response.text = json.dumps(invalid_title_dict)
    mock_generative_model.generate_content.return_value = mock_response

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function
        result = generate_titles(mock_audio_part)

        # Verify the result is the default dictionary for invalid structure
        assert result["Description"] == "Default Title"
        assert result["Keywords"] == "default,keywords"


def test_generate_titles_error_handling(mock_generative_model, mock_part):
    """Test error handling in the generate_titles function."""
    # Set up the mock to raise an exception
    mock_generative_model.generate_content.side_effect = Exception("API error")

    # Create a mock audio part
    mock_audio_part = MagicMock()

    # Patch the GenerativeModel class to return our mock
    with patch(
        "video_processor.process_uploaded_video.GenerativeModel",
        return_value=mock_generative_model,
    ):
        # Call the function - it should handle the exception and return
        # the default dictionary
        result = generate_titles(mock_audio_part)

        # Verify the result is the default dictionary when an exception occurs
        assert result["Description"] == "Default Title"
        assert result["Keywords"] == "default,keywords"
