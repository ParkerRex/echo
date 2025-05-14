"""
Subtitle service for generating subtitles in various formats.

This module provides services for generating subtitles in WebVTT, SRT, and other
formats from a transcript using AI services.
"""

import logging
import os
from typing import Optional

from video_processor.application.interfaces.ai import AIServiceInterface
from video_processor.application.interfaces.storage import StorageInterface
from video_processor.domain.exceptions import MetadataGenerationError


class SubtitleService:
    """
    Service for generating subtitles from transcripts.

    This service handles the generation of subtitles in various formats
    using AI services or direct conversion from transcripts.
    """

    def __init__(
        self,
        ai_adapter: AIServiceInterface,
        storage_adapter: StorageInterface,
        output_dir: str = "subtitles",
    ):
        """
        Initialize the SubtitleService with required dependencies.

        Args:
            ai_adapter: AI adapter for content generation
            storage_adapter: Storage adapter for file operations
            output_dir: Directory for generated subtitle files
        """
        self._ai = ai_adapter
        self._storage = storage_adapter
        self._output_dir = output_dir

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        logging.info(f"Initialized SubtitleService with output_dir={output_dir}")

    def generate_vtt(self, audio_path: str, transcript: Optional[str] = None) -> str:
        """
        Generate WebVTT subtitles from an audio file or transcript.

        Args:
            audio_path: Path to the audio file
            transcript: Optional transcript text (if already generated)

        Returns:
            Path to the generated VTT file

        Raises:
            MetadataGenerationError: If subtitle generation fails
        """
        try:
            logging.info(f"Generating WebVTT subtitles from {audio_path}")

            # If transcript isn't provided, rely on AI to generate directly from audio
            if not transcript:
                # Use AI to generate VTT directly from audio
                logging.info("Generating VTT directly from audio file")

                # Create audio part (this is done inside the AI adapter)
                vtt_content = self._ai_generate_vtt(audio_path)
            else:
                # Convert transcript to VTT format
                logging.info("Converting transcript to VTT format")
                vtt_content = self._transcript_to_vtt(transcript)

            # Ensure content starts with WEBVTT
            if not vtt_content.strip().startswith("WEBVTT"):
                vtt_content = f"WEBVTT\n\n{vtt_content}"

            # Save to file
            base_name = os.path.basename(audio_path)
            file_name = os.path.splitext(base_name)[0] + ".vtt"
            output_path = os.path.join(self._output_dir, file_name)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(vtt_content)

            logging.info(f"Successfully saved WebVTT subtitles to {output_path}")
            return output_path

        except Exception as e:
            error_msg = f"Failed to generate WebVTT subtitles: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def generate_srt(self, audio_path: str, transcript: Optional[str] = None) -> str:
        """
        Generate SRT subtitles from an audio file or transcript.

        Args:
            audio_path: Path to the audio file
            transcript: Optional transcript text (if already generated)

        Returns:
            Path to the generated SRT file

        Raises:
            MetadataGenerationError: If subtitle generation fails
        """
        try:
            logging.info(f"Generating SRT subtitles from {audio_path}")

            # Get VTT content first (either from transcript or directly)
            vtt_path = self.generate_vtt(audio_path, transcript)

            # Read VTT content
            with open(vtt_path, "r", encoding="utf-8") as f:
                vtt_content = f.read()

            # Convert VTT to SRT
            srt_content = self._vtt_to_srt(vtt_content)

            # Save to file
            base_name = os.path.basename(audio_path)
            file_name = os.path.splitext(base_name)[0] + ".srt"
            output_path = os.path.join(self._output_dir, file_name)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

            logging.info(f"Successfully saved SRT subtitles to {output_path}")
            return output_path

        except Exception as e:
            error_msg = f"Failed to generate SRT subtitles: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def _ai_generate_vtt(self, audio_path: str) -> str:
        """
        Use AI to generate VTT subtitles directly from audio.

        Args:
            audio_path: Path to the audio file

        Returns:
            VTT subtitle content as string

        Raises:
            MetadataGenerationError: If subtitle generation fails
        """
        try:
            # Create a prompt for the AI to generate VTT format
            # This might be implementation-specific based on the AI adapter
            prompt = (
                "Generate subtitles in WebVTT format for the following audio. "
                "Ensure accurate timing.\n"
                "Example format:\n"
                "WEBVTT\n\n"
                "00:00:00.000 --> 00:00:05.000\n"
                "Hello everyone and welcome back.\n\n"
                "00:00:05.500 --> 00:00:10.000\n"
                "Today we are discussing..."
            )

            # We're getting this directly from the AI adapter, with custom prompting
            # The actual implementation might vary based on the AI service
            # This is a simplification - the actual AI adapter would handle
            # the audio file and prompt differently

            # Use audio part and a special method, or fall back to transcript + processing
            # The method name is fictional and depends on the AI adapter implementation
            vtt_content = self._generate_vtt_from_audio(audio_path, prompt)

            return vtt_content

        except Exception as e:
            error_msg = f"Failed to generate VTT using AI: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def _generate_vtt_from_audio(self, audio_path: str, prompt: str) -> str:
        """
        Wrapper around AI adapter call to generate VTT from audio.

        This method exists primarily to simplify testing and mocking.

        Args:
            audio_path: Path to the audio file
            prompt: Prompt for the AI

        Returns:
            VTT subtitle content as string
        """
        # This is a placeholder for the actual AI-specific implementation
        # In a real implementation, this might use different AI adapter methods
        # or might process the audio differently based on the AI service

        # This is a simplification - in reality, this would be a more complex
        # interaction with the AI adapter based on its capabilities
        vtt_result = self._ai.generate_transcript(audio_path)

        # Simple conversion - in reality, we'd need more processing to add timestamps
        return self._transcript_to_vtt(vtt_result)

    def _transcript_to_vtt(self, transcript: str) -> str:
        """
        Convert a plain transcript to VTT format with estimated timestamps.

        Args:
            transcript: Plain text transcript

        Returns:
            VTT subtitle content as string
        """
        # Very simple conversion for demonstration
        # In a real implementation, we'd use natural breaks in the text,
        # sentence boundaries, etc., and estimate durations based on word count

        lines = []
        lines.append("WEBVTT\n")

        # Split by sentences or paragraphs
        paragraphs = [p.strip() for p in transcript.split(".") if p.strip()]

        # Estimate 5 seconds per sentence
        current_time = 0
        for i, paragraph in enumerate(paragraphs):
            # Estimate duration based on word count (rough approximation)
            words = paragraph.split()
            duration = max(
                2, len(words) * 0.5
            )  # 0.5 seconds per word, minimum 2 seconds

            start_time = self._format_timestamp(current_time)
            end_time = self._format_timestamp(current_time + duration)
            current_time += duration

            lines.append(f"\n{start_time} --> {end_time}")
            lines.append(f"{paragraph}.")

        return "\n".join(lines)

    def _vtt_to_srt(self, vtt_content: str) -> str:
        """
        Convert WebVTT content to SRT format.

        Args:
            vtt_content: WebVTT content as string

        Returns:
            SRT subtitle content as string
        """
        try:
            # Parse VTT content
            vtt_lines = vtt_content.strip().split("\n")

            # Skip WebVTT header
            start_index = 0
            while start_index < len(vtt_lines) and not self._is_timestamp_line(
                vtt_lines[start_index]
            ):
                start_index += 1

            srt_lines = []
            subtitle_index = 1
            i = start_index

            while i < len(vtt_lines):
                # Find timestamp line
                if self._is_timestamp_line(vtt_lines[i]):
                    # Add subtitle index
                    srt_lines.append(str(subtitle_index))
                    subtitle_index += 1

                    # Convert timestamp format from VTT to SRT
                    timestamp_line = vtt_lines[i].replace(".", ",")
                    srt_lines.append(timestamp_line)

                    # Add subtitle text
                    text_lines = []
                    i += 1
                    while (
                        i < len(vtt_lines)
                        and not self._is_timestamp_line(vtt_lines[i])
                        and vtt_lines[i].strip()
                    ):
                        text_lines.append(vtt_lines[i])
                        i += 1

                    srt_lines.append("\n".join(text_lines))
                    srt_lines.append("")  # Empty line between subtitles
                else:
                    i += 1

            return "\n".join(srt_lines)

        except Exception as e:
            error_msg = f"Failed to convert VTT to SRT: {str(e)}"
            logging.error(error_msg)
            raise MetadataGenerationError(error_msg) from e

    def _is_timestamp_line(self, line: str) -> bool:
        """
        Check if a line contains a VTT timestamp.

        Args:
            line: Line of text to check

        Returns:
            True if the line contains a timestamp, False otherwise
        """
        return "-->" in line and ":" in line

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format a timestamp in VTT format (HH:MM:SS.mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
