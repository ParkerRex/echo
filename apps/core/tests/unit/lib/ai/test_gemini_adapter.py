"""
Unit tests for the Gemini AI adapter.
"""

import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from core.config import Settings
from core.exceptions import VideoProcessingError

from apps.core.lib.ai.gemini_adapter import AINoResponseError, GeminiAdapter


@pytest.fixture
def mock_settings():
    """Create mock settings with a valid Gemini API key."""
    settings = Settings()
    settings.GEMINI_API_KEY = "fake-api-key"
    return settings


@pytest.fixture
def mock_settings_no_api_key():
    """Create mock settings without a Gemini API key."""
    settings = Settings()
    settings.GEMINI_API_KEY = None
    return settings


@pytest.fixture
def mock_audio_file():
    """Create a temporary audio file for testing."""
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        temp_file.write(b"fake audio data")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def mock_genai():
    """Mock the Google Generative AI library."""
    with patch("lib.ai.gemini_adapter.genai") as mock_genai:
        # Mock the GenerativeModel class
        mock_text_model = MagicMock()
        mock_vision_model = MagicMock()

        # Mock the text response
        mock_response = MagicMock()
        mock_response.text = "Generated text from Gemini"
        mock_text_model.generate_content.return_value = mock_response

        # Set up the GenerativeModel constructor to return our mocks
        mock_genai.GenerativeModel.side_effect = (
            lambda model_name: mock_text_model
            if model_name == "gemini-pro"
            else mock_vision_model
        )

        yield mock_genai


