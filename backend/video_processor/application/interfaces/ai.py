"""
AI service interface for the video processing application.

Defines the contract for AI operations independent of any specific
AI service implementation (Gemini, Vertex AI, etc.).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class AIServiceInterface(ABC):
    """
    Interface for AI service operations.

    This interface defines the contract for all AI service adapter implementations,
    ensuring they provide the necessary methods for content generation.
    """

    @abstractmethod
    def generate_transcript(self, audio_file: str) -> str:
        """
        Generate a transcript from an audio file.

        Args:
            audio_file: Path to the audio file

        Returns:
            The generated transcript text

        Raises:
            TranscriptionError: If transcript generation fails
        """
        pass

    @abstractmethod
    def generate_metadata(self, transcript: str) -> Dict:
        """
        Generate video metadata from a transcript.

        Args:
            transcript: Transcript text

        Returns:
            A dictionary containing generated metadata:
            {
                "title": str,
                "description": str,
                "tags": List[str],
                "show_notes": str,
                "chapters": List[Dict[str, str]]
            }

        Raises:
            MetadataGenerationError: If metadata generation fails
        """
        pass

    @abstractmethod
    def generate_thumbnail_description(self, transcript: str, timestamp: float) -> str:
        """
        Generate a description for a thumbnail at a specific timestamp.

        Args:
            transcript: Transcript text
            timestamp: Time in seconds for the thumbnail

        Returns:
            A text description for the thumbnail image

        Raises:
            MetadataGenerationError: If description generation fails
        """
        pass

    @abstractmethod
    def summarize_content(self, transcript: str, max_length: int = 500) -> str:
        """
        Generate a summary of the content from a transcript.

        Args:
            transcript: Transcript text
            max_length: Maximum length of the summary in characters

        Returns:
            A summary of the content

        Raises:
            MetadataGenerationError: If summary generation fails
        """
        pass

    @abstractmethod
    def set_model(self, model_name: str) -> None:
        """
        Set the AI model to use for generation.

        Args:
            model_name: Name of the model to use

        Raises:
            ValueError: If the model name is invalid
        """
        pass

    @abstractmethod
    def generate_chapters(
        self, transcript: str, num_chapters: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate chapters from a transcript.

        Args:
            transcript: Transcript text
            num_chapters: Optional number of chapters to generate,
                          or None to let the AI determine the optimal number

        Returns:
            A list of chapter dictionaries:
            [
                {"title": str, "start_time": float, "end_time": float},
                ...
            ]

        Raises:
            MetadataGenerationError: If chapter generation fails
        """
        pass
