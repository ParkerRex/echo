"""
SubtitleUtils: Utility functions for generating VTT and SRT subtitle files.

- Provides methods to generate VTT and SRT content from transcript segments.
- Designed for use in the infrastructure/lib layer.

Directory: apps/core/lib/utils/subtitle_utils.py
Layer: Infrastructure/Lib
"""

from typing import Dict, List


class SubtitleUtils:
    """
    Utility class for generating VTT and SRT subtitle content.
    """

    @staticmethod
    def generate_vtt(transcript_segments: List[Dict]) -> str:
        """
        Generates VTT subtitle content from transcript segments.

        Args:
            transcript_segments (List[Dict]): List of segments, each with 'text', 'start_time', 'end_time'.

        Returns:
            str: VTT formatted subtitle content.
        """

        def format_timestamp(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = seconds % 60
            ms = int((s - int(s)) * 1000)
            return f"{h:02}:{m:02}:{int(s):02}.{ms:03}"

        lines = ["WEBVTT\n"]
        for seg in transcript_segments:
            start = format_timestamp(seg["start_time"])
            end = format_timestamp(seg["end_time"])
            lines.append(f"{start} --> {end}")
            lines.append(seg["text"])
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def generate_srt(transcript_segments: List[Dict]) -> str:
        """
        Generates SRT subtitle content from transcript segments.

        Args:
            transcript_segments (List[Dict]): List of segments, each with 'text', 'start_time', 'end_time'.

        Returns:
            str: SRT formatted subtitle content.
        """

        def format_timestamp(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        lines = []
        for idx, seg in enumerate(transcript_segments, 1):
            start = format_timestamp(seg["start_time"])
            end = format_timestamp(seg["end_time"])
            lines.append(f"{idx}")
            lines.append(f"{start} --> {end}")
            lines.append(seg["text"])
            lines.append("")
        return "\n".join(lines)
