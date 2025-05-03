"""
Gemini AI adapter implementation.

This module provides a concrete implementation of the AIServiceInterface
for Google's Gemini AI models, handling transcript and metadata generation.
"""

import json
import logging
import time
from typing import Dict, List, Optional

from vertexai.generative_models import GenerativeModel, Part

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.domain.exceptions import (
    MetadataGenerationError,
    TranscriptionError,
)


class GeminiAIAdapter(AIServiceInterface):
    """
    Gemini AI implementation of AIServiceInterface.

    This adapter implements AI operations using Google's Gemini AI models.
    """

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-001"
    ):
        """
        Initialize the Gemini AI Adapter.

        Args:
            api_key: Optional API key for Gemini (usually handled by environment)
            model: Model name to use (default: gemini-2.0-flash-001)
        """
        self._api_key = api_key
        self._model_name = model
        self._model = GenerativeModel(self._model_name)
        logging.info(f"Initialized Gemini AI adapter with model: {self._model_name}")

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
                "Generate a transcription of the audio, only extract speech "
                "and ignore background audio."
            )

            # Implement retry logic with exponential backoff
            max_retries = 3
            backoff = 1  # Initial backoff in seconds

            for attempt in range(max_retries):
                try:
                    response = self._model.generate_content(
                        [prompt, audio_part],
                        generation_config={
                            "temperature": 0.2
                        },  # Lower temp for accuracy
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
            # Generate title and tags
            title_tags = self._generate_title_tags(transcript)

            # Generate show notes
            show_notes = self.summarize_content(transcript, max_length=2000)

            # Generate chapters
            chapters = self.generate_chapters(transcript)

            # Compose the complete metadata
            metadata = {
                "title": title_tags.get("Description", "Untitled Video"),
                "description": show_notes[:500],  # Shorter version for description
                "tags": title_tags.get("Keywords", "").split(","),
                "show_notes": show_notes,
                "chapters": chapters,
            }

            return metadata

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

            # Create prompt for thumbnail description
            prompt = (
                f"Based on the transcript, describe what is likely happening in the video "
                f"at timestamp {timecode}. This will be used to create a thumbnail image. "
                f"Keep it brief (30 words max) and focus on visually descriptive elements. "
                f"Do not include the timestamp in your description. "
                f"Transcript: {transcript[:2000]}..."  # Limit transcript length
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
                f"Include key takeaways, any mentioned resources, and highlight "
                f"important points. Format with Markdown headings and bullet points. "
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
        ]

        if model_name not in valid_models:
            logging.warning(
                f"Model {model_name} not in known models: {valid_models}. Using anyway."
            )

        self._model_name = model_name
        self._model = GenerativeModel(self._model_name)
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
                "Chapterize the video content by grouping the content into chapters "
                "and providing a summary for each chapter. "
            )

            if num_chapters:
                chapter_prompt += f"Create exactly {num_chapters} chapters. "

            chapter_prompt += (
                "Please only capture key events and highlights. "
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

    def _generate_title_tags(self, transcript: str) -> Dict[str, str]:
        """
        Generate title and tags as a dictionary from transcript.

        Args:
            transcript: Transcript text

        Returns:
            Dictionary with "Description" (title) and "Keywords" (comma-separated tags)

        Raises:
            MetadataGenerationError: If generation fails
        """
        try:
            prompt = (
                "Write a 40-character long intriguing title for this video "
                "and 10 comma-separated hashtags suitable for YouTube "
                "based on the transcript. Format the response strictly as a valid JSON object "
                "with two keys: 'Description' (containing the title, max 50 characters) "
                "and 'Keywords' (containing the comma-separated hashtags as a single string)."
            )

            response = self._model.generate_content(
                [prompt, transcript],
                generation_config={
                    "temperature": 0.8,
                    "response_mime_type": "application/json",
                },
            )

            # Parse the JSON response
            try:
                title_dict = json.loads(response.text)

                # Basic validation
                if not isinstance(title_dict, dict):
                    raise ValueError("Response is not a dictionary")

                if "Description" not in title_dict or "Keywords" not in title_dict:
                    raise ValueError("Response missing required keys")

                return title_dict

            except json.JSONDecodeError as e:
                logging.error(
                    f"Failed to parse title/tags JSON: {e}. Raw response: {response.text}"
                )
                # Fallback to default
                return {
                    "Description": "Untitled Video",
                    "Keywords": "video,content,media",
                }

        except Exception as e:
            error_msg = f"Failed to generate title and tags: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e
