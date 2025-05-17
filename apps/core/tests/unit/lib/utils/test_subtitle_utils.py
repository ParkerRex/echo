"""
Unit tests for the SubtitleUtils class.
"""

import re
from typing import Dict, List

import pytest

from apps.core.lib.utils.subtitle_utils import SubtitleUtils


class TestSubtitleUtils:
    """Test cases for the SubtitleUtils class."""

    @pytest.fixture
    def sample_transcript_segments(self) -> List[Dict]:
        """
        Creates a sample transcript segments list for testing.
        """
        return [
            {"text": "This is the first segment.", "start_time": 0.0, "end_time": 5.5},
            {
                "text": "This is the second segment.",
                "start_time": 5.5,
                "end_time": 10.0,
            },
            {"text": "This spans over a minute.", "start_time": 59.0, "end_time": 65.0},
            {
                "text": "This spans over an hour.",
                "start_time": 3599.0,
                "end_time": 3605.0,
            },
        ]

    def test_generate_vtt_format(self, sample_transcript_segments):
        """Test VTT formatting with sample transcript segments."""
        vtt_content = SubtitleUtils.generate_vtt(sample_transcript_segments)

        # Verify basic structure
        assert vtt_content.startswith("WEBVTT")

        # Split lines and analyze
        lines = vtt_content.strip().split("\n")

        # Verify we have the right number of segments
        # Each segment has: timestamp line, text line, empty line
        # Plus the WEBVTT header and a final empty line
        expected_lines = 1 + (3 * len(sample_transcript_segments))
        assert len(lines) == expected_lines

        # Verify timestamp format (HH:MM:SS.mmm --> HH:MM:SS.mmm)
        timestamp_pattern = r"^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$"
        for i in range(1, len(lines), 3):
            assert re.match(timestamp_pattern, lines[i]), (
                f"Line {i} is not a valid VTT timestamp: {lines[i]}"
            )

        # Verify the text content for each segment
        for i, segment in enumerate(sample_transcript_segments):
            text_line_index = 2 + (i * 3)
            assert lines[text_line_index] == segment["text"]

    def test_generate_vtt_timestamps(self, sample_transcript_segments):
        """Test VTT timestamp formatting specifically."""
        vtt_content = SubtitleUtils.generate_vtt(sample_transcript_segments)
        lines = vtt_content.strip().split("\n")

        # First segment: 00:00:00.000 --> 00:00:05.500
        assert lines[1] == "00:00:00.000 --> 00:00:05.500"

        # Second segment: 00:00:05.500 --> 00:00:10.000
        assert lines[4] == "00:00:05.500 --> 00:00:10.000"

        # Minute spanning: 00:00:59.000 --> 00:01:05.000
        assert lines[7] == "00:00:59.000 --> 00:01:05.000"

        # Hour spanning: 00:59:59.000 --> 01:00:05.000
        assert lines[10] == "00:59:59.000 --> 01:00:05.000"

    def test_generate_srt_format(self, sample_transcript_segments):
        """Test SRT formatting with sample transcript segments."""
        srt_content = SubtitleUtils.generate_srt(sample_transcript_segments)

        # Split lines and analyze
        lines = srt_content.strip().split("\n")

        # Verify we have the right number of segments
        # Each segment has: index line, timestamp line, text line, empty line
        expected_lines = 4 * len(sample_transcript_segments)
        assert len(lines) == expected_lines

        # Verify sequence numbers
        for i in range(0, len(lines), 4):
            seq_num = i // 4 + 1
            assert lines[i] == str(seq_num)

        # Verify timestamp format (HH:MM:SS,mmm --> HH:MM:SS,mmm)
        timestamp_pattern = r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$"
        for i in range(1, len(lines), 4):
            assert re.match(timestamp_pattern, lines[i]), (
                f"Line {i} is not a valid SRT timestamp: {lines[i]}"
            )

        # Verify the text content for each segment
        for i, segment in enumerate(sample_transcript_segments):
            text_line_index = 2 + (i * 4)
            assert lines[text_line_index] == segment["text"]

    def test_generate_srt_timestamps(self, sample_transcript_segments):
        """Test SRT timestamp formatting specifically."""
        srt_content = SubtitleUtils.generate_srt(sample_transcript_segments)
        lines = srt_content.strip().split("\n")

        # First segment: 00:00:00,000 --> 00:00:05,500
        assert lines[1] == "00:00:00,000 --> 00:00:05,500"

        # Second segment: 00:00:05,500 --> 00:00:10,000
        assert lines[5] == "00:00:05,500 --> 00:00:10,000"

        # Minute spanning: 00:00:59,000 --> 00:01:05,000
        assert lines[9] == "00:00:59,000 --> 00:01:05,000"

        # Hour spanning: 00:59:59,000 --> 01:00:05,000
        assert lines[13] == "00:59:59,000 --> 01:00:05,000"

    def test_empty_transcript(self):
        """Test generating subtitles with an empty transcript."""
        empty_segments = []

        # VTT should just have the header
        vtt_content = SubtitleUtils.generate_vtt(empty_segments)
        assert vtt_content == "WEBVTT\n"

        # SRT should be empty
        srt_content = SubtitleUtils.generate_srt(empty_segments)
        assert srt_content == ""

    def test_malformed_segments(self):
        """Test handling of malformed segment data."""
        # Missing start_time
        malformed_segments = [
            {"text": "This segment is missing start_time.", "end_time": 5.0}
        ]

        # This should raise a KeyError
        with pytest.raises(KeyError):
            SubtitleUtils.generate_vtt(malformed_segments)

        with pytest.raises(KeyError):
            SubtitleUtils.generate_srt(malformed_segments)

        # Missing text
        malformed_segments = [{"start_time": 0.0, "end_time": 5.0}]

        # This should raise a KeyError
        with pytest.raises(KeyError):
            SubtitleUtils.generate_vtt(malformed_segments)

        with pytest.raises(KeyError):
            SubtitleUtils.generate_srt(malformed_segments)
