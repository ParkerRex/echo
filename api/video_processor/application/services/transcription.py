"""
Transcription service for generating transcripts from audio and video files.

This module provides services for extracting audio from videos and generating
transcripts using AI services.
"""

import logging
import os
import subprocess
from typing import Optional

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.exceptions import TranscriptionError


class TranscriptionService:
    """
    Service for audio extraction and transcript generation.

    This service handles audio extraction from video files and transcript
    generation using AI services.
    """

    def __init__(
        self,
        ai_adapter: AIServiceInterface,
        storage_adapter: StorageInterface,
        temp_dir: str = "/tmp",
    ):
        """
        Initialize the TranscriptionService with required dependencies.

        Args:
            ai_adapter: AI adapter for transcript generation
            storage_adapter: Storage adapter for file operations
            temp_dir: Directory for temporary files
        """
        self._ai = ai_adapter
        self._storage = storage_adapter
        self._temp_dir = temp_dir

        # Ensure temp directory exists
        os.makedirs(temp_dir, exist_ok=True)

        logging.info(f"Initialized TranscriptionService with temp_dir={temp_dir}")

    def extract_audio(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> str:
        """
        Extract audio from a video file using FFmpeg.

        Args:
            video_path: Path to the video file
            output_path: Path where the extracted audio should be saved (optional)
            sample_rate: Audio sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1)

        Returns:
            Path to the extracted audio file

        Raises:
            TranscriptionError: If audio extraction fails
        """
        try:
            # Generate output path if not provided
            if not output_path:
                video_filename = os.path.basename(video_path)
                audio_filename = os.path.splitext(video_filename)[0] + ".wav"
                output_path = os.path.join(self._temp_dir, audio_filename)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            logging.info(f"Extracting audio from {video_path} to {output_path}")

            # Build FFmpeg command for audio extraction
            command = [
                "ffmpeg",
                "-i",
                video_path,  # Input file
                "-vn",  # No video
                "-ar",
                str(sample_rate),  # Sample rate
                "-ac",
                str(channels),  # Number of channels
                "-acodec",
                "pcm_s16le",  # Audio codec
                "-y",  # Overwrite output file if exists
                output_path,  # Output file
            ]

            # Execute FFmpeg command
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception, handle errors manually
            )

            # Check for errors
            if result.returncode != 0:
                error_msg = (
                    f"FFmpeg failed with code {result.returncode}: {result.stderr}"
                )
                logging.error(error_msg)
                raise TranscriptionError(error_msg)

            # Check if output file exists
            if not os.path.exists(output_path):
                raise TranscriptionError(
                    f"FFmpeg did not create output file: {output_path}"
                )

            logging.info(f"Successfully extracted audio to {output_path}")
            return output_path

        except subprocess.SubprocessError as e:
            error_msg = f"FFmpeg subprocess error: {str(e)}"
            logging.error(error_msg)
            raise TranscriptionError(error_msg) from e

        except Exception as e:
            error_msg = f"Failed to extract audio: {str(e)}"
            logging.error(error_msg)
            raise TranscriptionError(error_msg) from e

    def generate_transcript(self, audio_path: str) -> str:
        """
        Generate a transcript from an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Generated transcript text

        Raises:
            TranscriptionError: If transcript generation fails
        """
        try:
            logging.info(f"Generating transcript from {audio_path}")

            # Delegate to AI adapter for transcript generation
            transcript = self._ai.generate_transcript(audio_path)

            if not transcript:
                raise TranscriptionError("Generated transcript is empty")

            logging.info(f"Successfully generated transcript ({len(transcript)} chars)")
            return transcript

        except Exception as e:
            error_msg = f"Failed to generate transcript: {str(e)}"
            logging.error(error_msg)
            raise TranscriptionError(error_msg) from e

    def process_video_to_transcript(self, video_path: str) -> str:
        """
        Process a video file to generate a transcript.

        This is a convenience method that combines audio extraction and
        transcript generation.

        Args:
            video_path: Path to the video file

        Returns:
            Generated transcript text

        Raises:
            TranscriptionError: If processing fails
        """
        try:
            # Extract audio from video
            audio_path = self.extract_audio(video_path)

            # Generate transcript from audio
            transcript = self.generate_transcript(audio_path)

            # Clean up temporary audio file
            try:
                os.remove(audio_path)
                logging.debug(f"Cleaned up temporary audio file: {audio_path}")
            except OSError:
                logging.warning(
                    f"Failed to clean up temporary audio file: {audio_path}"
                )

            return transcript

        except Exception as e:
            error_msg = f"Failed to process video to transcript: {str(e)}"
            logging.error(error_msg)
            raise TranscriptionError(error_msg) from e
