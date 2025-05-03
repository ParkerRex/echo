"""
Vertex AI adapter implementation.

This module provides a concrete implementation of the AIServiceInterface
for Google Cloud Vertex AI, offering advanced AI capabilities beyond basic Gemini models.
"""

import json
import logging
import time
from typing import Dict, List, Optional

from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, Part

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.domain.exceptions import (
    MetadataGenerationError,
    TranscriptionError,
)


class VertexAIAdapter(AIServiceInterface):
    """
    Vertex AI implementation of AIServiceInterface.

    This adapter implements AI operations using Google's Vertex AI platform,
    which provides more advanced features and models compared to basic Gemini.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model: str = "gemini-2.0-pro",
    ):
        """
        Initialize the Vertex AI Adapter.

        Args:
            project_id: Google Cloud project ID (if None, will use default from environment)
            location: Google Cloud region to use
            model: Model name to use (default: gemini-2.0-pro)
        """
        self._project_id = project_id
        self._location = location
        self._model_name = model

        # Initialize Vertex AI client
        aiplatform.init(project=self._project_id, location=self._location)

        # Initialize the model
        self._model = GenerativeModel(self._model_name)

        logging.info(
            f"Initialized Vertex AI adapter with project: {self._project_id}, "
            f"location: {self._location}, model: {self._model_name}"
        )

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
        try:
            # Create audio part from file
            audio_part = Part.from_uri(audio_file, mime_type="audio/wav")

            # Set prompt for transcript generation
            prompt = (
                "Generate a detailed, accurate transcription of the audio, "
                "only extract speech and ignore background audio. "
                "Include speaker labels if multiple speakers are detected."
            )

            # Implement retry logic with exponential backoff
            max_retries = 3
            backoff = 1  # Initial backoff in seconds

            for attempt in range(max_retries):
                try:
                    response = self._model.generate_content(
                        [prompt, audio_part],
                        generation_config={
                            "temperature": 0.2,  # Lower temp for accuracy
                            "max_output_tokens": 8192,  # Allow longer transcripts
                        },
                    )

                    # Validate response
                    if not hasattr(response, "text") or not response.text:
                        raise TranscriptionError("Empty transcript generated")

                    return response.text.strip()
                except Exception as e:
                    if attempt == max_retries - 1:
                        # Last attempt failed, raise exception
                        raise
                    # Exponential backoff
                    logging.warning(
                        f"Transcript generation attempt {attempt+1} failed: {e}. Retrying..."
                    )
                    time.sleep(backoff)
                    backoff *= 2

        except Exception as e:
            error_msg = f"Failed to generate transcript: {str(e)}"
            logging.error(error_msg)
            raise TranscriptionError(error_msg) from e

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
        try:
            # Generate content with a single comprehensive prompt to reduce API calls
            prompt = (
                "Generate comprehensive metadata for a video based on this transcript. "
                "Return ONLY a valid JSON object with the following structure:\n"
                "{\n"
                '  "title": "An engaging, SEO-optimized title under 60 characters",\n'
                '  "description": "A compelling 2-3 sentence description of the video content",\n'
                '  "tags": ["tag1", "tag2", "tag3", ...],\n'  # List of 8-10 relevant tags
                '  "show_notes": "Detailed markdown-formatted notes with sections and bullet points",\n'
                '  "chapters": [\n'
                '    {"title": "Chapter title", "start_time": 0.0, "end_time": 120.5},\n'
                '    {"title": "Next chapter", "start_time": 120.5, "end_time": 300.0},\n'
                "    ...\n"
                "  ]\n"
                "}\n"
                "Ensure the JSON is valid and each field follows the format described."
            )

            response = self._model.generate_content(
                [prompt, transcript],
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 4096,
                    "response_mime_type": "application/json",
                },
            )

            # Parse and validate the JSON response
            try:
                metadata = json.loads(response.text)

                # Basic validation
                required_keys = [
                    "title",
                    "description",
                    "tags",
                    "show_notes",
                    "chapters",
                ]
                if not all(key in metadata for key in required_keys):
                    missing_keys = [key for key in required_keys if key not in metadata]
                    raise ValueError(
                        f"Missing required keys in metadata: {missing_keys}"
                    )

                # Additional validation for nested structures
                if not isinstance(metadata["tags"], list):
                    metadata["tags"] = (
                        metadata["tags"].split(",")
                        if isinstance(metadata["tags"], str)
                        else []
                    )

                if not isinstance(metadata["chapters"], list):
                    metadata["chapters"] = []

                return metadata

            except json.JSONDecodeError as e:
                logging.error(
                    f"Failed to parse metadata JSON: {e}. Raw response: {response.text}"
                )
                raise ValueError(f"Invalid JSON response: {e}")

        except Exception as e:
            error_msg = f"Failed to generate metadata: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

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
        try:
            # Format timestamp as timecode for readability
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            timecode = f"{minutes:02d}:{seconds:02d}"

            # Create context by extracting relevant portion of transcript
            # Find text near the timestamp (approximate)
            context = self._extract_context_around_timestamp(transcript, timestamp)

            # Create prompt for thumbnail description
            prompt = (
                f"Based on this portion of the transcript around timestamp {timecode}, "
                f"describe what is likely happening visually in the video at this moment. "
                f"Focus on concrete visual elements that would make a compelling thumbnail. "
                f"Keep your description under 30 words and make it visually descriptive. "
                f"Do not include the timestamp in your description.\n\n"
                f"Transcript context: {context}"
            )

            response = self._model.generate_content(
                prompt,
                generation_config={"temperature": 0.7, "max_output_tokens": 100},
            )

            return response.text.strip()

        except Exception as e:
            error_msg = f"Failed to generate thumbnail description: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

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
        try:
            prompt = (
                f"Create detailed show notes for this video transcript. "
                f"Include key takeaways, any mentioned resources, and important points. "
                f"Format with Markdown headings (##) and bullet points. "
                f"Include a brief introduction, main sections with key points, "
                f"and a conclusion or summary section. "
                f"Maximum length: {max_length} characters."
            )

            response = self._model.generate_content(
                [prompt, transcript],
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": max(1024, max_length // 2),
                },
            )

            summary = response.text.strip()

            # Truncate if needed while preserving complete sentences
            if len(summary) > max_length:
                truncated = summary[:max_length]
                last_period = truncated.rfind(".")
                if (
                    last_period > max_length * 0.7
                ):  # Only truncate if we're not losing too much
                    summary = truncated[: last_period + 1]

            return summary

        except Exception as e:
            error_msg = f"Failed to generate content summary: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def set_model(self, model_name: str) -> None:
        """
        Set the AI model to use for generation.

        Args:
            model_name: Name of the model to use

        Raises:
            ValueError: If the model name is invalid
        """
        valid_models = [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-2.0-pro",
            "gemini-2.0-flash-001",
            "text-bison",
            "text-unicorn",
        ]

        if model_name not in valid_models:
            logging.warning(
                f"Model {model_name} not in known models: {valid_models}. Using anyway."
            )

        self._model_name = model_name

        # Reinitialize the model
        if model_name.startswith("gemini"):
            self._model = GenerativeModel(self._model_name)
        else:
            # For non-Gemini models, use a different initialization approach
            self._model = aiplatform.Model.get_model_from_name(model_name)

        logging.info(f"Switched to model: {self._model_name}")

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
        try:
            # Construct the prompt
            chapter_prompt = (
                "Analyze this transcript and divide it into logical chapters. "
            )

            if num_chapters:
                chapter_prompt += f"Create exactly {num_chapters} chapters. "

            chapter_prompt += (
                "For each chapter, provide a concise title and estimate the start and end times. "
                "Return the result ONLY as a valid JSON array of objects, "
                'where each object has the keys "title" (string), '
                '"start_time" (float, seconds from start), and '
                '"end_time" (float, seconds from start). '
                "Example JSON output format:\n"
                "[\n"
                '  {"title": "Introduction to the topic", "start_time": 0.0, "end_time": 120.5},\n'
                '  {"title": "First main point", "start_time": 120.5, "end_time": 300.0}\n'
                "]"
            )

            response = self._model.generate_content(
                [chapter_prompt, transcript],
                generation_config={
                    "temperature": 0.6,
                    "response_mime_type": "application/json",
                },
            )

            # Parse and validate the JSON response
            try:
                chapter_list = json.loads(response.text)

                # Basic validation
                if not isinstance(chapter_list, list):
                    raise ValueError("Response is not a list")

                for chapter in chapter_list:
                    if not isinstance(chapter, dict):
                        raise ValueError("Chapter is not a dictionary")
                    if not all(
                        key in chapter for key in ["title", "start_time", "end_time"]
                    ):
                        raise ValueError("Chapter missing required keys")

                return chapter_list

            except json.JSONDecodeError as e:
                logging.error(
                    f"Failed to parse chapters JSON: {e}. Raw response: {response.text}"
                )
                raise ValueError(f"Invalid JSON response: {e}")

        except Exception as e:
            error_msg = f"Failed to generate chapters: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def _extract_context_around_timestamp(
        self, transcript: str, timestamp: float, context_window: int = 200
    ) -> str:
        """
        Extract a portion of the transcript around the specified timestamp.

        This is a simple heuristic that assumes the transcript is roughly chronological.
        A more accurate implementation would require a timestamped transcript.

        Args:
            transcript: The full transcript text
            timestamp: The timestamp in seconds
            context_window: Number of characters to include before and after

        Returns:
            A portion of the transcript around the timestamp
        """
        # Estimate position in transcript based on timestamp
        # This is a rough heuristic assuming average speaking rate
        total_duration = len(transcript) / 10  # Rough estimate: 10 chars per second

        if total_duration == 0:
            return transcript

        position_ratio = timestamp / total_duration
        estimated_position = int(len(transcript) * position_ratio)

        # Get a window around the estimated position
        start = max(0, estimated_position - context_window)
        end = min(len(transcript), estimated_position + context_window)

        # Try to start at the beginning of a sentence
        while start > 0 and transcript[start] != ".":
            start -= 1
        if start > 0:
            start += 1  # Skip the period

        # Try to end at the end of a sentence
        while end < len(transcript) - 1 and transcript[end] != ".":
            end += 1
        if end < len(transcript) - 1:
            end += 1  # Include the period

        return transcript[start:end].strip()
