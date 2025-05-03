"""
Transcript generation processor.
"""

from typing import Any

from video_processor.utils.error_handling import TranscriptionError, retry
from video_processor.utils.logging import get_logger

logger = get_logger(__name__)


class TranscriptProcessor:
    """
    Handles generation of transcripts from audio files.
    """

    def __init__(self, model_service: Any, testing_mode: bool = False):
        """
        Initialize the transcript processor.

        Args:
            model_service: Service for AI model access
            testing_mode: Whether to run in testing mode (returns mock data)
        """
        self.model_service = model_service
        self.testing_mode = testing_mode

    @retry(max_attempts=3)
    def generate_transcript(self, audio_path: str) -> str:
        """
        Generate a transcript from an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Generated transcript text

        Raises:
            TranscriptionError: If generation fails
        """
        try:
            logger.info(f"Generating transcript for {audio_path}")

            # For testing mode, return a mock transcript
            if self.testing_mode:
                logger.info("TESTING MODE: Returning mock transcript")
                return self._get_mock_transcript()

            # Read the audio file
            with open(audio_path, "rb") as f:
                audio_content = f.read()

            # Generate transcript using the model service
            prompt = (
                "Generate a transcription of the audio, only extract speech "
                "and ignore background audio."
            )
            response = self.model_service.generate_content(
                prompt=prompt,
                content=audio_content,
                content_type="audio/wav",
                config={"temperature": 0.2},
            )

            # Extract and clean the transcript
            transcript = self._clean_transcript(response)
            logger.info(f"Generated transcript ({len(transcript)} chars)")

            return transcript
        except Exception as e:
            logger.error(f"Failed to generate transcript: {e}")
            raise TranscriptionError(f"Failed to generate transcript: {e}") from e

    def _clean_transcript(self, response: Any) -> str:
        """
        Clean and format the transcript response.

        Args:
            response: Raw response from the model

        Returns:
            Cleaned transcript text
        """
        # Extract text from response
        if hasattr(response, "text") and response.text:
            transcript = response.text.strip()
        elif isinstance(response, str):
            transcript = response.strip()
        else:
            # Try to get text from the response or use empty string
            transcript = getattr(response, "text", str(response)).strip()

        # Basic cleaning (can be expanded)
        lines = transcript.split("\n")
        cleaned_lines = []

        for line in lines:
            # Remove common artifacts and unnecessary prefixes
            cleaned = line.strip()

            # Skip empty lines
            if not cleaned:
                continue

            # Remove timestamp prefixes (common in some models)
            if cleaned and cleaned[0].isdigit() and ":" in cleaned[:6]:
                parts = cleaned.split(" ", 1)
                if len(parts) > 1:
                    cleaned = parts[1]

            cleaned_lines.append(cleaned)

        return "\n".join(cleaned_lines)

    def _get_mock_transcript(self) -> str:
        """
        Generate a mock transcript for testing.

        Returns:
            Mock transcript text
        """
        return (
            "This is a mock transcript for testing purposes.\n"
            "It simulates what would be returned by the model in production.\n\n"
            "The transcript would contain all the spoken content from the video,\n"
            "formatted into paragraphs based on natural speech breaks.\n\n"
            "Speaker 1: This demonstrates a speaker change.\n"
            "Speaker 2: And here's another speaker responding.\n"
        )
