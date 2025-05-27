"""
Gemini AI service adapter implementation.

This module implements the AIAdapterInterface for Google's Gemini AI models.
"""

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

# Import Google's Generative AI library with error handling
try:
    import google.generativeai as genai
    from google.generativeai.types import content_types

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from apps.core.core.config import settings
from apps.core.lib.ai.base_adapter import AIAdapterInterface


class GeminiAdapter(AIAdapterInterface):
    """
    Adapter for Google's Gemini AI models.
    """

    def __init__(self, settings_instance=None):
        """
        Initialize the Gemini adapter with API key from settings.

        Args:
            settings_instance: Optional settings instance. If not provided, uses the global settings.
        """
        self.settings = settings_instance or settings

        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Generative AI library is not installed. "
                "Please install with: pip install google-generativeai"
            )

        if not self.settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY must be set in settings to use GeminiAdapter"
            )

        # Configure the Gemini API
        genai.configure(api_key=self.settings.GEMINI_API_KEY)

        # Set up the default model
        self.text_model = genai.GenerativeModel("gemini-pro")
        self.vision_model = genai.GenerativeModel("gemini-pro-vision")

    async def generate_text(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate text based on a prompt and optional context using Gemini.

        Args:
            prompt: The text prompt to generate content from
            context: Optional context to provide additional information to the AI

        Returns:
            The generated text as a string

        Raises:
            AINoResponseError: If Gemini fails to generate a response
        """
        try:
            # Combine prompt and context if context is provided
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            # Run in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool, lambda: self.text_model.generate_content(full_prompt)
                )

            # Check response validity
            if not response or not hasattr(response, "text"):
                raise AINoResponseError("Gemini failed to generate a response")

            return cast(str, response.text)

        except Exception as e:
            # Re-raise as AINoResponseError for consistent error handling
            raise AINoResponseError(
                f"Error generating text with Gemini: {str(e)}"
            ) from e

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe speech from an audio file to text.

        Note: As of current implementation, Gemini does not directly support audio transcription.
        This method relies on a custom implementation or may use other Google services.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text as a string

        Raises:
            AINoResponseError: If transcription fails
            FileNotFoundError: If the audio file does not exist
        """
        # Check if file exists
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Note: This is a placeholder implementation.
        # In a real implementation, this would typically use:
        # 1. Google Speech-to-Text API
        # 2. Google Cloud Speech API
        # 3. A separate transcription service

        try:
            # Placeholder for actual transcription implementation
            # In a real implementation, would call the appropriate API
            raise NotImplementedError(
                "Direct audio transcription is not supported by Gemini. "
                "Consider using Google Speech-to-Text API instead."
            )

        except Exception as e:
            raise AINoResponseError(f"Error transcribing audio: {str(e)}") from e

    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze content to extract meaningful information using Gemini.

        Args:
            content: The text content to analyze

        Returns:
            A dictionary containing analysis results

        Raises:
            AINoResponseError: If Gemini fails to analyze the content
        """
        try:
            # Create a structured prompt for content analysis
            analysis_prompt = """
            Analyze the following content and extract meaningful information.
            Return your analysis as a valid JSON object with the following structure:
            {
                "title": "A concise, attention-grabbing title",
                "description": "A clear description summarizing the main points (150-200 words)",
                "tags": ["relevant", "tags", "for", "categorization"],
                "key_points": ["Main point 1", "Main point 2", "Main point 3"],
                "sentiment": "positive/negative/neutral"
            }

            Only provide the JSON object without any additional text or explanation.

            Content to analyze:

            """

            full_prompt = f"{analysis_prompt}\n{content}"

            # Run in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool, lambda: self.text_model.generate_content(full_prompt)
                )

            # Parse the JSON response
            result = cast(Dict[str, Any], json.loads(response.text))

            # Validate essential fields
            required_fields = ["title", "description", "tags", "key_points"]
            for field in required_fields:
                if field not in result:
                    result[field] = None

            return result

        except json.JSONDecodeError as e:
            raise AINoResponseError(f"Gemini returned malformed JSON: {str(e)}") from e
        except Exception as e:
            raise AINoResponseError(
                f"Error analyzing content with Gemini: {str(e)}"
            ) from e

    async def segment_transcript(
        self, transcript: str
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Segment a transcript into meaningful chunks with timestamps.

        Args:
            transcript: The transcript text to segment

        Returns:
            A list of segment dictionaries

        Raises:
            AINoResponseError: If Gemini fails to segment the transcript
        """
        try:
            # Create a structured prompt for transcript segmentation
            segmentation_prompt = """
            Segment the following transcript into meaningful chunks with estimated timestamps.
            Return your segmentation as a valid JSON array with the following structure:
            [
                {
                    "text": "Segment text",
                    "start_time": 0.0,
                    "end_time": 10.5
                },
                {
                    "text": "Next segment text",
                    "start_time": 10.5,
                    "end_time": 20.0
                }
            ]

            Only provide the JSON array without any additional text or explanation.
            Assume the transcript starts at 0.0 seconds.
            Estimate reasonable timestamps based on the length of text.

            Transcript to segment:

            """

            full_prompt = f"{segmentation_prompt}\n{transcript}"

            # Run in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool, lambda: self.text_model.generate_content(full_prompt)
                )

            # Parse the JSON response
            segments = cast(List[Dict[str, Union[str, float]]], json.loads(response.text))

            # Validate segment structure
            for segment in segments:
                if not all(
                    key in segment for key in ["text", "start_time", "end_time"]
                ):
                    raise ValueError("Segment is missing required fields")

            return segments

        except json.JSONDecodeError as e:
            raise AINoResponseError(f"Gemini returned malformed JSON: {str(e)}") from e
        except Exception as e:
            raise AINoResponseError(
                f"Error segmenting transcript with Gemini: {str(e)}"
            ) from e

    async def summarize_text(self, text: str, max_length: Optional[int] = None) -> str:
        """
        Generate a concise summary of the provided text using Gemini.

        Args:
            text: The text to summarize
            max_length: Optional maximum length of the summary in characters

        Returns:
            The summarized text as a string

        Raises:
            AINoResponseError: If Gemini fails to summarize the text
        """
        try:
            # Create a structured prompt for summarization
            summary_prompt = "Summarize the following text in a concise manner"

            if max_length:
                summary_prompt += f" in {max_length} characters or less"

            full_prompt = f"{summary_prompt}:\n\n{text}"

            # Run in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                response = await loop.run_in_executor(
                    pool, lambda: self.text_model.generate_content(full_prompt)
                )

            # Check response validity
            if not response or not hasattr(response, "text"):
                raise AINoResponseError("Gemini failed to generate a summary")

            summary = cast(str, response.text)

            # Trim if necessary
            if max_length and len(summary) > max_length:
                summary = summary[:max_length]

            return summary

        except Exception as e:
            raise AINoResponseError(
                f"Error summarizing text with Gemini: {str(e)}"
            ) from e


# Custom exception for AI services
class AINoResponseError(Exception):
    """Exception raised when an AI service fails to generate a response."""

    pass