class TestGeminiAdapter:
    """Test cases for the GeminiAdapter class."""

    def test_initialization_with_valid_api_key(self, mock_settings, mock_genai):
        """Test adapter initialization with a valid API key."""
        adapter = GeminiAdapter(mock_settings)

        # Verify genai was configured with the API key
        mock_genai.configure.assert_called_once_with(api_key="fake-api-key")

        # Verify models were initialized
        assert adapter.text_model is not None
        assert adapter.vision_model is not None

    def test_initialization_without_api_key(self, mock_settings_no_api_key):
        """Test adapter initialization fails without an API key."""
        with pytest.raises(ValueError) as excinfo:
            GeminiAdapter(mock_settings_no_api_key)

        assert "GEMINI_API_KEY must be set" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text_with_prompt_only(self, mock_settings, mock_genai):
        """Test generate_text with a prompt but no context."""
        adapter = GeminiAdapter(mock_settings)

        result = await adapter.generate_text("Generate a poem about AI")

        # Verify the model was called with the correct prompt
        adapter.text_model.generate_content.assert_called_once_with(
            "Generate a poem about AI"
        )

        # Verify the result
        assert result == "Generated text from Gemini"

    @pytest.mark.asyncio
    async def test_generate_text_with_prompt_and_context(
        self, mock_settings, mock_genai
    ):
        """Test generate_text with both prompt and context."""
        adapter = GeminiAdapter(mock_settings)

        result = await adapter.generate_text(
            prompt="Generate a poem about AI",
            context="Make it sound hopeful and optimistic",
        )

        # Verify the model was called with the combined prompt and context
        adapter.text_model.generate_content.assert_called_once_with(
            "Make it sound hopeful and optimistic\n\nGenerate a poem about AI"
        )

        # Verify the result
        assert result == "Generated text from Gemini"

    @pytest.mark.asyncio
    async def test_generate_text_handles_errors(self, mock_settings, mock_genai):
        """Test generate_text handles errors properly."""
        adapter = GeminiAdapter(mock_settings)

        # Set up the mock to raise an exception
        adapter.text_model.generate_content.side_effect = Exception("API error")

        # Test that our method wraps the exception properly
        with pytest.raises(AINoResponseError) as excinfo:
            await adapter.generate_text("Generate a poem about AI")

        assert "Error generating text with Gemini" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_text_handles_empty_response(
        self, mock_settings, mock_genai
    ):
        """Test generate_text handles empty response."""
        adapter = GeminiAdapter(mock_settings)

        # Set up the mock to return None
        adapter.text_model.generate_content.return_value = None

        # Test that our method detects the empty response
        with pytest.raises(AINoResponseError) as excinfo:
            await adapter.generate_text("Generate a poem about AI")

        assert "Gemini failed to generate a response" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_transcribe_audio(self, mock_settings, mock_genai, mock_audio_file):
        """Test transcribe_audio method."""
        adapter = GeminiAdapter(mock_settings)

        # Since Gemini doesn't natively support audio transcription (per the implementation),
        # verify it raises NotImplementedError wrapped in our AINoResponseError
        with pytest.raises(AINoResponseError) as excinfo:
            await adapter.transcribe_audio(mock_audio_file)

        assert "not supported by Gemini" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_transcribe_audio_file_not_found(self, mock_settings, mock_genai):
        """Test transcribe_audio with a non-existent file."""
        adapter = GeminiAdapter(mock_settings)

        with pytest.raises(FileNotFoundError):
            await adapter.transcribe_audio("/nonexistent/audio.mp3")

    @pytest.mark.asyncio
    async def test_analyze_content(self, mock_settings, mock_genai):
        """Test analyze_content method."""
        adapter = GeminiAdapter(mock_settings)

        # Mock the JSON response
        adapter.text_model.generate_content.return_value.text = json.dumps(
            {
                "title": "Test Title",
                "description": "Test description",
                "tags": ["test", "ai", "gemini"],
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "sentiment": "positive",
            }
        )

        result = await adapter.analyze_content("This is content to analyze")

        # Verify the model was called with the structured prompt
        assert adapter.text_model.generate_content.called

        # Verify the result contains expected keys
        assert "title" in result
        assert "description" in result
        assert "tags" in result
        assert "key_points" in result
        assert "sentiment" in result

        # Verify specific values
        assert result["title"] == "Test Title"
        assert result["tags"] == ["test", "ai", "gemini"]

    @pytest.mark.asyncio
    async def test_analyze_content_handles_malformed_json(
        self, mock_settings, mock_genai
    ):
        """Test analyze_content handles malformed JSON."""
        adapter = GeminiAdapter(mock_settings)

        # Mock malformed JSON response
        adapter.text_model.generate_content.return_value.text = "Not a valid JSON"

        # Test that our method wraps the JSON decode exception
        with pytest.raises(AINoResponseError) as excinfo:
            await adapter.analyze_content("This is content to analyze")

        assert "Gemini returned malformed JSON" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_segment_transcript(self, mock_settings, mock_genai):
        """Test segment_transcript method."""
        adapter = GeminiAdapter(mock_settings)

        # Mock the JSON response for transcript segmentation
        adapter.text_model.generate_content.return_value.text = json.dumps(
            [
                {"text": "First segment", "start_time": 0.0, "end_time": 5.0},
                {"text": "Second segment", "start_time": 5.0, "end_time": 10.0},
            ]
        )

        result = await adapter.segment_transcript("This is a transcript to segment")

        # Verify the model was called with the structured prompt
        assert adapter.text_model.generate_content.called

        # Verify the result is a list of segments
        assert isinstance(result, list)
        assert len(result) == 2

        # Verify each segment has required fields
        for segment in result:
            assert "text" in segment
            assert "start_time" in segment
            assert "end_time" in segment

    @pytest.mark.asyncio
    async def test_summarize_text(self, mock_settings, mock_genai):
        """Test summarize_text method."""
        adapter = GeminiAdapter(mock_settings)

        # Test without max_length
        result1 = await adapter.summarize_text("This is text to summarize")

        # Verify the model was called with the right prompt
        adapter.text_model.generate_content.assert_called_with(
            "Summarize the following text in a concise manner:\n\nThis is text to summarize"
        )

        # Test with max_length
        result2 = await adapter.summarize_text(
            "This is text to summarize", max_length=100
        )

        # Verify the model was called with the right prompt including max_length
        adapter.text_model.generate_content.assert_called_with(
            "Summarize the following text in a concise manner in 100 characters or less:\n\nThis is text to summarize"
        )
