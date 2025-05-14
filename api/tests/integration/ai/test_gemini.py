"""Integration tests for Gemini AI adapter."""
import os
import pytest
from typing import Optional

from video_processor.adapters.ai.gemini import GeminiAIAdapter
from video_processor.domain.exceptions import MetadataGenerationError


@pytest.fixture
def api_key() -> Optional[str]:
    """Get API key from environment variable."""
    return os.environ.get("GEMINI_API_KEY")


@pytest.fixture
def sample_transcript() -> str:
    """Provide a sample transcript for testing."""
    return """
    Hello and welcome to our video about the benefits of clean architecture. 
    Today, we're going to discuss how clean architecture helps with maintainability, 
    testing, and overall code quality. 
    
    First, let's talk about separation of concerns. Clean architecture divides your
    codebase into distinct layers, each with specific responsibilities. This makes
    it easier to understand and maintain the system.
    
    Second, we'll cover dependency inversion. By depending on abstractions rather
    than concrete implementations, we can easily swap out components, which is
    particularly useful for testing.
    
    Finally, we'll look at how clean architecture promotes testability by allowing
    us to test business logic in isolation from external dependencies.
    
    Thanks for watching, and don't forget to like and subscribe for more architecture videos!
    """


@pytest.fixture
def sample_audio_file(tmpdir) -> str:
    """Create a placeholder for an audio file path.
    
    In a real test, this would be a path to an actual audio file.
    For this integration test, we'll skip actual audio transcription
    and focus on the other AI functions that use text input.
    """
    return str(tmpdir.join("sample_audio.mp3"))


@pytest.fixture
def ai_adapter(api_key) -> Optional[GeminiAIAdapter]:
    """Create a Gemini AI adapter for testing if API key is available."""
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable not set")
    
    return GeminiAIAdapter(api_key=api_key)


@pytest.mark.integration
class TestGeminiAIAdapter:
    """Integration tests for Gemini AI adapter."""
    
    def test_generate_metadata(self, ai_adapter, sample_transcript):
        """Test generating metadata from a transcript."""
        metadata = ai_adapter.generate_metadata(sample_transcript)
        
        # Verify that we get a dictionary with expected keys
        assert isinstance(metadata, dict)
        assert "title" in metadata
        assert "description" in metadata
        assert "tags" in metadata
        
        # Verify title is a reasonable length
        assert len(metadata["title"]) > 10
        assert len(metadata["title"]) < 100
        
        # Verify description has some content
        assert len(metadata["description"]) > 50
        
        # Verify tags are a list with reasonable content
        assert isinstance(metadata["tags"], list)
        assert len(metadata["tags"]) > 0
        
        # Verify content relevance (basic check)
        assert "architecture" in sample_transcript.lower()
        assert any("architecture" in tag.lower() for tag in metadata["tags"]) or \
               "architecture" in metadata["title"].lower() or \
               "architecture" in metadata["description"].lower()
    
    def test_generate_thumbnail_description(self, ai_adapter, sample_transcript):
        """Test generating a thumbnail description."""
        timestamp = 30.0  # 30 seconds into the video
        description = ai_adapter.generate_thumbnail_description(
            transcript=sample_transcript,
            timestamp=timestamp
        )
        
        # Verify we get a non-empty string
        assert isinstance(description, str)
        assert len(description) > 10
        
        # Should be related to the content
        assert "architecture" in description.lower() or \
               "clean" in description.lower() or \
               "code" in description.lower()
    
    def test_summarize_content(self, ai_adapter, sample_transcript):
        """Test summarizing content from a transcript."""
        max_length = 100
        summary = ai_adapter.summarize_content(
            transcript=sample_transcript,
            max_length=max_length
        )
        
        # Verify length constraints
        assert isinstance(summary, str)
        assert len(summary) <= max_length
        assert len(summary) > 20  # Should have reasonable content
        
        # Should be related to the content
        assert "architecture" in summary.lower() or \
               "clean" in summary.lower()
    
    def test_set_model(self, ai_adapter):
        """Test setting a different model."""
        # Store the original model
        original_model = ai_adapter.model_name
        
        # Set a new model
        new_model = "gemini-pro-vision"
        ai_adapter.set_model(new_model)
        
        # Verify the model was changed
        assert ai_adapter.model_name == new_model
        
        # Reset to original model
        ai_adapter.set_model(original_model)
    
    def test_invalid_api_key(self):
        """Test that an invalid API key raises an appropriate error."""
        invalid_adapter = GeminiAIAdapter(api_key="invalid_key")
        
        with pytest.raises(MetadataGenerationError):
            invalid_adapter.generate_metadata("This is a test transcript") 