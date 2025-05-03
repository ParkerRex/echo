"""
Mock implementation of the AI service interface for testing.
"""

from typing import Dict

from video_processor.application.interfaces.ai import AIServiceInterface


class MockAIAdapter(AIServiceInterface):
    """
    Mock implementation of AIServiceInterface for testing.

    Provides predetermined responses for AI operations without actually
    calling any AI services.
    """

    def __init__(self, model_name: str = "mock-model"):
        """Initialize the mock AI adapter."""
        self.model_name = model_name
        # Store call counts for verification in tests
        self.call_counts = {
            "generate_transcript": 0,
            "generate_metadata": 0,
            "generate_thumbnail_description": 0,
            "summarize_content": 0,
            "set_model": 0,
        }
        # Predefined responses
        self.responses = {
            "transcript": "This is a mock transcript of the video content. "
            "The speaker discusses video processing techniques.",
            "metadata": {
                "title": "How to Process Videos Effectively",
                "description": "A comprehensive guide to video processing using modern techniques.",
                "tags": ["video", "processing", "tutorial", "AI"],
                "show_notes": "00:00 Introduction\n00:30 Basic concepts\n01:45 Advanced techniques",
            },
            "thumbnail": "A person explaining video processing concepts with a whiteboard",
            "summary": "This video covers the fundamentals of video processing including "
            "transcoding, metadata extraction, and AI-assisted content generation.",
        }

    def set_model(self, model_name: str) -> None:
        """
        Set the AI model to use.

        Args:
            model_name: Name of the model to use
        """
        self.call_counts["set_model"] += 1
        self.model_name = model_name

    def generate_transcript(self, audio_file: str) -> str:
        """
        Generate a transcript from an audio file.

        Args:
            audio_file: Path to the audio file

        Returns:
            Generated transcript text
        """
        self.call_counts["generate_transcript"] += 1
        return self.responses["transcript"]

    def generate_metadata(self, transcript: str) -> Dict:
        """
        Generate metadata from a transcript.

        Args:
            transcript: Video transcript text

        Returns:
            Dictionary containing generated metadata
        """
        self.call_counts["generate_metadata"] += 1
        return self.responses["metadata"]

    def generate_thumbnail_description(self, transcript: str, timestamp: float) -> str:
        """
        Generate a description for a thumbnail at a specific timestamp.

        Args:
            transcript: Video transcript text
            timestamp: Timestamp in seconds

        Returns:
            Description for the thumbnail
        """
        self.call_counts["generate_thumbnail_description"] += 1
        return f"At {timestamp:.2f}s: {self.responses['thumbnail']}"

    def summarize_content(self, transcript: str, max_length: int = 500) -> str:
        """
        Generate a summary of the transcript content.

        Args:
            transcript: Video transcript text
            max_length: Maximum summary length

        Returns:
            Summarized content
        """
        self.call_counts["summarize_content"] += 1
        # Adjust summary length if needed
        if max_length < len(self.responses["summary"]):
            return self.responses["summary"][:max_length] + "..."
        return self.responses["summary"]

    def set_custom_response(self, response_type: str, response_data: any) -> None:
        """
        Set a custom response for a specific operation.
        Useful for testing specific scenarios.

        Args:
            response_type: Type of response to set (transcript, metadata, etc.)
            response_data: The response data to use
        """
        if response_type in self.responses:
            self.responses[response_type] = response_data

    def reset_call_counts(self) -> None:
        """Reset all call counters to zero."""
        for key in self.call_counts:
            self.call_counts[key] = 0
