"""
Base adapter interface for AI service integrations.

This module defines the abstract base class that all AI service adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class AIAdapterInterface(ABC):
    """
    Abstract base class defining the interface for AI service adapters.

    All AI service implementations (e.g., Gemini, OpenAI) must inherit from this
    class and implement its methods to provide a consistent interface for the application.
    """

    @abstractmethod
    async def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate text based on a prompt and optional context."""
        pass

    @abstractmethod
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe speech from an audio file to text."""
        pass

    @abstractmethod
    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content to extract meaningful information."""
        pass

    @abstractmethod
    async def segment_transcript(
        self, transcript: str
    ) -> List[Dict[str, Union[str, float]]]:
        """Segment a transcript into meaningful chunks with timestamps."""
        pass

    @abstractmethod
    async def summarize_text(self, text: str, max_length: Optional[int] = None) -> str:
        """Generate a concise summary of the provided text."""
        pass

    # --- Additional methods required by MetadataService ---

    def generate_metadata(self, transcript: str) -> Dict[str, Any]:
        """
        Generate all metadata components from a transcript.
        Should return a dict with keys: title, description, tags, show_notes, chapters.
        """
        raise NotImplementedError

    def summarize_content(self, transcript: str, max_length: int = 500) -> str:
        """
        Summarize transcript content to a description.
        """
        raise NotImplementedError

    def generate_thumbnail_description(
        self, transcript: str, timestamp: float = 30.0
    ) -> str:
        """
        Generate a description for a thumbnail at a specific timestamp.
        """
        raise NotImplementedError

    def _generate_title_tags(self, transcript: str) -> Dict[str, str]:
        """
        Generate title and tags as a dictionary from transcript.
        Should return a dict with keys: Description, Keywords.
        """
        raise NotImplementedError
