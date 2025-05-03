"""
Mock AI service adapter for testing.
"""

from typing import Dict

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.domain.exceptions import MetadataGenerationError


class MockAIAdapter(AIServiceInterface):
    """
    Mock implementation of AIServiceInterface for testing.
    Provides predefined responses for AI operations.
    """

    def __init__(self, model_name: str = "test-model"):
        """
        Initialize the mock AI adapter.

        Args:
            model_name: Name of the AI model to simulate
        """
        self.model_name = model_name
        self.responses = {
            "transcripts": {},
            "metadata": {},
            "thumbnails": {},
            "summaries": {},
        }

        # Set some default mock responses
        self._set_default_responses()

    def _set_default_responses(self):
        """Set up default mock responses."""
        # Default transcript
        default_transcript = (
            "This is a mock transcript generated for testing purposes. "
            "It contains some sample text that would typically be generated "
            "from audio content. The quick brown fox jumps over the lazy dog. "
            "Welcome to our video about automated processing."
        )

        # Default metadata
        default_metadata = {
            "title": "Sample Test Video",
            "description": "This is an automatically generated description for a test video.",
            "tags": ["test", "sample", "automation", "video processing"],
            "chapters": [
                {"time": 0, "title": "Introduction"},
                {"time": 60, "title": "Main Content"},
                {"time": 120, "title": "Conclusion"},
            ],
        }

        # Default thumbnail description
        default_thumbnail = (
            "A person explaining a concept with diagrams on a whiteboard."
        )

        # Default summary
        default_summary = "This video covers automated video processing and metadata generation techniques."

        # Set as default responses
        self.responses["transcripts"]["default"] = default_transcript
        self.responses["metadata"]["default"] = default_metadata
        self.responses["thumbnails"]["default"] = default_thumbnail
        self.responses["summaries"]["default"] = default_summary

    def generate_transcript(self, audio_file: str) -> str:
        """
        Generate a transcript from an audio file.

        Args:
            audio_file: Path to audio file

        Returns:
            Generated transcript text

        Raises:
            MetadataGenerationError: If generation fails
        """
        try:
            # Return a specific mock transcript if one is set for this file
            file_key = audio_file.split("/")[-1]
            if file_key in self.responses["transcripts"]:
                return self.responses["transcripts"][file_key]

            # Otherwise return the default
            return self.responses["transcripts"]["default"]
        except Exception as e:
            raise MetadataGenerationError(f"Failed to generate transcript: {str(e)}")

    def generate_metadata(self, transcript: str) -> Dict:
        """
        Generate metadata from a transcript.

        Args:
            transcript: Transcript text

        Returns:
            Dictionary of generated metadata

        Raises:
            MetadataGenerationError: If generation fails
        """
        try:
            # Check if we have a specific response for this transcript
            # Using a hash of the first 50 chars as a simple lookup key
            key = hash(transcript[:50]) % 10000
            if str(key) in self.responses["metadata"]:
                return self.responses["metadata"][str(key)]

            # Otherwise return the default
            return self.responses["metadata"]["default"]
        except Exception as e:
            raise MetadataGenerationError(f"Failed to generate metadata: {str(e)}")

    def generate_thumbnail_description(self, transcript: str, timestamp: float) -> str:
        """
        Generate a description for a thumbnail at a specific timestamp.

        Args:
            transcript: Transcript text
            timestamp: Time in seconds

        Returns:
            Thumbnail description

        Raises:
            MetadataGenerationError: If generation fails
        """
        try:
            # Create a key based on timestamp
            key = f"time_{int(timestamp)}"
            if key in self.responses["thumbnails"]:
                return self.responses["thumbnails"][key]

            # Otherwise return the default
            return self.responses["thumbnails"]["default"]
        except Exception as e:
            raise MetadataGenerationError(
                f"Failed to generate thumbnail description: {str(e)}"
            )

    def summarize_content(self, transcript: str, max_length: int = 500) -> str:
        """
        Summarize content from a transcript.

        Args:
            transcript: Transcript text
            max_length: Maximum length of summary

        Returns:
            Summary text

        Raises:
            MetadataGenerationError: If generation fails
        """
        try:
            # Check if we have a specific response for this transcript
            # Using a hash of the first 50 chars as a simple lookup key
            key = hash(transcript[:50]) % 10000
            if str(key) in self.responses["summaries"]:
                summary = self.responses["summaries"][str(key)]
            else:
                summary = self.responses["summaries"]["default"]

            # Respect max_length
            return summary[:max_length]
        except Exception as e:
            raise MetadataGenerationError(f"Failed to summarize content: {str(e)}")

    def set_model(self, model_name: str) -> None:
        """
        Set the AI model to use.

        Args:
            model_name: Name of the model
        """
        self.model_name = model_name

    def set_custom_response(self, response_type: str, key: str, value: any) -> None:
        """
        Set a custom response for a specific input.

        Args:
            response_type: Type of response ("transcripts", "metadata", "thumbnails", "summaries")
            key: Key for the response
            value: Response value
        """
        if response_type in self.responses:
            self.responses[response_type][key] = value
